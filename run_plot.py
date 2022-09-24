'''
This script changes the methane abundances and methane surface fluxes in configuration (.txt) files, then automatically runs the model.
Plots are saved in the folder assigned in vulcan_cfg.py with different output names each iteration.
'''
import os
import re
import sys
import fileinput
from search_species import repl_text


vars = [4e-5, 8e-5, 1.2e-4, 1.6e-4, 2e-4, 2.4e-4, 2.8e-4, 3.2e-4, 3.6e-4]
filename_bot = '../atm/BC_bot_terr.txt'
filename_cfg = '../vulcan_cfg.py'


def methane_abundance(line, var, tag):
    r = re.compile(r"('CH4':[0-9Ee\*.-]+)")
    replacement_text = f"'CH4':{var}"
    val = repl_text(line, r, replacement_text, tag, True)
    return val
    
        
def rename(line, var, tag):
    r = re.compile(r"out_name\s*=\s*([\S]+)")
    replacement_text = f"'PCb-um-nchofull-ch4_{tag}.vul'"
    val = repl_text(line, r, replacement_text, tag)
    return val
            
            
def methane_flux(line, var, tag):
    r = re.compile(r"CH4\s*([\S]+)")
    replacement_text = str(var)
    val = repl_text(line, r, replacement_text, tag)
    return val
    

for var in vars:
    tag = vars.index(var) + 169
    with fileinput.FileInput(filename_cfg, inplace=True) as file:
        for line in file:
            if not rename(line, var, tag):
                print(line, end='')
                
    with fileinput.FileInput(filename_cfg, inplace=True) as file:        
        for line in file:
            if not methane_abundance(line, var, tag):
                print(line, end='')
            
    os.chdir('../')
    os.system('python vulcan.py')
    os.chdir('./plot_py_new')
    os.system(f'python plot_vulcan.py ../output/PCb-um-nchofull-ch4_{tag}.vul CH4_{tag}_{var} H2O,CO2,O3,OH,NH3,CH4,HCN,C2H2,C4H2')

