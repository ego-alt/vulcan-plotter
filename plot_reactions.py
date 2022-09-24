'''
This script reads VULCAN output (.vul) files using pickle and plot the species volume mixing ratios as a function of pressure, with the individual contributing reactions shown in dashed lines.
Plots are saved in the folder assigned in vulcan_cfg.py, with the default plot_dir = 'plot/'.
'''
import sys
import re
import numpy as np
import fileinput
import extract_vul
from search_species import assign_label, find_text, find_sig
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

sys.path.insert(0, '../')  # Including the upper level of directory for the path of modules
import vulcan_cfg

filename_net = '../thermo/NCHO_full_photo_network_pb.txt' # Change the chemical network HERE


class Plotter:
    def __init__(self, arguments):
        self.vul_obj = extract_vul.Vul(arguments)
        self.species = self.vul_obj.param('variable', 'species')
        self.yabun = self.vul_obj.param('variable', 'y') # Number of molecules cm-3 for each species in each layer
        self.ymix = self.vul_obj.param('variable', 'ymix') # Mixing ratio (/[M]) for each species in each layer
        self.m = self.vul_obj.param('atm', 'n_0') # Total number of molecules cm-3 ([M]) in each layer
        self.k = self.vul_obj.param('variable', 'k') # Reaction rates in each layer
        self.zco = self.vul_obj.param('atm', 'zco')
        self.zmco = self.vul_obj.param('atm', 'zmco')
        self.ni, self.nz = len(self.species), vulcan_cfg.nz

        self.species_req = self.vul_obj.species_req[0] # INPUT species of interest
        self.reaction_num = [int(i) for i in self.vul_obj.reactions] # INPUT reaction indices
        self.reaction_spec = {} # Dictionary of reactants
        self.reactions = {} # Dictionary of reaction strings
    
        for n in self.reaction_num:
            with fileinput.FileInput(filename_net, inplace=True) as file:
                if n % 2 == 0: # Even reactions are odd reactions in reverse
                     start = n - 1
                     r = re.compile(r"([0-9A-Z\_]+)[\s\+]*([0-9A-Z\_]*)[\s\+]*([0-9A-Z\_]*)\s*\]")
                     self.reverse = True
                else: 
                    start = n
                    r = re.compile(r"\[\s*([0-9A-Z\_]+)[\s\+]*([0-9A-Z\_]*)[\s\+]*([0-9A-Z\_]*)")
                    self.reverse = False

                for line in file:
                    print(line, end='')
                    if line.startswith(str(start) + ' '):
                        reac, prod = find_text(line, re.compile(r"\[(.*?)\->(.*?)\]"))
                        if self.reverse: reaction = prod.strip() + ' -> ' + reac.strip()
                        else: reaction = reac.strip() + ' -> ' + prod.strip()
                
                        self.reactions[n] = reaction.strip()
                        reactants = find_text(line, r)
                        self.reaction_spec[n] = [i.replace(' ', '') for i in reactants if i.strip()]
                    else:
                        continue
        
    def plotting(self, total=False):
        # var total TRUE: plots overall reaction rate, FALSE: plots individual reactions
        print(self.reactions)
        print(self.reaction_spec)

        main_species = assign_label(self.species_req)
        x_0, y = self.ymix[:, self.species.index(self.species_req)], self.zco[1:] / 1.e5
        fig, ax = plt.subplots()
        ax.set_title(f'Reaction rates and corresponding {main_species} profile')
        ax.set_ylabel("Height (km)")
        ax.set_xlabel('Mixing ratio')
        ax.plot(x_0, y, lw=1.0, color='black')
        
        plt.gca().set_xlim([1e-20, 1e-8])
        # plt.gca().set_ylim([self.zmco[1] / 1.e5, self.zmco[-1] / 1.e5])
        plt.gca().set_ylim([self.zmco[1] / 1.e5, 120])
        ax.legend([main_species], loc='best') 
        ax.xaxis.set_major_formatter(mtick.FormatStrFormatter('%.1e'))
        if not total: plt.gca().set_xscale('log')

        ax2 = ax.twiny()
        ax2.set_xlabel('Reaction rate (molec cm$^{-3}$ s$^{-1}$)')
        k_holder = []
        if total:
            for n in self.reactions:
                find_k = self.k[n]
                for reactant in self.reaction_spec[n]:
                    if reactant == 'M': x_1 = self.m
                    else: x_1 = self.yabun[:, self.species.index(reactant)]
                    find_k = np.multiply(find_k, x_1)
            
                if self.species_req in self.reaction_spec[n]: k_holder.append(np.negative(find_k))
                else: k_holder.append(find_k) # Sums production rates and deducts loss rates 

            ax2.plot(sum(k_holder), y, lw=1.0, linestyle='dashed') # Plots the overall reaction rate (production - loss)
            ax2.plot(sum(k_holder).clip(min=0), y, lw=1.0, color='orange', linestyle='dashed') # Plots reaction rate with negative values clipped
           
        else:
            for n in self.reactions:
                find_k = self.k[n]
                for reactant in self.reaction_spec[n]:
                    if reactant == 'M': x_1 = self.m
                    else: x_1 = self.yabun[:, self.species.index(reactant)]
                    find_k = np.multiply(find_k, x_1)
                    
                k_holder.append(find_k)
                line = ax2.plot(find_k, y, lw=1.0, label=self.reactions[n], linestyle='dashed')
                     
            ax2.legend(frameon=0, prop={'size': 10}, loc = 'lower left')
  
        if not total: 
            plt.gca().set_xscale('log')
            plt.gca().set_xlim([1e-14, 1e6])
    
        print(find_sig(k_holder, self.reaction_num)) 
        plt.tight_layout()
        self.vul_obj.save(plt)

    def photolysis(self):        
        y = self.zco[1:] / 1.e5
        fig, ax = plt.subplots()
        ax.set_title(f'Photolysis rates over altitude')
        ax.set_ylabel("Height (km)")
        ax.set_xlabel('Reaction rate (molec cm$^{-3}$ s$^{-1}$)')
        
        flipped_dict = {}
        for key, value in self.reaction_spec.items():
            value = value[0]
            if value not in flipped_dict: flipped_dict[value] = [key]
            else: flipped_dict[value].append(key)
        print(flipped_dict)
        
        key_species = []
        k_holder = []
        for reactant, i in flipped_dict.items():
            find_k = sum([self.k[n] for n in i])
            x = self.yabun[:, self.species.index(reactant)]
            find_k = np.multiply(find_k, x)            
            k_holder.append(find_k)
            if reactant in key_species:
                ax.plot(find_k, y, lw=1.0, label=f"{reactant} photolysis")
            else:
                ax.plot(find_k, y, lw=1.0, label=f"{reactant} photolysis", linestyle='dashed')
            ax.legend(frameon=0, prop={'size': 10}, loc = 'lower left')
        
        plt.gca().set_xscale('log')
        plt.gca().set_xlim([1e-28, 1e8])
        plt.gca().set_ylim([self.zmco[1] / 1.e5, self.zmco[-1] / 1.e5])
        # plt.gca().set_ylim([self.zmco[1] / 1.e5, 120])
        plt.tight_layout()
        self.vul_obj.save(plt)
        
    def by_species(self):
        pass
    
    

