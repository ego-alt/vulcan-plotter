import sys
import extract_vul
import numpy as np
from heapq import nlargest, nsmallest
from search_species import assign_label
import matplotlib.pyplot as plt

sys.path.insert(0, '../')  # including the upper level of directory for the path of modules
import vulcan_cfg

vul_obj = extract_vul.Vul(sys.argv)

species = vul_obj.param('variable', 'species')
ymix = vul_obj.param('variable', 'ymix')
pco = vul_obj.param('atm', 'pco')
gas_indx = vul_obj.param('atm', 'gas_indx')
full_jac = vul_obj.param('variable', 'full_jac')

ni = len(species)
nz = vulcan_cfg.nz
species_req = vul_obj.species_req[0]
i = species.index(species_req)

indx = [] 
for j in range(ni): 
    indx.append(np.arange(j,j+ni*nz,ni)) 

def find_sig():
    matr_order = {}
    for j in range(ni):
        jac = full_jac[indx[i],indx[j]]
        total_val = jac.sum()
        if total_val == 0:
            pass
        else:
            matr_order[j] = total_val

    large_loss = nlargest(6, matr_order, key=matr_order.get)
    large_prod = nsmallest(6, matr_order, key=matr_order.get)
    return large_loss, large_prod
    

def plotting(species_list):
    main_species = assign_label(species_req)
    
    x = ymix[:, i]
    y = pco / 1.e6
    fig, ax = plt.subplots()
    ax.set_title(f'{main_species} based on reactions involving certain species')
    ax.set_ylabel("Pressure (bar)")
    ax.set_xlabel('Mixing ratio')
    ax.plot(x, y, lw=1.0, color='black') 
    
    plt.gca().set_ylim([pco[0] / 1.e6, pco[-1] / 1.e6])
    ax.legend([main_species], loc='best')
    plt.gca().set_xscale('log')
    plt.gca().set_yscale('log')
        
    ax2 = ax.twiny()
    ax2.set_xlabel('Reaction rate (molec cm$^{-3}$ s$^{-1}$)')
    for j in species_list:
        name = species[j]
        x = full_jac[indx[i], indx[j]] * ymix[:, i] 
        ax2.plot(x, y, lw=1.0, label=f'rxns of {assign_label(name)}', linestyle='dashed')
        plt.gca().set_xscale('log')
        plt.gca().set_yscale('log')
        ax2.legend(frameon=0, prop={'size': 10}, loc = 'lower left')
        
    vul_obj.save(plt)


try: 
    contr_species = vul_obj.reactions
    index_list = [species.index(spec) for spec in contr_species]
    plotting(index_list)
        
except AttributeError:
    large_loss, large_prod = find_sig()
    plotting(large_loss)
    


