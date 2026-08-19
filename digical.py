"""
DigiCal Business Calculator
Main application entry point
"""
import tkinter as tk
from gui import DigiCalGUI

def main():
    root = tk.Tk()
    app = DigiCalGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
