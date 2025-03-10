# src/core/excel_exporter.py
import pandas as pd
import numpy as np
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
            'Arbeit_std [µJ]': [],
            'Force Modulus [N/µm]': [],
            'Force Modulus_std [N/µm]': []
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
            self.results['Force Modulus [N/µm]'].append(analyzer.calculate_mean('force_modulus'))
            self.results['Force Modulus_std [N/µm]'].append(analyzer.calculate_stddev('force_modulus'))

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
            # Excel Writer erstellen
            with pd.ExcelWriter(file_path) as writer:
                # Erstes Sheet: Bisherige Arbeitsintervalle
                data = {}
                for name, analyzer in self.interval_data.items():
                    data[name] = analyzer.mean_normed_intervals
                df = pd.DataFrame(data)
                df.index = [f"Intervall {i + 1}" for i in range(10)]
                df.to_excel(writer, sheet_name='Arbeitsintervalle')

                # Zweites Sheet: Normierte Intervalle mit Standardabweichungen
                normed_data = {}
                for name, analyzer in self.interval_data.items():
                    # Für jeden Probennamen zwei Spalten: Wert und Standardabweichung
                    normed_data[f"{name}"] = analyzer.mean_normed_intervals
                    normed_data[f"{name}_std"] = analyzer.stddev_normed_intervals

                normed_df = pd.DataFrame(normed_data)
                normed_df.index = [f"Intervall {i + 1}" for i in range(10)]
                normed_df.to_excel(writer, sheet_name='Normierte Intervalle')

                return Path(file_path)
        return None

    def save_boxplot_data_to_excel(self) -> Optional[Path]:
        """Speichert die Boxplot-Daten (F_max und Arbeit) in einer Excel-Datei."""
        root = tk.Tk()
        root.withdraw()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"SFPO_Boxplot_Daten_{timestamp}.xlsx"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=default_filename,
            filetypes=[("Excel files", "*.xlsx")],
            title="Speicherort für Boxplot-Daten wählen"
        )

        if file_path:
            with pd.ExcelWriter(file_path) as writer:
                # Sheet für F_max Daten
                fmax_data = {}
                for name, analyzer in self.interval_data.items():
                    fmax_data[name] = pd.Series(analyzer.max_forces_data)

                df_fmax = pd.DataFrame(fmax_data)
                df_fmax.index = [f"Messung {i + 1}" for i in range(len(df_fmax))]

                # Statistiken für F_max hinzufügen
                stats_fmax = pd.DataFrame({
                    name: {
                        'Mittelwert': np.mean(data),
                        'Standardabweichung': np.std(data),
                        'Minimum': np.min(data),
                        'Q1': np.percentile(data, 25),
                        'Median': np.median(data),
                        'Q3': np.percentile(data, 75),
                        'Maximum': np.max(data)
                    }
                    for name, data in fmax_data.items()
                }).T  # Transponieren für bessere Lesbarkeit

                # F_max Daten und Statistiken in separaten Sheets speichern
                df_fmax.to_excel(writer, sheet_name='F_max Werte')
                stats_fmax.to_excel(writer, sheet_name='F_max Statistiken')

                # Sheet für Arbeitsdaten
                work_data = {}
                for name, analyzer in self.interval_data.items():
                    work_data[name] = pd.Series(analyzer.works)

                df_work = pd.DataFrame(work_data)
                df_work.index = [f"Messung {i + 1}" for i in range(len(df_work))]

                # Statistiken für Arbeit hinzufügen
                stats_work = pd.DataFrame({
                    name: {
                        'Mittelwert': np.mean(data),
                        'Standardabweichung': np.std(data),
                        'Minimum': np.min(data),
                        'Q1': np.percentile(data, 25),
                        'Median': np.median(data),
                        'Q3': np.percentile(data, 75),
                        'Maximum': np.max(data)
                    }
                    for name, data in work_data.items()
                }).T  # Transponieren für bessere Lesbarkeit

                # Arbeitsdaten und Statistiken in separaten Sheets speichern
                df_work.to_excel(writer, sheet_name='Arbeit Werte')
                stats_work.to_excel(writer, sheet_name='Arbeit Statistiken')

                return Path(file_path)
        return None
        
    def export_anova_results(self, anova_results, output_path=None):
        """
        Exportiert die Ergebnisse der ANOVA-Analyse in eine Excel-Datei.
        
        Args:
            anova_results: Dictionary mit ANOVA-Ergebnissen
            output_path: Optionaler Pfad für die Ausgabedatei
        
        Returns:
            Path: Pfad zur erstellten Excel-Datei
        """
        import pandas as pd
        from pathlib import Path
        import tkinter as tk
        from tkinter import filedialog
        from datetime import datetime
        
        if output_path is None:
            # Dialog zur Dateiauswahl anzeigen
            root = tk.Tk()
            root.withdraw()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"SFPO_ANOVA_Ergebnisse_{timestamp}.xlsx"
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=default_filename,
                filetypes=[("Excel files", "*.xlsx")],
                title="Speicherort für ANOVA-Ergebnisse wählen"
            )
            
            if not file_path:
                print("Export abgebrochen")
                return None
            
            output_path = Path(file_path)
        
        # Excel-Writer erstellen
        with pd.ExcelWriter(output_path) as writer:
            # Hauptergebnisse der ANOVA
            main_results = []
            
            for data_type, results in anova_results.items():
                if 'error' in results:
                    # Fehlerfall
                    row = {
                        'Datentyp': data_type,
                        'F-Wert': None,
                        'p-Wert': None,
                        'Signifikant': None,
                        'Fehler': results['error']
                    }
                else:
                    # Erfolgsfall
                    row = {
                        'Datentyp': data_type,
                        'F-Wert': results['f_value'],
                        'p-Wert': results['p_value'],
                        'Signifikant': 'Ja' if results['significant'] else 'Nein'
                    }
                main_results.append(row)
            
            # Erstelle DataFrame für die Hauptergebnisse
            main_df = pd.DataFrame(main_results)
            main_df.to_excel(writer, sheet_name='ANOVA_Zusammenfassung', index=False)
            
            # Detaillierte Ergebnisse pro Datentyp in separaten Sheets
            for data_type, results in anova_results.items():
                if 'error' in results:
                    continue
                
                # Gruppenmittelwerte und Standardabweichungen
                if 'group_means' in results:
                    group_data = []
                    for group_name in results['group_means'].keys():
                        row = {
                            'Gruppe': group_name,
                            'Mittelwert': results['group_means'][group_name],
                            'Standardabweichung': results['group_std'][group_name]
                        }
                        group_data.append(row)
                    
                    group_df = pd.DataFrame(group_data)
                    group_df.to_excel(writer, sheet_name=f'{data_type}_Gruppen', index=False)
                
                # Tukey-Ergebnisse, falls vorhanden
                if 'tukey_results' in results:
                    tukey_df = pd.DataFrame(results['tukey_results'])
                    tukey_df.columns = ['Gruppe 1', 'Gruppe 2', 'Mittlere Differenz', 
                                        'p-Wert', 'Untere Grenze', 'Obere Grenze', 
                                        'Signifikant']
                    tukey_df.to_excel(writer, sheet_name=f'{data_type}_Tukey', index=False)
        
        print(f"ANOVA-Ergebnisse gespeichert: {output_path}")
        return output_path