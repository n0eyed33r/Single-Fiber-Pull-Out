# src/core/excel_exporter.py
import pandas as pd
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
from src.core.data_statistics import MeasurementAnalyzer
from typing import Optional

class ExcelExporter:
    def __init__(self):
        # Grundlegende Ergebnisse für die Haupttabelle
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
        # Dictionary für Arbeitsintervalle: {Probenname: Analyzer}
        self.interval_data = {}

    def add_measurement_series(self, name: str, analyzer: 'MeasurementAnalyzer'):
        """Fügt Ergebnisse einer Messreihe hinzu und speichert den Analyzer für Intervalldaten"""
        if analyzer:
            # Hauptergebnisse hinzufügen
            self.results['Probenname'].append(name)
            self.results['F_max [N]'].append(analyzer.calculate_mean('forces'))
            self.results['F_max_std [N]'].append(analyzer.calculate_stddev('forces'))
            self.results['Einbettlänge [µm]'].append(analyzer.calculate_mean('lengths'))
            self.results['Einbettlänge_std [µm]'].append(analyzer.calculate_stddev('lengths'))
            self.results['IFSS [MPa]'].append(analyzer.calculate_mean('ifss'))
            self.results['IFSS_std [MPa]'].append(analyzer.calculate_stddev('ifss'))
            self.results['Arbeit [µJ]'].append(analyzer.calculate_mean('works'))
            self.results['Arbeit_std [µJ]'].append(analyzer.calculate_stddev('works'))

            # Analyzer für Intervalldaten speichern
            self.interval_data[name] = analyzer

    def save_to_excel(self) -> Optional[Path]:
        """
        Speichert die Hauptergebnisse in einer Excel-Datei.

        Returns:
            Optional[Path]: Der Pfad zur gespeicherten Datei oder None, wenn der Benutzer abbricht
        """
        root = tk.Tk()
        root.withdraw()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"SFPO_Ergebnisse_{timestamp}.xlsx"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=default_filename,
            filetypes=[("Excel files", "*.xlsx")],
            title="Speicherort für Hauptergebnis-Datei wählen"
        )

        if file_path:
            df = pd.DataFrame(self.results)
            df.to_excel(file_path, index=False)
            return Path(file_path)
        return None

    def save_work_intervals_to_excel(self) -> Optional[Path]:
        """ Speichert die Arbeitsintervalle in einer separaten Excel-Datei.
            Returns:
            Optional[Path]: Der Pfad zur gespeicherten Datei oder None,
            wenn der Benutzer abbricht
        """
        root = tk.Tk()
        root.withdraw()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"SFPO_Arbeitsintervalle_{timestamp}.xlsx"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=default_filename,
            filetypes=[("Excel files", "*.xlsx")],
            title="Speicherort für Arbeitsintervall-Datei wählen"
        )

        if file_path:
            # Erstelle Dictionary für DataFrame
            data = {}
            for name, analyzer in self.interval_data.items():
                data[name] = analyzer.mean_normed_intervals

            # Erstelle DataFrame mit beschrifteten Zeilen
            df = pd.DataFrame(data)
            df.index = [f"Intervall {i + 1}" for i in range(10)]

            # Speichere mit Zeilenüberschriften
            df.to_excel(file_path)
            return Path(file_path)
        return None