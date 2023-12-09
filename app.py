from tkinter import *
from tkinter import ttk, filedialog, messagebox
from collections import deque
from functools import reduce
from heapq import merge
import operator
import pickle
import re

from plot_reactions import Plotter
from search_species import find_species


class App:
    def __init__(self):
        self.filename = "appstate.pickle"
        self.logged_reactions = set()
        self.history = []
        self.history_limit = 10
        self.favourite = []

        self.window = Tk()
        self.window.title("VULCAN reaction plotter")
        self.menubar = Menu(self.window, activebackground='dark grey', activeforeground='white')
        self.fileMenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="  File  ", menu=self.fileMenu, underline=2)
        self.fileMenu.add_command(label="New", underline=0, command=self.new_state)
        self.recentMenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="History", menu=self.recentMenu, underline=0)

        self.netLabel = Label(self.window, text="Chemical network", font=("Arial Bold", 12))
        self.netLabel.grid(column=0, row=0)
        self.netEntry = Entry(self.window, width=30, selectbackground='black', selectforeground='white')
        self.netEntry.grid(column=1, row=0, columnspan=3)
        self.netEntry.bind('<Control-KeyRelease-a>', self.callback)
        self.netEntry.focus()
        self.netButton = Button(self.window, text="Browse files", command=lambda: self.browse_files(self.netEntry))
        self.netButton.grid(column=4, row=0)

        self.speciesLabel = Label(self.window, text="Species", font=("Arial Bold", 12))
        self.speciesLabel.grid(column=0, row=1)
        self.speciesEntry = Entry(self.window, width=30, selectbackground='black', selectforeground='white')
        self.speciesEntry.grid(column=1, row=1, columnspan=3)
        self.speciesEntry.bind('<Control-KeyRelease-a>', self.callback)
        self.speciesEntry.bind('<Return>', self.search_species)
        self.enterButton = Button(self.window, text="    Search     ", command=self.search_species)
        self.enterButton.grid(column=4, row=1)

        self.sourceLabel = Label(self.window, text="Sources:", font=("Arial Bold", 11))
        self.sourceLabel.grid(column=0, row=2, columnspan=3)
        self.sinkLabel = Label(self.window, text="Sinks:", font=("Arial Bold", 11))
        self.sinkLabel.grid(column=3, row=2, columnspan=2)

        self.sourceList = Listbox(self.window, width=30, selectbackground="light green", selectmode="multiple",
                                  exportselection=False)
        self.sourceList.bind('<Return>', self.add_select)
        self.sourceList.bind('<BackSpace>', self.del_select)
        self.sourceList.grid(column=0, row=3, columnspan=3, rowspan=4)
        self.sinkList = Listbox(self.window, width=30, selectbackground="light green", selectmode="multiple",
                                exportselection=False)
        self.sinkList.bind('<Return>', self.add_select)
        self.sinkList.bind('<BackSpace>', self.del_select)
        self.sinkList.grid(column=3, row=3, columnspan=3, rowspan=4)

        self.addallButton = Button(self.window, text="Select all", command=self.select_all)
        self.addallButton.grid(column=0, row=7, columnspan=3)
        self.clearButton = Button(self.window, text="Clear all", command=self.clear_entry)
        self.clearButton.grid(column=3, row=7, columnspan=3)

        self.separator = ttk.Separator(self.window, orient='horizontal')
        self.separator.grid(column=0, row=8, ipadx=280, pady=10, columnspan=7)

        self.manualLabel = Label(self.window, text="Manual entry", font=("Arial Bold", 12))
        self.manualLabel.grid(column=0, row=9)
        self.reactionCombo = Entry(self.window, width=30, selectbackground='black', selectforeground='white')
        self.reactionCombo.grid(column=1, row=9, columnspan=3)
        self.reactionCombo.bind('<Return>', self.add_entry)
        self.copyButton = Button(self.window, text="      Copy      ", command=self.copy)
        self.copyButton.grid(column=4, row=9)

        self.separator = ttk.Separator(self.window, orient='horizontal')
        self.separator.grid(column=0, row=10, ipadx=280, pady=10, columnspan=7)

        self.numLabel = Label(self.window, height=2, text="Number of logged reactions is 0 (max. 10 for plotting)")
        self.numLabel.grid(column=0, row=11, columnspan=5)

        self.fileLabel = Label(self.window, text="Output file", font=("Arial Bold", 12))
        self.fileLabel.grid(column=0, row=12)
        self.fileEntry = Entry(self.window, width=30, selectbackground='black', selectforeground='white')
        self.fileEntry.grid(column=1, row=12, columnspan=3)
        self.fileEntry.bind('<Control-KeyRelease-a>', self.callback)
        self.fileButton = Button(self.window, text="Browse files", command=lambda: self.browse_files(self.fileEntry))
        self.fileButton.grid(column=4, row=12)

        self.nameLabel = Label(self.window, text="File name", font=("Arial Bold", 12))
        self.nameLabel.grid(column=0, row=13)
        self.nameEntry = Entry(self.window, width=30, selectbackground='black', selectforeground='white')
        self.nameEntry.grid(column=1, row=13, columnspan=3)
        self.nameEntry.bind('<Control-KeyRelease-a>', self.callback)
        self.nameEntry.bind('<Return>', self.plot_graph)
        self.plotButton = Button(self.window, text="      Plot      ", command=self.plot_graph)
        self.plotButton.grid(column=4, row=13)

    def call(self):
        self.window.geometry('555x445')
        self.window.resizable(False, False)
        self.window.config(menu=self.menubar)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()

    def colour_entry(self, option=1):
        if option == 1:
            for ind in self.sourceList.curselection():
                self.sourceList.itemconfig(ind, {"background": "dark grey"})
            for ind in self.sinkList.curselection():
                self.sinkList.itemconfig(ind, {"background": "dark grey"})
        elif option == 2:
            for ind in self.sourceList.curselection():
                self.sourceList.itemconfig(ind, {"background": ""})
            for ind in self.sinkList.curselection():
                self.sinkList.itemconfig(ind, {"background": ""})
        elif option == 3:
            for ind in range(self.sourceList.size()):
                self.sourceList.itemconfig(ind, {"background": ""})
                self.sinkList.itemconfig(ind, {"background": ""})

    def colour_update(self, record):
        for ind in range(self.sourceList.size()):
            if self.sourceList.get(ind) in record:
                self.sourceList.itemconfig(ind, {"background": "dark grey"})
            if self.sinkList.get(ind) in record:
                self.sinkList.itemconfig(ind, {"background": "dark grey"})

    def colour_update_with_lookup(self, reaction_nums):
        combo = []
        for ind in range(self.sourceList.size()):
            source = self.sourceList.get(ind)
            sink = self.sinkList.get(ind)
            if source.split(maxsplit=1)[0] in reaction_nums:
                self.sourceList.itemconfig(ind, {"background": "dark grey"})
                combo.append(source)
            if sink.split(maxsplit=1)[0] in reaction_nums:
                self.sinkList.itemconfig(ind, {"background": "dark grey"})
                combo.append(sink)
        return combo

    def search_species(self, event=None):
        network_path = self.netEntry.get()
        species = self.speciesEntry.get().upper().strip()
        self.speciesEntry.delete("0", END)
        self.speciesEntry.insert(0, species)

        source, sink = find_species(network_path, species)
        self.sourceList.delete(0, END)
        self.sinkList.delete(0, END)
        for i in source:
            self.sourceList.insert(END, i)
        for j in sink:
            self.sinkList.insert(END, j)

    def select_all(self):
        self.sourceList.select_set(0, END)
        self.sinkList.select_set(0, END)

    def add_select(self, event=None):
        source = [self.sourceList.get(i) for i in self.sourceList.curselection()]
        sink = [self.sinkList.get(i) for i in self.sinkList.curselection()]
        self.logged_reactions = self.logged_reactions.union(set(source).union(set(sink)))

        self.colour_entry()
        self.sourceList.selection_clear(0, END)
        self.sinkList.selection_clear(0, END)
        self.numLabel.config(text=f"Number of logged reactions is {len(self.logged_reactions)} (max. 10 for plotting)")

    def del_select(self, event=None):
        source = [self.sourceList.get(i) for i in self.sourceList.curselection()]
        sink = [self.sinkList.get(i) for i in self.sinkList.curselection()]
        self.logged_reactions = self.logged_reactions.difference(set(source)).difference(set(sink))

        self.colour_entry(2)
        self.sourceList.selection_clear(0, END)
        self.sinkList.selection_clear(0, END)
        self.numLabel.config(text=f"Number of logged reactions is {len(self.logged_reactions)} (max. 10 for plotting)")

    def add_entry(self, event=None):
        combo = self.reactionCombo.get().replace(' ', '').split(',')
        self.reactionCombo.delete(0, END)
        self.logged_reactions = self.logged_reactions.union(set(self.colour_update_with_lookup(combo)))

    def clear_entry(self, event=None):
        self.logged_reactions = set()
        self.colour_entry(3)
        # reactionCombo.delete("0", END)
        self.numLabel.config(text=f"Number of logged reactions is 0 (max. 10 for plotting)")

    def browse_files(self, widget):
        if widget == self.netEntry:
            filename = filedialog.askopenfilename(filetypes=(("txt files", "*.txt"), ("All files", "*.*")),
                                                  initialdir="../thermo")
        elif widget == self.fileEntry:
            filename = filedialog.askopenfilename(filetypes=(("vul files", "*.vul"), ("All files", "*.*")),
                                                  initialdir="../output")
        filename = re.sub(r".*?VULCAN", "..", filename)
        widget.delete(0, END)
        widget.insert(0, filename)

    def plot_graph(self, event=None):
        graph_name = self.nameEntry.get()
        data_path = self.fileEntry.get()
        species = self.speciesEntry.get()

        reactions = sorted(list(self.logged_reactions))
        labels = [i.split(maxsplit=1)[0] for i in reactions]

        try:
            ind = self.recentMenu.index(reactions)
            self.recentMenu.delete(ind)
            self.recentMenu.insert_command(0, label=', '.join(labels), command=lambda: self.overwrite(reactions))
        except TclError:
            self.history.append(reactions)
            self.recentMenu.insert_command(0, label=', '.join(labels), command=lambda: self.overwrite(reactions))

        if len(self.history) > self.history_limit:
            self.history.pop()
            self.recentMenu.delete(END)

        plot_reactions = Plotter([data_path, graph_name, species, reactions])
        plot_reactions.plotting()

    def overwrite(self, reactions):
        answer = messagebox.askokcancel("Warning", "This selection will overwrite the current reaction list")
        if answer:
            self.clear_entry()
            self.colour_update(reactions)
            self.logged_reactions = set(reactions)
            self.numLabel.config(text=f"Number of logged reactions is {len(self.logged_reactions)} (max. 10 for plotting)")

    def copy(self):
        self.window.clipboard_clear()
        self.window.clipboard_append(self.logged_reactions)

    def callback(self, event):
        event.widget.select_range(0, END)

    def new_state(self):
        self.netEntry.delete(0, END)
        self.speciesEntry.delete(0, END)
        self.sourceList.delete(0, END)
        self.sinkList.delete(0, END)
        self.clear_entry()
        self.fileEntry.delete(0, END)
        self.nameEntry.delete(0, END)

    def on_closing(self):
        self.window.quit()
        self.window.destroy()


app = App()
app.call()

