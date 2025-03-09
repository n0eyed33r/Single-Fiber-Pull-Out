"""
this code was made with the help of chatgpt, claude, gemini, stackoverflow .... u name it
"""
# src/core/excel_exporter.py
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
from src.core.data_statistics import MeasurementAnalyzer
from typing import Optional
import logging
import os


class ExcelExporter:
    def __init__(self, logger=None):
        """
        Initialisiert den ExcelExporter mit einem optionalen Logger.

        Args:
            logger: Logger-Instanz für Protokollierung (optional)
        """
        # Logger initialisieren
        self.logger = logger or logging.getLogger('SFPO_Analyzer')

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
        """
        Fügt Ergebnisse einer Messreihe hinzu und speichert den Analyzer für Intervalldaten.

        Args:
            name: Name der Messreihe
            analyzer: MeasurementAnalyzer-Instanz mit den Analyseergebnissen
        """
        if analyzer:
            try:
                # Hauptergebnisse hinzufügen
                self.results['Probenname'].append(name)

                # Füge Daten mit Fehlerprüfung hinzu
                self._add_result_safely('forces', 'F_max [N]', 'F_max_std [N]', name, analyzer)
                self._add_result_safely('lengths', 'Einbettlänge [µm]', 'Einbettlänge_std [µm]', name, analyzer)
                self._add_result_safely('ifss', 'IFSS [MPa]', 'IFSS_std [MPa]', name, analyzer)
                self._add_result_safely('works', 'Arbeit [µJ]', 'Arbeit_std [µJ]', name, analyzer)
                self._add_result_safely('force_modulus', 'Force Modulus [N/µm]', 'Force Modulus_std [N/µm]', name, analyzer)

                # Analyzer für Intervalldaten speichern
                self.interval_data[name] = analyzer

            except Exception as e:
                # Bei Fehlern diesen Eintrag überspringen, aber protokollieren
                self.logger.error(f"Fehler beim Hinzufügen der Messreihe {name}: {str(e)}")
                # Spalten wieder entfernen, falls sie bereits hinzugefügt wurden
                if name in self.results['Probenname']:
                    idx = self.results['Probenname'].index(name)
                    for key in self.results:
                        if len(self.results[key]) > idx:
                            self.results[key].pop(idx)

    def _add_result_safely(self, data_type: str, mean_col: str, std_col: str, name: str, analyzer: 'MeasurementAnalyzer'):
        """
        Fügt Mittelwert und Standardabweichung für einen bestimmten Datentyp sicher hinzu.

        Args:
            data_type: Typ der Daten (z.B. 'forces', 'works')
            mean_col: Spaltenname für den Mittelwert
            std_col: Spaltenname für die Standardabweichung
            name: Name der Messreihe
            analyzer: MeasurementAnalyzer-Instanz
        """
        try:
            self.results[mean_col].append(analyzer.calculate_mean(data_type))
            self.results[std_col].append(analyzer.calculate_stddev(data_type))
        except Exception as e:
            self.logger.warning(f"Konnte {data_type} für {name} nicht berechnen: {e}")
            self.results[mean_col].append(0.0)
            self.results[std_col].append(0.0)

    def save_to_excel(self) -> Optional[Path]:
        """
        Speichert die Hauptergebnisse in einer Excel-Datei.

        Returns:
            Optional[Path]: Der Pfad zur gespeicherten Datei oder None, wenn der Benutzer abbricht
        """
        # Prüfe, ob Daten vorhanden sind
        if not self.results['Probenname']:
            self.logger.warning("Keine Ergebnisse zum Speichern vorhanden")
            return None

        # In Tkinter: Stelle sicher, dass ein Root-Fenster existiert und im Vordergrund ist
        root = tk.Tk()
        root.withdraw()
        root.lift()
        root.attributes('-topmost', True)
        root.focus_force()  # Forciere den Fokus auf dieses Fenster

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"SFPO_Ergebnisse_{timestamp}.xlsx"

        # Setze den Dialog explizit in den Vordergrund
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=default_filename,
            filetypes=[("Excel files", "*.xlsx")],
            title="Speicherort für Hauptergebnis-Datei wählen",
            parent=root  # Verknüpfe mit dem Root-Fenster
        )

        if not file_path:
            self.logger.info("Excel-Export abgebrochen")
            root.destroy()  # Wichtig: Root-Fenster explizit zerstören
            return None

        try:
            self.logger.info(f"Excel-Datei wird gespeichert: {file_path}")

            # Erstelle DataFrame
            df = pd.DataFrame(self.results)

            # Prüfe, ob Verzeichnis existiert
            save_dir = os.path.dirname(file_path)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir)

            # Speichere mit ExcelWriter für mehr Kontrolle
            with pd.ExcelWriter(file_path) as writer:
                df.to_excel(writer, sheet_name='Ergebnisse', index=False)

                # Füge ein Informationsblatt hinzu
                info_df = pd.DataFrame({
                    'Info': ['SFPO-Analyzer Ergebnisse'],
                    'Datum': [datetime.now().strftime("%d.%m.%Y %H:%M:%S")]
                })
                info_df.to_excel(writer, sheet_name='Info', index=False)

            self.logger.info(f"Excel-Datei erfolgreich gespeichert: {file_path}")
            root.destroy()  # Wichtig: Root-Fenster explizit zerstören
            return Path(file_path)

        except PermissionError:
            self.logger.error(f"Keine Berechtigung zum Speichern der Datei: {file_path}")
            self.logger.info("Bitte stellen Sie sicher, dass die Datei nicht bereits geöffnet ist.")
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern der Excel-Datei: {str(e)}")
            import traceback
            self.logger.debug(traceback.format_exc())

        root.destroy()  # Wichtig: Root-Fenster explizit zerstören auch im Fehlerfall
        return None

    def save_work_intervals_to_excel(self) -> Optional[Path]:
        """
        Speichert die Arbeitsintervalle in einer separaten Excel-Datei.

        Returns:
            Optional[Path]: Der Pfad zur gespeicherten Datei oder None, wenn der Benutzer abbricht
                            oder keine Daten vorhanden sind
        """
        # Prüfe, ob überhaupt Daten vorhanden sind
        if not self.interval_data:
            self.logger.warning("Keine Intervalldaten zum Speichern vorhanden")
            return None

        # Prüfe, ob die Daten gültig sind
        data = {}
        for name, analyzer in self.interval_data.items():
            if hasattr(analyzer, 'mean_normed_intervals') and analyzer.mean_normed_intervals:
                data[name] = analyzer.mean_normed_intervals

        if not data:
            self.logger.warning("Keine gültigen Intervalldaten zum Speichern vorhanden")
            return None

        # Fahre mit Dialog fort, wenn Daten vorhanden sind
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

        if not file_path:
            return None

        try:
            # Excel Writer erstellen
            with pd.ExcelWriter(file_path) as writer:
                # Immer ein Info-Sheet erstellen, um sicherzustellen, dass mindestens ein Sheet existiert
                pd.DataFrame({'Info': ['SFPO-Analyzer Arbeitsintervalle']}).to_excel(
                    writer, sheet_name='Info', index=False
                )

                # Erstes Sheet: Arbeitsintervalle
                df = pd.DataFrame(data)

                # Nur wenn der DataFrame nicht leer ist, Index setzen und speichern
                if not df.empty:
                    # Stelle sicher, dass wir 10 Intervalle haben (oder passe an die tatsächliche Anzahl an)
                    num_intervals = min(10, len(next(iter(data.values()))) if data else 0)
                    df.index = [f"Intervall {i + 1}" for i in range(num_intervals)]
                    df.to_excel(writer, sheet_name='Arbeitsintervalle')

                # Zweites Sheet: Normierte Intervalle mit Standardabweichungen
                normed_data = {}
                for name, analyzer in self.interval_data.items():
                    if (hasattr(analyzer, 'mean_normed_intervals') and
                            hasattr(analyzer, 'stddev_normed_intervals') and
                            analyzer.mean_normed_intervals and
                            analyzer.stddev_normed_intervals):
                        # Für jeden Probennamen zwei Spalten: Wert und Standardabweichung
                        normed_data[f"{name}"] = analyzer.mean_normed_intervals
                        normed_data[f"{name}_std"] = analyzer.stddev_normed_intervals

                # Nur wenn normierte Daten vorhanden sind
                if normed_data:
                    normed_df = pd.DataFrame(normed_data)
                    num_intervals = min(10, len(next(iter(normed_data.values()))) if normed_data else 0)
                    normed_df.index = [f"Intervall {i + 1}" for i in range(num_intervals)]
                    normed_df.to_excel(writer, sheet_name='Normierte Intervalle')

                # Drittes Sheet: Kumulative Daten
                cum_data = {}

                for name, analyzer in self.interval_data.items():
                    if hasattr(analyzer, 'get_cumulative_normed_work_statistics'):
                        try:
                            # Verwende die Methode, wenn sie existiert
                            stats = analyzer.get_cumulative_normed_work_statistics()

                            if stats:  # Nur wenn Daten zurückgegeben wurden
                                for position, values in stats.items():
                                    col_mean = f"{name}_{position}_mean"
                                    col_std = f"{name}_{position}_std"

                                    if 'cum_data_means' not in locals():
                                        cum_data_means = {}
                                        cum_data_stds = {}

                                    cum_data_means[position] = values.get('mean', 0)
                                    cum_data_stds[position] = values.get('std', 0)

                                if 'cum_data_means' in locals() and cum_data_means:
                                    means_df = pd.DataFrame(cum_data_means, index=[name])
                                    stds_df = pd.DataFrame(cum_data_stds, index=[f"{name}_std"])

                                    cum_df = pd.concat([means_df, stds_df])
                                    cum_df.to_excel(writer, sheet_name='Kumulative Daten')
                        except Exception as e:
                            self.logger.warning(f"Fehler bei kumulativen Daten für {name}: {str(e)}")

            self.logger.info(f"Arbeitsintervalle erfolgreich gespeichert: {file_path}")
            return Path(file_path)

        except Exception as e:
            self.logger.error(f"Fehler beim Speichern der Arbeitsintervalle: {str(e)}")
            import traceback
            self.logger.debug(traceback.format_exc())

            # Falls die Datei teilweise erstellt wurde, lösche sie
            try:
                if Path(file_path).exists():
                    Path(file_path).unlink()
            except Exception:
                pass

        return None

    def save_boxplot_data_to_excel(self) -> Optional[Path]:
        """
        Speichert die Boxplot-Daten (F_max und Arbeit) in einer Excel-Datei.

        Returns:
            Optional[Path]: Der Pfad zur gespeicherten Datei oder None, wenn der Benutzer abbricht
                            oder keine Daten vorhanden sind
        """
        # Prüfe, ob überhaupt Daten vorhanden sind
        if not self.interval_data:
            self.logger.warning("Keine Analyzer-Daten für Boxplots vorhanden")
            return None

        # Prüfe, ob die Daten valid sind
        fmax_data = {}
        work_data = {}

        for name, analyzer in self.interval_data.items():
            if hasattr(analyzer, 'max_forces_data') and analyzer.max_forces_data:
                fmax_data[name] = pd.Series(analyzer.max_forces_data)

            if hasattr(analyzer, 'works') and analyzer.works:
                work_data[name] = pd.Series(analyzer.works)

        if not fmax_data and not work_data:
            self.logger.warning("Keine gültigen Daten für Boxplots vorhanden")
            return None

        # Fahre mit Dialog fort, wenn Daten vorhanden sind
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

        if not file_path:
            return None

        try:
            # Sicherstellen, dass wir ein leeres Excel-Blatt erstellen, falls keine Daten
            # für bestimmte Sheets vorhanden sind
            with pd.ExcelWriter(file_path) as writer:
                # Stelle sicher, dass mindestens ein Sheet immer erstellt wird
                pd.DataFrame({'Info': ['SFPO-Analyzer Boxplot-Daten']}).to_excel(
                    writer, sheet_name='Info', index=False
                )
                sheets_written = 1  # Zähler für erstellte Sheets

                # Sheet für F_max Daten
                if fmax_data:
                    df_fmax = pd.DataFrame(fmax_data)

                    if not df_fmax.empty:
                        # Korrigierte Version: Iteration über die Series-Objekte im Dictionary
                        max_rows = max(len(series) for series in fmax_data.values())
                        df_fmax.index = [f"Messung {i + 1}" for i in range(max_rows)]
                        df_fmax.to_excel(writer, sheet_name='F_max Werte')
                        sheets_written += 1

                        # Statistiken für F_max hinzufügen
                        stats_fmax_data = {}

                        for name, data in fmax_data.items():
                            # Nur Statistiken berechnen, wenn Daten vorhanden sind
                            if len(data) > 0:
                                stats_fmax_data[name] = {
                                    'Mittelwert': np.mean(data),
                                    'Standardabweichung': np.std(data),
                                    'Minimum': np.min(data),
                                    'Q1': np.percentile(data, 25) if len(data) >= 4 else np.min(data),
                                    'Median': np.median(data),
                                    'Q3': np.percentile(data, 75) if len(data) >= 4 else np.max(data),
                                    'Maximum': np.max(data)
                                }
                            else:
                                # Platzhalter-Daten für leere Series
                                stats_fmax_data[name] = {
                                    'Mittelwert': 0,
                                    'Standardabweichung': 0,
                                    'Minimum': 0,
                                    'Q1': 0,
                                    'Median': 0,
                                    'Q3': 0,
                                    'Maximum': 0
                                }

                        if stats_fmax_data:
                            stats_df = pd.DataFrame(stats_fmax_data).T
                            stats_df.to_excel(writer, sheet_name='F_max Statistiken')
                            sheets_written += 1

                # Sheet für Arbeitsdaten
                if work_data:
                    df_work = pd.DataFrame(work_data)

                    if not df_work.empty:
                        # Korrigierte Version: Iteration über die Series-Objekte im Dictionary
                        max_rows = max(len(series) for series in work_data.values())
                        df_work.index = [f"Messung {i + 1}" for i in range(max_rows)]
                        df_work.to_excel(writer, sheet_name='Arbeit Werte')
                        sheets_written += 1

                        # Statistiken für Arbeit hinzufügen
                        stats_work_data = {}

                        for name, data in work_data.items():
                            # Nur Statistiken berechnen, wenn Daten vorhanden sind
                            if len(data) > 0:
                                stats_work_data[name] = {
                                    'Mittelwert': np.mean(data),
                                    'Standardabweichung': np.std(data),
                                    'Minimum': np.min(data),
                                    'Q1': np.percentile(data, 25) if len(data) >= 4 else np.min(data),
                                    'Median': np.median(data),
                                    'Q3': np.percentile(data, 75) if len(data) >= 4 else np.max(data),
                                    'Maximum': np.max(data)
                                }
                            else:
                                # Platzhalter-Daten für leere Series
                                stats_work_data[name] = {
                                    'Mittelwert': 0,
                                    'Standardabweichung': 0,
                                    'Minimum': 0,
                                    'Q1': 0,
                                    'Median': 0,
                                    'Q3': 0,
                                    'Maximum': 0
                                }

                        if stats_work_data:
                            stats_df = pd.DataFrame(stats_work_data).T
                            stats_df.to_excel(writer, sheet_name='Arbeit Statistiken')
                            sheets_written += 1

            self.logger.info(f"Boxplot-Daten erfolgreich gespeichert: {file_path}")
            return Path(file_path)

        except Exception as e:
            self.logger.error(f"Fehler beim Speichern der Boxplot-Daten: {str(e)}")
            import traceback
            self.logger.debug(traceback.format_exc())  # Detaillierte Fehlerinformation

            # Falls die Datei teilweise erstellt wurde, lösche sie
            try:
                if Path(file_path).exists():
                    Path(file_path).unlink()
            except Exception:
                pass

        return None