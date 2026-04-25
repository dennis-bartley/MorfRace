import tkinter as tk
from sys import argv
from Utils import get_full_path

from RosterController import RosterController

def main(rosterFile):
        
    controller = RosterController(rosterFile)
    tk.mainloop()

if __name__ == "__main__":
    rosterFile = "MorfRace.rst"
    if len(argv) > 1:
        rosterFile = argv[1]
        
    rosterFile = get_full_path(rosterFile)
    main(rosterFile)