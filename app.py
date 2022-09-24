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

FILENAME = "appstate.pickle"
window = Tk()
window.title("VULCAN reaction plotter")
rev_var = IntVar()
option_var = IntVar()
history, favourite = [], []
 
        
def colour_entry():
    logged_reactions = [int(i) for i in reactionCombo['values']]
    source = [int(re.findall("^\d+", sourceList.get(i))[0]) for i in range(sourceList.size())]
    sink = [int(re.findall("^\d+", sinkList.get(i))[0]) for i in range(sinkList.size())]
    
    logged_source = list(set(logged_reactions) & set(source))
    for ind, i in enumerate(source):
        if all(x in logged_reactions for x in [i, i + 1]): 
            sourceList.itemconfig(ind, {"background": "dark grey"})
        elif any(x in logged_reactions for x in [i, i + 1]): 
            sourceList.itemconfig(ind, {"background": "light grey"})
        else: 
            sourceList.itemconfig(ind, {"background": ""})
        
    logged_sink = list(set(logged_reactions) & set(sink))
    for ind, i in enumerate(sink):
        if all(x in logged_reactions for x in [i, i + 1]): 
            sinkList.itemconfig(ind, {"background": "dark grey"})
        elif any(x in logged_reactions for x in [i, i + 1]): 
            sinkList.itemconfig(ind, {"background": "light grey"})
        else: 
            sinkList.itemconfig(ind, {"background": ""})          

def search_species(event=None):    
    data_path = netEntry.get()
    species = speciesEntry.get().upper()
    speciesEntry.delete("0", END)
    speciesEntry.insert(0, species) 
    
    source, sink = find_species(data_path, species)   
    sourceList.delete(0, END)
    sinkList.delete(0, END)
    for i in source:
        sourceList.insert(END, i)
    for j in sink:
        sinkList.insert(END, j)
    colour_entry()
    
def select_all():
    sourceList.select_set(0, END)
    sinkList.select_set(0, END)
    
def add_select():    
    source_indices = sourceList.curselection()
    sink_indices = sinkList.curselection()
    source = [int(re.findall("^\d+", sourceList.get(i))[0]) for i in source_indices]
    sink = [int(re.findall("^\d+", sinkList.get(i))[0]) for i in sink_indices]    
    reverse = rev_var.get()
    
    if reverse:
        try: source = reduce(operator.add, zip(source, [i + 1 for i in source]))
        except TypeError: pass
        try: sink = reduce(operator.add, zip(sink, [i + 1 for i in sink]))
        except TypeError: pass
        
    original = [int(i) for i in reactionCombo['values']]
    new_reactions = [i for i in list(merge(source, sink)) if i not in original]            
    reactionCombo['values'] = list(merge(new_reactions, original))
    
    colour_entry()     
    sourceList.selection_clear(0, END)
    sinkList.selection_clear(0, END)    
    numLabel.config(text = f"Number of logged reactions is {len(reactionCombo['values'])} (max. 10 for plotting)")
    
def add_entry(event=None):
    new_reaction = reactionCombo.get()
    if new_reaction:
        original = list(reactionCombo['values'])
        new = [i for i in new_reaction.split(',') if i not in original]
        combined = sorted(original + new, key=lambda x: (len (x), x))
        reactionCombo['values'] = combined
        
        colour_entry()                     
        reactionCombo.delete("0", END)
        numLabel.config(text = f"Number of logged reactions is {len(reactionCombo['values'])} (max. 10 for plotting)")
    else: pass
    
def del_entry(event=0):
    reaction = reactionCombo.get()
    new_list = [r for r in reactionCombo['values'] if r!= reaction]
    reactionCombo['values'] = new_list
    
    colour_entry() 
    reactionCombo.delete("0", END)
    numLabel.config(text = f"Number of logged reactions is {len(reactionCombo['values'])} (max. 10 for plotting)")
    
def clear_entry():
    reactionCombo['values'] = []
    colour_entry() 
    reactionCombo.delete("0", END)
    numLabel.config(text = f"Number of logged reactions is 0 (max. 10 for plotting)")

