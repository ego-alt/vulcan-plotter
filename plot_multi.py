'''
This script reads VULCAN output (.vul) files using pickle and plot the species volumn mixing ratios as a function of pressure, with the initial abundances (typically equilibrium) shown in dashed lines.
Plots are saved in the folder assigned in vulcan_cfg.py, with the default plot_dir = 'plot/'.
'''
import extract_vul
import re
import sys
import numpy as np
import matplotlib.pylab as ply
from search_species import find_text


output_files = ['../output/H2O_1e-6/oRimmer0.75.vul', '../output/H2O_1e-6/oRimmer1.0.vul', '../output/H2O_1e-6/oRimmer1.25.vul', '../output/H2O_1e-6/oRimmer1.50.vul']
spec = 'HCN'
n = 4
colors = ply.cm.jet(np.linspace(0, 1, n))

for ind, f in enumerate(output_files):
    vul_obj = extract_vul.Vul([0, f, f'full_track{spec}', spec])

    species = vul_obj.param('variable', 'species')
    ymix = vul_obj.param('variable', 'ymix')
    pco = vul_obj.param('atm', 'pco')
    zco = vul_obj.param('atm', 'zco')
    zmco = vul_obj.param('atm', 'zmco')
    x = ymix[:, species.index(spec)]
    
    co_ratio = re.compile(r"./[A-Za-z]+([0-9\.]+)\.vul")
    label = find_text(f, co_ratio)

    if '-h' in sys.argv:
        y = zco[1:] / 1.e5
        plot = vul_obj.plot(x, y, 1, colors[ind], label)        
        plot.ylim((zmco[1] / 1.e5, zmco[-1] / 1.e5))
        vul_obj.name(f'{spec} abundance-altitude curves at different C/O ratios', "Mixing ratio", "Height (km)")
        vul_obj.scale(plot, x_log=True, y_log=False)
    else:
        y = pco / 1.e6
        plot = vul_obj.plot(x, y, 1, colors[ind], label)
        plot.ylim((pco[0] / 1.e6, pco[-1] / 1.e6))
        vul_obj.name(f'{spec} abundance-altitude curves at different C/O ratios', "Mixing ratio", "Pressure (bar)")
        vul_obj.scale(plot, x_log=True, y_log=True)
        
    # plot.xlim((1.E-20, 1.e-2))

vul_obj.save(plot)

