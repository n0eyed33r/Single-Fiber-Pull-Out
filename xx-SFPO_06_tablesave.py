import csv
import tkinter as tk
from tkinter import filedialog
import SFPO_config

def speichere_csv():
    root = tk.Tk()
    root.withdraw()  # Verstecke das Hauptfenster

    # Dateidialog für Speicherort und Dateinamen anzeigen
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        initialdir=SFPO_config.mainfolder,
        title="CSV-Datei speichern",
        filetypes=[("CSV-Dateien", "*.csv")])

    if not file_path:
        return  # Abbruch, wenn kein Speicherort ausgewählt wurde

    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)

        for i in range(len(SFPO_config.measurements)):
            f_kink = SFPO_config.integral_bis_maximal[i][1]
            f_max = SFPO_config.integrale_nach_maximal[i][0]
            w_total = SFPO_config.gesamtintegrale[i][1]
            w_before_max = SFPO_config.integral_bis_maximal[i][1]
            w_after_max = SFPO_config.integrale_nach_maximal[i][1:]

            row = [f_kink, f_max, w_total, w_before_max, *w_after_max]
            writer.writerow(row)