# vulcan-plotter

The VULCAN plotter can plot individual reactions overlaid over the altitude-abundance curve of a species from the .vul output files of the chemical kinetic network VULCAN. To do so, it searches the chemical network and identifies source & sink reactions based on the chemical species provided, which are displayed in a window pane. From this window pane, you can directly select reactions (highlighted in green) and press RETURN to register the reactions or BACKSPACE to remove them. Otherwise, you can add or remove individual reactions from the entry box by entering the reaction number. 

In addition, the plotter keeps track of your plotting history. If you want to return to a previous combination of reactions, select it from the 'History' tab. Note that this will overwrite all current selected and registered reactions after a warning pop-up. 

To launch the plotter, run app.py from the command line.
