import pickle
from PIL import Image
import matplotlib.pyplot as plt
import os
import vulcan_cfg


plot_dir = './plots/'


class Vul:
    def __init__(self, system_arg):
        vul_data = system_arg[0]  # Set the 1st input as the filename of vulcan output
        with open(vul_data, 'rb') as handle:
            self.data = pickle.load(handle)            
        self.plot_name = system_arg[1]  # 2nd input: output filename
        self.species_req = system_arg[2]  # 3rd input: species names
        self.reactions = system_arg[3]  # 4th input: list of reactions

    def param(self, category, var):
        param = self.data[category][var]
        return param

    def plot(self, x_data, y_data, lw, color=None, label=None, linestyle=None): # The most basic, functional plot
        if linestyle == 'd':
            plt.plot(x_data, y_data, lw=lw, color=color, label=label, linestyle = 'dashed')
        else:
            plt.plot(x_data, y_data, lw=lw, color=color, label=label)
        plt.legend(frameon=0, prop={'size': 10}, loc='best')
        return plt
        
    def name(self, title, x_name, y_name): # Set the plot title, x-axis and y-axis labels
        plt.title(title)
        plt.xlabel(x_name)
        plt.ylabel(y_name)
        
    def scale(self, plot, x_log=None, y_log=None, x_invert=None, y_invert=None): # Scale the axes if necessary
        if x_log: plot.gca().set_xscale('log')
        if y_log: plot.gca().set_yscale('log')

        if x_invert: plot.gca().invert_xaxis()
        if y_invert: plot.gca().invert_yaxis()

    def save(self, plot): # Save the plot in the specified directory
        if not os.path.exists(plot_dir):  # Checking if the folder exists
            print('The plotting directory assigned in vulcan_cfg.py does not exist.')
            print('Directory ', plot_dir, " created.")
            os.mkdir(plot_dir)
        plot.savefig(plot_dir + self.plot_name + '.png')
        plot.savefig(plot_dir + self.plot_name + '.eps')
        
        if vulcan_cfg.use_PIL:
            plot = Image.open(plot_dir + self.plot_name + '.png')
            plot.show()
        else:
            plot.show()

