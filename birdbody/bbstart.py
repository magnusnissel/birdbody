import tkinter as tk
import multiprocessing as mp
try:
	from birdbody.bbcore import BirdbodyGUI
except ImportError:
	from bbcore import BirdbodyGUI

def main():
    root = tk.Tk()
    BirdbodyGUI(root)

if __name__ == '__main__':
    mp.freeze_support()
    main()
