import tkinter as tk
from tkinter import filedialog
import os

# Tkinter-Fenster erstellen
root = tk.Tk()
root.withdraw()

# Überordner auswählen
folder_path = filedialog.askdirectory(title="Überordner auswählen")

# Unterordner durchlaufen und List Comprehension verwenden
sub_dirs = [sub_dir for sub_dir in os.listdir(folder_path) if
            os.path.isdir(os.path.join(folder_path, sub_dir))]

# List Comprehension für das Anwenden von main_modul.py
[SFPO_00_main(os.path.join(folder_path, sub_dir)) for
 i, sub_dir in enumerate(sub_dirs)]
