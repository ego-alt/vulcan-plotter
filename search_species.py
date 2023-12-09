import re
import fileinput


def find_species(file1, species):  # Outputs all chemical network reactions involving species A and count instances
    with open(file1, 'r') as fp:
        count = 0
        species = ' ' + species + ' '
        source, sink = [], []

        lines = fp.readlines()
        for line in lines:
            line = line.replace('\t', ' ')
            if not line.startswith('#') and species in line:
                # Ignores comments and distinguishes between repetitive species, e.g. 'CH2NH' in CH2NH2
                r = re.compile('^([0-9\s]+)\[(.*?)\->(.*?)\]')
                result = re.findall(r, line)
                if result:
                    result = result[0]
                    num1 = result[0].strip()
                    if num1:
                        num2 = str(int(num1) + 1)
                        reaction = num1 + ' ' + result[1].strip() + ' -> ' + result[2].strip()
                        rev_reaction = num2 + ' ' + result[2].strip() + ' -> ' + result[1].strip()
                        if species in result[1]:
                            sink.append(reaction)
                            source.append(rev_reaction)
                            count += 1
                        elif species in result[2]:
                            source.append(reaction)
                            sink.append(rev_reaction)
                            count += 1
                        else:
                            pass

        print(f'The total number of network reactions involving {species} is {count * 2}.')
        # print(*reaction_num, sep=',')
        # print(f'Sources:')
        # print(*source, sep='\n')
        # print(f'Sinks:')
        # print(*sink, sep='\n')
        return source, sink


"""def reverse_reaction(line):
    num, reaction = line.split(maxsplit=1)
    num = str(int(num) + 1)
    reactant, product = reaction.split(' -> ')
    return num + ' ' + product + ' -> ' + reactant
"""


def find_max(rates):
    peak_reaction_rates = []
    for height_layer in range(rates[0].size):
        peak_rate = [k[height_layer] for k in rates]
        peak_reaction_rates.append(max(peak_rate))
    return peak_reaction_rates


def choose_significant_reactions(rates, reactions):
    summed_rate = [sum(layer_rate) for layer_rate in rates]
    overall_threshold = 0.6 * max(summed_rate)  # 60% of largest summed reaction rate (across all altitudes)
    significant_overall = [reactions[ind] for ind, i in enumerate(summed_rate) if i >= overall_threshold]
    return significant_overall


"""def find_sig(reaction_rates, reaction_num):
    fastest_reaction = find_max(reaction_rates, reaction_num)
    peak_threshold = 0.6  # 80% of maximum reaction rate in a single altitude layer
    top_peak = [reaction_rates[reaction_num.index(i)][alt] * peak_threshold for alt, i in enumerate(fastest_reaction)]
    
    # Peak threshold applied to highest reaction rate in each layer 
    signif_peak = set([reaction_num[ind] for ind, j in enumerate(reaction_rates) if any(j >= top_peak)])
    return signif_peak"""


def read_network(file1):  # Stores all chemical network reactions in a list for compare_txt
    reactions = []
    with open(file1, 'r') as fp:
        lines = fp.readlines()
        for line in lines:
            try:
                result = re.search(r'(?<=\[).+?(?=\])', line)
                reactions.append(result[0].rstrip())
            except TypeError:
                pass
    return reactions


def compare_txt(file1, file2):  # Compares two reaction networks
    set1 = set(read_network(file1))
    set2 = set(read_network(file2))
    if set1 == set2:
        print("These are identical networks.")
    elif set1 > set2:
        print(f'{file1} has extra reaction(s) {set1.difference(set2)}')
    elif set2 > set1:
        print(f'{file2} has extra reaction(s) {set2.difference(set1)}')


def find_text(line, r):  # Given one line, finds the specified text
    if r.findall(line):
        search_text = r.findall(line)[0]
        return search_text
    else:
        return None


def repl_text(line, r, replacement_text, tag, update=False):  # Given one line, finds and replaces the specified text
    if r.findall(line):
        search_text = r.findall(line)[0]
        print(line.replace(search_text, replacement_text), end='')
        if update:
            print(f'# This has been appended {tag} times')
        return True
    else:
        return False


def assign_label(name):  # Assigns formatted labels based on the molecule, i.e. with subscripted numbers
    tex_labels = {'H': 'H', 'H2': 'H$_2$', 'O': 'O', 'OH': 'OH', 'H2O': 'H$_2$O', 'CH': 'CH', 'C': 'C', 'CH2': 'CH$_2$',
                  'CH3': 'CH$_3$', 'CH4': 'CH$_4$', 'HCO': 'HCO', 'H2CO': 'H$_2$CO', 'C4H2': 'C$_4$H$_2$',
                  'C2': 'C$_2$', 'C2H2': 'C$_2$H$_2$', 'C2H3': 'C$_2$H$_3$', 'C2H': 'C$_2$H', 'CO': 'CO',
                  'CO2': 'CO$_2$', 'He': 'He', 'O2': 'O$_2$', 'CH3OH': 'CH$_3$OH', 'C2H4': 'C$_2$H$_4$',
                  'C2H5': 'C$_2$H$_5$', 'C2H6': 'C$_2$H$_6$', 'CH3O': 'CH$_3$O', 'CH2OH': 'CH$_2$OH', 'N2': 'N$_2$',
                  'NH3': 'NH$_3$', 'NO2': 'NO$_2$', 'HCN': 'HCN', 'NO': 'NO', 'O3': 'O$_3$'}  # Text labels for plotting

    if name in tex_labels:
        label = tex_labels[name]
    else:
        label = name
    return label


def calculateC_Oratio(file1):
    with fileinput.FileInput(file1, inplace=True) as file:
        ch4, co2 = None, None
        for line in file:
            if ch4 and co2:
                ch4, co2 = float(ch4), float(co2)
                try:
                    c_oratio = (ch4 + co2) / (2 * co2)
                except ZeroDivisionError:
                    c_oratio = None
            else:
                ch4 = find_text(line, re.compile(r"'CH4':([0-9Ee\*.-]+)"))
                co2 = find_text(line, re.compile(r"'CO2':([0-9Ee\*.-]+)"))
            print(line, end='')
        print(f'The C/O ratio for CO2:{co2} and CH4:{ch4} is {c_oratio}')
        return c_oratio
