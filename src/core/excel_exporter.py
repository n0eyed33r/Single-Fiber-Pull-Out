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
    def __init__(self, output_folder: Optional[Path] = None):
        """
        Initialisiert den ExcelExporter mit einem optionalen Ausgabeordner.

        Args:
            output_folder: Ordner, in dem alle Excel-Dateien gespeichert werden sollen.
                           Falls None, wird für jede Datei ein Dialog angezeigt.
        """
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
            'Force Modulus_std [N/µm]': [],
            'Flächennormierte Arbeit [µJ/µm²]': [],
            'Flächennormierte Arbeit_std [µJ/µm²]': []
        }
        # Dictionary für Arbeitsintervalle: {Probenname: Analyzer}
        self.interval_data = {}
        # Speicherort für Ausgabedateien
        self.output_folder = output_folder
    
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
            
            # Flächennormierte Arbeitswerte prüfen und hinzufügen
            print(f"\nFüge flächennormierte Arbeitsdaten für Messreihe '{name}' hinzu:")
            if hasattr(analyzer, 'area_normalized_works') and analyzer.area_normalized_works:
                # Prüfe, ob gültige Werte enthalten sind (nicht NaN)
                valid_data = [x for x in analyzer.area_normalized_works if not np.isnan(x)]
                
                if valid_data:
                    print(f"  {len(valid_data)} gültige Werte gefunden")
                    self.results['Flächennormierte Arbeit [µJ/µm²]'].append(
                        analyzer.calculate_mean('area_normalized_works'))
                    self.results['Flächennormierte Arbeit_std [µJ/µm²]'].append(
                        analyzer.calculate_stddev('area_normalized_works'))
                else:
                    print("  Keine gültigen Werte gefunden, füge NaN ein")
                    self.results['Flächennormierte Arbeit [µJ/µm²]'].append(np.nan)
                    self.results['Flächennormierte Arbeit_std [µJ/µm²]'].append(np.nan)
            else:
                # Wenn keine Daten vorhanden sind, füge NaN hinzu
                print("  Keine flächennormierten Arbeitsdaten vorhanden, füge NaN ein")
                self.results['Flächennormierte Arbeit [µJ/µm²]'].append(np.nan)
                self.results['Flächennormierte Arbeit_std [µJ/µm²]'].append(np.nan)
            
            # Analyzer für Intervalldaten speichern
            self.interval_data[name] = analyzer
    
    def _get_file_path(self, default_filename: str, title: str, use_dialog: bool = True) -> Optional[Path]:
        """
        Bestimmt den Speicherpfad für eine Excel-Datei.
        Wenn output_folder gesetzt ist, wird die Datei dort gespeichert ohne Dialog anzuzeigen.
        Ansonsten wird ein Dateiauswahldialog angezeigt.

        Args:
            default_filename: Standarddateiname für die Excel-Datei
            title: Titel für den Dateiauswahldialog
            use_dialog: Wenn True, wird immer ein Dialog angezeigt, unabhängig von output_folder

        Returns:
            Path-Objekt für die Datei oder None, wenn abgebrochen wurde
        """
        # Wenn kein Ausgabeordner gesetzt ist oder Dialog erzwungen wird, Dialog anzeigen
        if self.output_folder is None or use_dialog:
            root = tk.Tk()
            root.withdraw()
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=default_filename,
                filetypes=[("Excel files", "*.xlsx")],
                title=title
            )
            
            if not file_path:
                return None
            
            return Path(file_path)
        else:
            # Direkter Pfad im output_folder
            file_path = self.output_folder / default_filename
            
            # Stelle sicher, dass der Ausgabeordner existiert
            self.output_folder.mkdir(exist_ok=True, parents=True)
            
            # Information für den Benutzer
            print(f"Datei wird automatisch gespeichert unter: {file_path}")
            
            return file_path
    
    def save_to_excel(self, use_dialog: bool = False) -> Optional[Path]:
        """
        Speichert die Hauptergebnisse in einer Excel-Datei.

        Args:
            use_dialog: Wenn True, wird immer ein Dialog angezeigt, unabhängig von output_folder

        Returns:
            Optional[Path]: Der Pfad zur gespeicherten Datei oder None, wenn der Benutzer abbricht
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"SFPO_Ergebnisse_{timestamp}.xlsx"
        
        file_path = self._get_file_path(default_filename, "Speicherort für Hauptergebnis-Datei wählen", use_dialog)
        
        if file_path:
            df = pd.DataFrame(self.results)
            df.to_excel(file_path, index=False)
            return file_path
        return None
    
    def save_work_intervals_to_excel(self, use_dialog: bool = False) -> Optional[Path]:
        """
        Speichert die Arbeitsintervalle in einer separaten Excel-Datei.

        Args:
            use_dialog: Wenn True, wird immer ein Dialog angezeigt, unabhängig von output_folder

        Returns:
            Optional[Path]: Der Pfad zur gespeicherten Datei oder None, wenn der Benutzer abbricht
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"SFPO_Arbeitsintervalle_{timestamp}.xlsx"
        
        file_path = self._get_file_path(default_filename, "Speicherort für Arbeitsintervall-Datei wählen", use_dialog)
        
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
                
                return file_path
        return None
    
    def save_boxplot_data_to_excel(self, use_dialog: bool = False) -> Optional[Path]:
        """
        Speichert die Boxplot-Daten (F_max, Arbeit, IFSS, flächennormierte Arbeit) in einer Excel-Datei.

        Args:
            use_dialog: Wenn True, wird immer ein Dialog angezeigt, unabhängig von output_folder

        Returns:
            Optional[Path]: Der Pfad zur gespeicherten Datei oder None, wenn der Benutzer abbricht
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"SFPO_Boxplot_Daten_{timestamp}.xlsx"
        
        file_path = self._get_file_path(default_filename, "Speicherort für Boxplot-Daten wählen", use_dialog)
        
        if file_path:
            with pd.ExcelWriter(file_path) as writer:
                # 1. Sheet für F_max Daten
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
                
                # 2. Sheet für Arbeitsdaten
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
                
                # 3. Sheet für IFSS-Daten
                ifss_data = {}
                for name, analyzer in self.interval_data.items():
                    ifss_data[name] = pd.Series(analyzer.ifssvalues)
                
                df_ifss = pd.DataFrame(ifss_data)
                df_ifss.index = [f"Messung {i + 1}" for i in range(len(df_ifss))]
                
                # Statistiken für IFSS hinzufügen
                stats_ifss = pd.DataFrame({
                    name: {
                        'Mittelwert': np.mean(data),
                        'Standardabweichung': np.std(data),
                        'Minimum': np.min(data),
                        'Q1': np.percentile(data, 25),
                        'Median': np.median(data),
                        'Q3': np.percentile(data, 75),
                        'Maximum': np.max(data)
                    }
                    for name, data in ifss_data.items()
                }).T  # Transponieren für bessere Lesbarkeit
                
                # IFSS-Daten und Statistiken in separaten Sheets speichern
                df_ifss.to_excel(writer, sheet_name='IFSS Werte')
                stats_ifss.to_excel(writer, sheet_name='IFSS Statistiken')
                
                # 4. Sheet für flächennormierte Arbeitsdaten
                area_norm_work_data = {}
                for name, analyzer in self.interval_data.items():
                    if hasattr(analyzer, 'area_normalized_works') and analyzer.area_normalized_works:
                        area_norm_work_data[name] = pd.Series(analyzer.area_normalized_works)
                
                if area_norm_work_data:
                    df_area_norm = pd.DataFrame(area_norm_work_data)
                    df_area_norm.index = [f"Messung {i + 1}" for i in range(len(df_area_norm))]
                    
                    # Statistiken für flächennormierte Arbeit hinzufügen
                    stats_area_norm = pd.DataFrame({
                        name: {
                            'Mittelwert': np.mean(data),
                            'Standardabweichung': np.std(data),
                            'Minimum': np.min(data),
                            'Q1': np.percentile(data, 25),
                            'Median': np.median(data),
                            'Q3': np.percentile(data, 75),
                            'Maximum': np.max(data)
                        }
                        for name, data in area_norm_work_data.items()
                    }).T  # Transponieren für bessere Lesbarkeit
                    
                    # Flächennormierte Arbeitsdaten und Statistiken in separaten Sheets speichern
                    df_area_norm.to_excel(writer, sheet_name='Flächennorm. Arbeit Werte')
                    stats_area_norm.to_excel(writer, sheet_name='Flächennorm. Arbeit Stat.')
                
                return file_path
        return None
    
    def save_area_normalized_work_to_excel(self, use_dialog: bool = False) -> Optional[Path]:
        """
        Speichert die flächennormierten Arbeitsdaten in einer separaten Excel-Datei.

        Args:
            use_dialog: Wenn True, wird immer ein Dialog angezeigt, unabhängig von output_folder

        Returns:
            Optional[Path]: Der Pfad zur gespeicherten Datei oder None, wenn der Benutzer abbricht
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"SFPO_Flächennormierte_Arbeit_{timestamp}.xlsx"
        
        file_path = self._get_file_path(default_filename, "Speicherort für flächennormierte Arbeitsdaten wählen",
                                        use_dialog)
        
        if file_path:
            # Sammle alle flächennormierten Arbeitsdaten
            area_norm_work_data = {}
            for name, analyzer in self.interval_data.items():
                if hasattr(analyzer, 'area_normalized_works') and analyzer.area_normalized_works:
                    area_norm_work_data[name] = pd.Series(analyzer.area_normalized_works)
            
            if not area_norm_work_data:
                print("Keine flächennormierten Arbeitsdaten zum Exportieren vorhanden")
                return None
            
            with pd.ExcelWriter(file_path) as writer:
                # Hauptdaten
                df = pd.DataFrame(area_norm_work_data)
                df.index = [f"Messung {i + 1}" for i in range(len(df))]
                df.to_excel(writer, sheet_name='Einzelwerte')
                
                # Statistische Daten
                stats_df = pd.DataFrame({
                    name: {
                        'Anzahl': len(data),
                        'Mittelwert': np.mean(data),
                        'Standardabweichung': np.std(data),
                        'Variationskoeffizient [%]': (np.std(data) / np.mean(data) * 100) if np.mean(data) != 0 else 0,
                        'Minimum': np.min(data),
                        'Q1 (25%)': np.percentile(data, 25),
                        'Median': np.median(data),
                        'Q3 (75%)': np.percentile(data, 75),
                        'Maximum': np.max(data)
                    }
                    for name, data in area_norm_work_data.items()
                }).T  # Transponieren für bessere Lesbarkeit
                
                stats_df.to_excel(writer, sheet_name='Statistik')
                
                # Zusammenfassung für schnellen Überblick
                summary_data = []
                for name, data in area_norm_work_data.items():
                    summary_data.append({
                        'Probenname': name,
                        'Mittelwert [µJ/µm²]': np.mean(data),
                        'Standardabweichung [µJ/µm²]': np.std(data),
                        'Anzahl der Messungen': len(data)
                    })
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Zusammenfassung', index=False)
                
                return file_path
        return None