def overwrite(reactions):
    answer = messagebox.askokcancel("Warning", "This selection will overwrite the current reaction list")
    if answer:
        clear_entry()
        reactionCombo['values'] = reactions.split(',')
        reactionCombo.delete("0", END)
        colour_entry() 
        numLabel.config(text = f"Number of logged reactions is {len(reactionCombo['values'])} (max. 10 for plotting)")
    
def plot_graph(event=None):
    graph_name = nameEntry.get()
    data_path = fileEntry.get()
    species = speciesEntry.get()
    
    reactions = ','.join(reactionCombo['values'])
    try: 
        ind = recentMenu.index(reactions)
        recentMenu.delete(ind)        
        recentMenu.insert_command(0, label=reactions, command=lambda: overwrite(reactions))
                            
    except TclError:
        history.append(reactions)        
        recentMenu.insert_command(0, label=reactions, command=lambda: overwrite(reactions))
        
    if len(history) > 5:
        history.pop()    
        recentMenu.delete(END)

    option = option_var.get()    
    plot_reactions = Plotter([0, data_path, graph_name, species, reactions])
    if option == 2: plot_reactions.photolysis()
    else: plot_reactions.plotting(option)

    
def browse_files(widget):
    if widget == netEntry: filename = filedialog.askopenfilename(filetypes=(("txt files","*.txt"), ("All files","*.*")), initialdir="../thermo")
    elif widget == fileEntry: filename = filedialog.askopenfilename(filetypes=(("vul files","*.vul"), ("All files","*.*")), initialdir="../output")
    filename = re.sub(r".*?VULCAN", "..", filename)
    widget.delete(0, END)
    widget.insert(0, filename)
    
def copy(reactions):
    window.clipboard_clear()
    window.clipboard_append(reactions)

def save_state():
    data = {"network_path": netEntry.get(),
            "species": speciesEntry.get(),
            "combo_reactions": list(reactionCombo["values"]),
            "clipboard": favourite,
            "data_path": fileEntry.get()}
    with open(FILENAME, "wb") as file:
        pickle.dump(data, file)
        
def load_state():
    try:
        with open(FILENAME, "rb") as file:
            data = pickle.load(file)
        netEntry.insert(0, data["network_path"])
        speciesEntry.insert(0, data["species"])
        reactionCombo["values"] = data["combo_reactions"]
        favourite.extend(data["clipboard"])
        fileEntry.insert(0, data["data_path"])
        numLabel.config(text = f"Number of logged reactions is {len(reactionCombo['values'])} (max. 10 for plotting)")     
        search_species()        
        colour_entry()        
        
        if favourite:
            favourMenu.add_command(label="Edit", background="light grey", activebackground="light grey", command=edit_clipboard)   
            for i in favourite:
                favourMenu.insert_command(0, label=i, command=lambda: copy(reactions))
                
    except FileNotFoundError:
        pass
        
def new_state():
    netEntry.delete(0, END)
    speciesEntry.delete(0, END)
    sourceList.delete(0, END)
    sinkList.delete(0, END)
    clear_entry()
    fileEntry.delete(0, END)
            
def add_favourite():
    reactions = ','.join(reactionCombo['values'])
    copy(reactions)
    
    if len(favourite) == 0:   
        favourMenu.add_command(label="Edit", background="light grey", activebackground="light grey", command=edit_clipboard)    
    try: 
        ind = favourMenu.index(reactions)
        favourMenu.delete(ind)        
        favourMenu.insert_command(0, label=reactions, command=lambda: copy(reactions))   
        favourite.insert(0, favourite.pop(ind))                         
    except TclError:
        favourite.insert(0, reactions)        
        favourMenu.insert_command(0, label=reactions, command=lambda: copy(reactions))
             
    if len(favourite) > 10:
        favourite.pop()    
        favourMenu.delete(END)
        
def callback(event):
    event.widget.select_range(0, END)

