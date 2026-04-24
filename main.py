"""
Main driver for the Molecular Editor application
"""

import tkinter as tk
from molecular_editor import MolecularEditor

def main():
    root = tk.Tk()
    app = MolecularEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()