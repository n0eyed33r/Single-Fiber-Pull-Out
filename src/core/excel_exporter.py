# src/core/excel_exporter.py
import pandas as pd
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
from src.core.data_statistics import MeasurementAnalyzer


class ExcelExporter:
    def __init__(self):
        self.results = {
            'Probenname': [],
            'F_max [N]': [],
            'F_max_std [N]': [],
            'Einbettlänge [µm]': [],
            'Einbettlänge_std [µm]': [],
            'IFSS [MPa]': [],
            'IFSS_std [MPa]': [],
            'Arbeit [µJ]': [],
            'Arbeit_std [µJ]': []
        }

    def save_to_excel(self):
        """Speichert die Ergebnisse in einer Excel-Datei an ausgewähltem Ort"""
        # Dialog zur Ordnerauswahl
        root = tk.Tk()
        root.withdraw()  # Verstecke das Hauptfenster

        # Erstelle Dateinamen mit Zeitstempel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"SFPO_Ergebnisse_{timestamp}.xlsx"

        # Öffne Speicherdialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=default_filename,
            filetypes=[("Excel files", "*.xlsx")],
            title="Speicherort für Excel-Datei wählen"
        )

        if file_path:  # Wenn ein Pfad ausgewählt wurde
            df = pd.DataFrame(self.results)
            df.to_excel(file_path, index=False)
            print(f"\nErgebnisse gespeichert in: {file_path}")
        else:
            print("\nSpeichern abgebrochen")

    def add_measurement_series(self, name: str, analyzer: 'MeasurementAnalyzer'):
        """Fügt die Ergebnisse einer Messreihe hinzu"""
        if analyzer:  # Prüfe ob analyzer nicht None ist
            self.results['Probenname'].append(name)
            self.results['F_max [N]'].append(analyzer.calculate_mean('forces'))
            self.results['F_max_std [N]'].append(analyzer.calculate_stddev('forces'))
            self.results['Einbettlänge [µm]'].append(analyzer.calculate_mean('lengths'))
            self.results['Einbettlänge_std [µm]'].append(analyzer.calculate_stddev('lengths'))
            self.results['IFSS [MPa]'].append(analyzer.calculate_mean('ifss'))
            self.results['IFSS_std [MPa]'].append(analyzer.calculate_stddev('ifss'))
            self.results['Arbeit [µJ]'].append(analyzer.calculate_mean('works'))
            self.results['Arbeit_std [µJ]'].append(analyzer.calculate_stddev('works'))