def edit_clipboard():
    view_clipboard = Toplevel(window)
    view_clipboard.geometry("300x225")
    view_clipboard.title("Clipboard editor")
    view_clipboard.grid_columnconfigure(0, weight=1)
    edit_record = [0] * len(favourite)
    under_selection = [0] * len(favourite)
    
    def get_reaction(event):
        clipEntry.delete(0, END)
        index = clipList.curselection()[0]
        reaction = clipList.get(index)
        clipList.selection_clear(0, END)
        if reaction:
            under_selection[index] = 1        
            clipEntry["state"] = NORMAL
            clipEntry.insert(0, reaction)
            clipEntry.focus()
        
    def edit_reaction(event):
        reaction = clipEntry.get()
        index = under_selection.index(1)                
        clipList.delete(index)                
        if index % 2 == 0: 
            clipList.insert(index, reaction)
            clipList.itemconfig(index, background="light grey")
        else: clipList.insert(index, reaction)
        
        under_selection[index] = 0
        edit_record[index] = 1
        clipEntry.delete(0, END)
        clipEntry["state"] = DISABLED
        
    def del_reaction(event):
        index = clipList.curselection()[0]
        reaction = clipList.get(index)
        clipList.delete(index)
        clipList.insert(index, "")
        if index % 2 == 0: clipList.itemconfig(index, background="light grey")
        edit_record[index] = 2
        
        if clipEntry.get() == reaction: 
            clipEntry.delete(0, END)        
        
    def save():
        to_edit = [favourite.index(i) for i in favourite if edit_record[favourite.index(i)] == 1]
        for i in to_edit:
            favourMenu.delete(favourite.pop(i))            
            favourite.insert(i, clipList.get(i))
            favourMenu.insert_command((len(favourite) - i) - 1, label=favourite[i], 
                                        command=lambda: copy(new_reaction)) 
                
        to_delete = [j for j in favourite if edit_record[favourite.index(j)] == 2]
        for j in to_delete:
            favourMenu.delete(j)
            favourite.remove(j)
        
        if not favourite:
            favourMenu.delete("Edit")                                 
        view_clipboard.destroy()
                
    clipLabel = Label(view_clipboard, text="Saved combinations:")
    clipLabel.grid(column=0, row=0, columnspan=2)
    clipList = Listbox(view_clipboard, height=8, selectbackground="light green")
    clipList.grid(column=0, row=1, columnspan=4, sticky="ew")
    clipList.bind('<Double-Button-1>', get_reaction)
    clipList.bind('<BackSpace>', del_reaction)
    
    for ind in range(10):
        if ind < len(favourite): clipList.insert(END, favourite[ind])
        else: clipList.insert(END, "")       
        if ind % 2 == 0: clipList.itemconfig(ind, background="light grey")
    
    clipEntry = Entry(view_clipboard, state=DISABLED)
    clipEntry.grid(column=0, row=2, columnspan=4, sticky="ew")
    clipEntry.bind('<Return>', edit_reaction) 
    clipButton = Button(view_clipboard, text="   Save   ", command=save)
    clipButton.grid(column=1, row=3)

def on_closing():
    window.quit()
    window.destroy()

menubar = Menu(window, activebackground='dark grey', activeforeground='white')
fileMenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="  File  ", menu=fileMenu, underline=2)
fileMenu.add_command(label="New", underline=0, command=new_state)
fileMenu.add_command(label="Save", underline=0, background="light grey", activebackground="light grey", command=save_state)
recentMenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="History", menu=recentMenu, underline=0)
favourMenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Clipboard", menu=favourMenu, underline=0)

netLabel = Label(window, text="Chemical network", font=("Arial Bold", 12))
netLabel.grid(column=0, row=0)
netEntry = Entry(window, width=30, selectbackground='black', selectforeground='white')
netEntry.grid(column=1, row=0, columnspan=3)
netEntry.bind('<Control-KeyRelease-a>', callback)
netButton = Button(window, text="Browse files", command=lambda: browse_files(netEntry))
netButton.grid(column=4, row=0)
        
