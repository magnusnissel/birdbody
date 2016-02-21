import tkinter as tk
import multiprocessing as mp
from birdbody.bbcore import BirdbodyGUI


def main():
    root = tk.Tk()
    BirdbodyGUI(root)

if __name__ == '__main__':
    mp.freeze_support()
    main()
