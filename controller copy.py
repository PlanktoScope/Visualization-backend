import sys
import threading

import load_dataframe as ld
import scatter_plot as sp
import hist_plot as hp
import html_manager as hm

while True:
    commande = sys.stdin.readline().strip()
    if("load dataframe" in commande):
        args = commande.split(" ")
        if(len(args) != 3):
            print(args,"\nCommande invalide\n Exemple: load dataframe /path/to/dataframe")
        else:
            df = ld.load_dataframe(args[2])
    elif("scatter plot" in commande):
        args = commande.split(" ")
        if(len(args) != 4):
            print(args,"\nCommande invalide\n Exemple: scatter plot x y")
        else:
            x = args[2]
            y = args[3]
        sp.ScatterPlot(df,x,y)
    elif("hist plot" in commande):
        args = commande.split(" ")
        if(len(args) <3):
            print(args,"\nCommande invalide\n Exemple: hist plot x")
        else:
            x = args[2]
        hp.HistPlot(df,x)

    # elif("remove iframe" in commande):
    #     args = commande.split(" ")
    #     if(len(args) != 3):
    #         print(args,"\nCommande invalide\n Exemple: remove iframe /path/to/iframe")
    #     else:
    #         hm.remove_iframe(args[2])