# vulcan-plotter

The VULCAN plotter can plot individual reactions, photolysis rates, and net reaction rates from the .vul output files of the chemical kinetic network VULCAN. To do so, it searches the chemical network and identifies source & sink reactions based on the chemical species provided, which are displayed in a window pane. From this window pane, you can directly select reactions (highlighted in green) and "add selected" to register the reactions for plotting. Otherwise, you can add or remove individual reactions from the entry box by entering the reaction number. In addition, the plotter keeps track of your plotting history, as well as storing up to 10 specific combinations of reactions in the 'Clipboard'. 

Note that all reaction numbers in the window pane are odd, which is a consequence of how the chemical network is designed. Each line has a forward and reverse reaction, denoted by odd and even numbers respectively. Reverse reactions can be added by inputting the corresponding even number. If you check "reverse" and then "add selected", both the forward and reverse reaction will be added automatically. Once reactions are added to the register, the line in the window pane changes colour as an indication (highlighted light grey if EITHER forward or reverse has been added, dark grey if BOTH have been added). 

If you want to return to a previous combination of reactions, select it from the 'History' tab. Note that this will overwrite all current selected and registered reactions after a warning pop-up. On the other hand, selecting combinations from 'Clipboard' will not overwrite the current settings and will only add it to your system clipboard, so that you can paste it into the entry box. Several reactions can be added at once, as long as they are only separated by a comma with NO spaces. The feature of manually editing 'Clipboard' is still under development.

Before closing the application, save your current settings if you want to pick up where you left off. Saved settings include the chemical network file, selected chemical species, selected reactions, reactions added to the register, the output file, and combinations stored in the clipboard, but not plotting history or the file name. These settings will be loaded on default when starting up the plotter again. 

To launch the plotter, run app.py from the command line.