speciesLabel = Label(window, text="Species", font=("Arial Bold", 12))
speciesLabel.grid(column=0, row=1)
speciesEntry = Entry(window, width=30, selectbackground='black', selectforeground='white')
speciesEntry.grid(column=1, row=1, columnspan=3)
speciesEntry.bind('<Control-KeyRelease-a>', callback)
speciesEntry.bind('<Return>', search_species)
speciesEntry.focus()
enterButton = Button(window, text="    Search     ", command=search_species)
enterButton.grid(column=4, row=1)

sourceLabel = Label(window, text="Sources:", font=("Arial Bold", 11))
sourceLabel.grid(column=0, row=2, columnspan=3)
sinkLabel = Label(window, text="Sinks:", font=("Arial Bold", 11))
sinkLabel.grid(column=3, row=2, columnspan=2)

sourceList = Listbox(window, width=30, selectbackground="light green", selectmode="multiple", exportselection=False)
sourceList.grid(column=0, row=3, columnspan=3, rowspan=4)
sinkList = Listbox(window, width=30, selectbackground="light green", selectmode="multiple", exportselection=False)
sinkList.grid(column=3, row=3, columnspan=3, rowspan=4)
addallButton = Button(window, text="Select all", command=select_all)
addallButton.grid(column=0, row=7)
addallButton = Button(window, text="Add selected", command=add_select)
addallButton.grid(column=1, row=7, columnspan=3)
revCheck = ttk.Checkbutton(window, text='reverse', variable=rev_var)
revCheck.grid(column=4, row=7)

separator = ttk.Separator(window, orient='horizontal')
separator.grid(column=0, row=8, ipadx=280, pady=10, columnspan=7)

reactionCombo = ttk.Combobox(window, width=20)
reactionCombo.grid(column=0, row=9, columnspan=2)
reactionCombo.bind('<Return>', add_entry)
reactionCombo.bind('<BackSpace>', del_entry)
addButton = Button(window, text="   Add   ", command=add_entry)
addButton.grid(column=2, row=9)
delButton = Button(window, text="Remove", command=del_entry)
delButton.grid(column=3, row=9)
clearButton = Button(window, text="Clear all", command=clear_entry)
clearButton.grid(column=4, row=9)

numLabel = Label(window, text="Number of logged reactions is 0 (max. 10 for plotting)")
numLabel.grid(column=0, row=10, columnspan=4)
copyButton = Button(window, text="      Copy      ", command=add_favourite)
copyButton.grid(column=4, row=10)

fileLabel = Label(window, text="Output file", font=("Arial Bold", 12))
fileLabel.grid(column=0, row=11)
fileEntry = Entry(window, width=30, selectbackground='black', selectforeground='white')
fileEntry.grid(column=1, row=11, columnspan=3)
fileEntry.bind('<Control-KeyRelease-a>', callback)
fileButton = Button(window, text="Browse files", command=lambda: browse_files(fileEntry))
fileButton.grid(column=4, row=11)

nameLabel = Label(window, text="File name", font=("Arial Bold", 12))
nameLabel.grid(column=0, row=12)
nameEntry = Entry(window, width=30, selectbackground='black', selectforeground='white')
nameEntry.grid(column=1, row=12, columnspan=3)
nameEntry.bind('<Control-KeyRelease-a>', callback)
nameEntry.bind('<Return>', plot_graph)

sumRadio = Radiobutton(window, text="overall rate", variable=option_var, value=1)
sumRadio.grid(column=0, row=13)
indivRadio = Radiobutton(window, text="individual rates", variable=option_var, value=0)
indivRadio.grid(column=1, row=13, columnspan=3)
photoRadio = Radiobutton(window, text="photolysis", variable=option_var, value=2)
photoRadio.grid(column=4, row=13)

plotButton = Button(window, text="   Plot   ", command=plot_graph)
plotButton.grid(column=1, row=14, columnspan=3)

load_state()
window.geometry('560x500')
window.resizable(False, False) 
window.config(menu=menubar)
window.protocol("WM_DELETE_WINDOW", on_closing) 
window.mainloop()
