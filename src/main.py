"""
Hauptmodul der SFPO-Analyzer Anwendung zur Steuerung des Analyseprozesses
und Koordination der verschiedenen Komponenten.
"""

import sys
from pathlib import Path
from tkinter import messagebox
from typing import Dict, Optional
import numpy as np

# Eigene Module importieren
from src.config.config_manager import app_config
from src.core.file_handler import FileHandler
from src.core.data_sorter import DataSorter
from src.core.data_statistics import MeasurementAnalyzer
from src.core.data_plotting import DataPlotter
from src.core.excel_exporter import ExcelExporter
from src.utils.logger_setup import LoggerSetup
from src.utils.debug_printer import DebugPrinter


class SFPOAnalyzer:
    """
    Hauptklasse der Anwendung, die den gesamten Analyse-Workflow steuert.
    """
    
    def __init__(self):
        """Initialisiert die Anwendung und richtet den Logger ein."""
        # Logger einrichten
        self.logger = LoggerSetup.setup_logger()
        self.logger.info("=== SFPO-Analyzer gestartet ===")
        
        # Komponenten initialisieren
        self.file_handler = FileHandler(self.logger)
        self.data_sorter = DataSorter(self.logger)
        self.data_plotter = DataPlotter(self.logger)
        self.excel_exporter = ExcelExporter(self.logger)
        self.debug_printer = DebugPrinter()
        
        # Speicher für Analyzer-Objekte
        self.analyzers: Dict[str, MeasurementAnalyzer] = {}
        
        # Statistische Analyse
        self.statistical_analyzer = None
        
        # Analysekonfiguration
        self.use_bootstrap = False
        self.anova_groups = {}
    
    def run(self):
        """Führt den Hauptablauf der Anwendung aus."""
        try:
            # Analysetyp wählen
            analysis_type = self.file_handler.select_analysis_type()
            
            # Welche Analysen sollen durchgeführt werden
            analysis_options = self.file_handler.select_analysis_types()
            
            # Update der Analysekonfiguration
            for key, value in analysis_options.items():
                setattr(app_config.analysis, key, value)
            
            # Bootstrap-Option abfragen
            self.use_bootstrap = self.file_handler.select_bootstrap_option()
            
            if analysis_type == "1":
                # Einzelne Messreihe analysieren
                self.analyze_single_series()
            elif analysis_type == "2":
                # Alle Messreihen im Ordner analysieren
                self.analyze_all_series()
                
                # ANOVA-Gruppenanalyse, wenn mehr als eine Messreihe vorhanden ist
                if len(self.analyzers) > 1:
                    self.perform_group_analysis()
            else:
                self.logger.error(f"Ungültiger Analysetyp: {analysis_type}")
                return
            
            # Export durchführen
            if app_config.analysis.export_to_excel:
                self.export_results()
            
            self.logger.info("=== Analyse abgeschlossen ===")
        
        except Exception as e:
            self.logger.error(f"Fehler in der Hauptanwendung: {e}", exc_info=True)
            messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten: {str(e)}")
        finally:
            # Abschließende Meldung
            self.logger.info("SFPO-Analyzer wird beendet.")
    
    def analyze_single_series(self):
        """Analysiert eine einzelne Messreihe."""
        # Ordner auswählen
        folder_path = self.file_handler.select_folder("1")
        if not folder_path:
            self.logger.info("Ordnerauswahl abgebrochen")
            return
        
        # Dateien finden und sortieren
        self.file_handler.find_specimen_files()
        successful, failed = self.data_sorter.analyze_filenames()
        
        # Pull-Out Verhältnis berechnen
        ratio = self.data_sorter.calculate_pullout_ratio()
        self.logger.info(f"Pull-Out Verhältnis: {ratio:.2f}")
        
        # Analyzer erstellen und Messungen lesen
        analyzer = self.create_analyzer(folder_path.name)
        if not analyzer:
            return
        
        # Speichern des Analyzers im Dictionary (wichtig für Bootstrap-Analyse)
        self.analyzers[folder_path.name] = analyzer
        
        # Ausgabeordner erstellen
        self.create_output_folders(folder_path)
        
        # Plots erstellen basierend auf Konfiguration
        self.create_plots(folder_path)
        
        # Bootstrap-Analyse, wenn gewünscht
        if self.use_bootstrap:
            self.perform_bootstrap_analysis(folder_path)
    
    def analyze_all_series(self):
        """Analysiert alle Messreihen in einem übergeordneten Ordner."""
        # Übergeordneten Ordner auswählen
        parent_folder = self.file_handler.select_folder("2")
        if not parent_folder:
            self.logger.info("Ordnerauswahl abgebrochen")
            return
        
        # Messreihenordner finden
        series_folders = self.file_handler.get_measurement_series_folders(parent_folder)
        if not series_folders:
            self.logger.warning("Keine Messreihen gefunden")
            return
        
        # Ausgabeordner erstellen
        plots_folder, boxplots_folder, violin_folder, zscore_folder = self.create_output_folders(parent_folder)
        
        # Jede Messreihe analysieren
        for folder in series_folders:
            try:
                self.logger.info(f"\n=== Analysiere Messreihe: {folder.name} ===")
                
                # Konfiguration zurücksetzen
                app_config.reset_for_new_series()
                app_config.paths.update_paths(folder)
                
                # Dateien finden und sortieren
                self.file_handler.find_specimen_files()
                successful, failed = self.data_sorter.analyze_filenames()
                
                # Pull-Out Verhältnis berechnen
                ratio = self.data_sorter.calculate_pullout_ratio()
                
                # Analyzer erstellen und Messungen lesen
                analyzer = self.create_analyzer(folder.name)
                if analyzer:
                    self.analyzers[folder.name] = analyzer
            
            except Exception as e:
                self.logger.error(f"Fehler bei Messreihe {folder.name}: {e}", exc_info=True)
        
        # Plots für alle Messreihen erstellen
        if self.analyzers:
            self.create_plots_for_all_series(parent_folder)
            
            # Bootstrap-Analyse für alle Messreihen, wenn gewünscht
            if self.use_bootstrap:
                self.perform_bootstrap_analysis(parent_folder)
        else:
            self.logger.warning("Keine Analyzer erstellt, überspringe Plot-Erstellung")
        
        # Speichere die Ordner für die spätere ANOVA-Analyse
        self.series_folders = series_folders
    
    def create_analyzer(self, name: str) -> Optional[MeasurementAnalyzer]:
        """Erstellt und konfiguriert einen MeasurementAnalyzer für eine Messreihe."""
        try:
            analyzer = MeasurementAnalyzer(self.logger)
            
            # Messungen einlesen
            analyzer.read_all_measurements()
            if not analyzer.measurements_data:
                self.logger.warning(f"Keine Messdaten für {name} gefunden")
                return None
            
            # Maximalkräfte und Einbettlängen finden
            analyzer.find_all_max_forces()
            analyzer.find_all_embeddinglengths()
            
            # Faserdurchmesser verarbeiten
            analyzer.process_all_fiberdiameters()
            
            # Konsistenzprüfung
            if not analyzer.check_data_consistency():
                self.logger.warning(f"Datenkonsistenz für {name} nicht erfüllt")
            
            # IFSS und Arbeit berechnen
            analyzer.interfaceshearstrength()
            analyzer.calculate_all_works()
            
            # Weitere Berechnungen basierend auf Konfiguration
            if app_config.analysis.calculate_work_intervals:
                analyzer.calculate_all_work_intervals()
                analyzer.calculate_normed_intervals()
                analyzer.calculate_interval_statistics()
            
            if app_config.analysis.calculate_force_moduli:
                analyzer.calculate_force_modulus()
            
            return analyzer
        
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen des Analyzers für {name}: {e}", exc_info=True)
            return None
    
    def create_output_folders(self, base_folder: Path) -> tuple:
        """Erstellt alle benötigten Ausgabeordner."""
        return self.file_handler.ensure_output_folders(base_folder)
    
    def create_plots(self, base_folder: Path):
        """Erstellt Plots basierend auf der Konfiguration."""
        plots_folder, boxplots_folder, violin_folder, zscore_folder = self.create_output_folders(base_folder)
        
        # Debug-Ausgabe der Plot-Konfiguration
        self.debug_printer.print_plot_config()
        
        # Standard Kraft-Weg-Diagramme
        if app_config.analysis.create_standard_plots:
            self.logger.info("Erstelle Standard Kraft-Weg-Diagramme...")
            DataPlotter.save_plots_for_series(self.analyzers, plots_folder)
        
        # Boxplots
        if app_config.analysis.create_boxplots:
            self.logger.info("Erstelle Boxplots...")
            DataPlotter.create_boxplots(self.analyzers, boxplots_folder)
        
        # Arbeitsintervall-Plots
        if app_config.analysis.create_work_interval_plots:
            self.logger.info("Erstelle Arbeitsintervall-Plots...")
            DataPlotter.create_work_interval_plots(self.analyzers, plots_folder)
        
        # Normierte Plots
        if app_config.analysis.create_normalized_plots:
            self.logger.info("Erstelle normierte Arbeits-Plots...")
            DataPlotter.create_normalized_plots(self.analyzers, plots_folder)
            DataPlotter.create_mean_normalized_plots(self.analyzers, plots_folder)
        
        # Violin-Plots
        if app_config.analysis.create_violin_plots:
            self.logger.info("Erstelle Violin-Plots...")
            DataPlotter.create_violin_plots(self.analyzers, violin_folder)
        
        # Z-Score Plots
        if app_config.analysis.create_zscore_plots:
            self.logger.info("Erstelle Z-Score Plots...")
            DataPlotter.create_z_score_plots(self.analyzers, zscore_folder)
    
    def create_plots_for_all_series(self, base_folder: Path):
        """Erstellt Plots für alle Messreihen zusammen."""
        plots_folder, boxplots_folder, violin_folder, zscore_folder = self.create_output_folders(base_folder)
        
        # Debug-Ausgabe der Plot-Konfiguration
        self.debug_printer.print_plot_config()
        
        # Plots erstellen basierend auf Konfiguration
        if app_config.analysis.create_standard_plots:
            self.logger.info("Erstelle Standard Kraft-Weg-Diagramme für alle Messreihen...")
            DataPlotter.save_plots_for_series(self.analyzers, plots_folder)
        
        # Weitere Plot-Typen analog zu create_plots()
        if app_config.analysis.create_boxplots:
            DataPlotter.create_boxplots(self.analyzers, boxplots_folder)
        
        if app_config.analysis.create_work_interval_plots:
            DataPlotter.create_work_interval_plots(self.analyzers, plots_folder)
        
        if app_config.analysis.create_normalized_plots:
            DataPlotter.create_normalized_plots(self.analyzers, plots_folder)
            DataPlotter.create_mean_normalized_plots(self.analyzers, plots_folder)
        
        if app_config.analysis.create_violin_plots:
            DataPlotter.create_violin_plots(self.analyzers, violin_folder)
        
        if app_config.analysis.create_zscore_plots:
            DataPlotter.create_z_score_plots(self.analyzers, zscore_folder)
    
    def export_results(self):
        """Exportiert die Ergebnisse in Excel-Dateien."""
        if not self.analyzers:
            self.logger.warning("Keine Ergebnisse zum Exportieren vorhanden")
            return
        
        # Excel-Exporter mit allen Ergebnissen befüllen
        exporter = ExcelExporter(self.logger)
        for name, analyzer in self.analyzers.items():
            exporter.add_measurement_series(name, analyzer)
        
        # Hauptergebnisse speichern
        main_file = exporter.save_to_excel()
        if main_file:
            self.logger.info(f"Hauptergebnisse gespeichert in: {main_file}")
        
        # Arbeitsintervalle speichern
        if app_config.analysis.calculate_work_intervals:
            intervals_file = exporter.save_work_intervals_to_excel()
            if intervals_file:
                self.logger.info(f"Arbeitsintervalle gespeichert in: {intervals_file}")
        
        # Boxplot-Daten speichern
        if app_config.analysis.create_boxplots:
            boxplot_file = exporter.save_boxplot_data_to_excel()
            if boxplot_file:
                self.logger.info(f"Boxplot-Daten gespeichert in: {boxplot_file}")
    
    def perform_group_analysis(self):
        """
        Führt eine automatische ANOVA-Analyse für Gruppen von Messreihen durch.
        Die Gruppen werden automatisch basierend auf gemeinsamen Präfixen der Ordnernamen erstellt.
        """
        if not hasattr(self, 'series_folders') or not self.series_folders:
            self.logger.warning("Keine Messreihen für Gruppenanalyse verfügbar")
            return
        
        # Automatische Gruppierung der Messreihen nach Präfixen
        self.anova_groups = self.file_handler.get_anova_groups(self.series_folders)
        
        if not self.anova_groups:
            self.logger.info("Keine geeigneten Gruppen für ANOVA-Analyse gefunden")
            return
        
        self.logger.info(f"ANOVA-Analyse wird für {len(self.anova_groups)} automatisch erkannte Gruppen durchgeführt")
        
        # Bestimme den übergeordneten Ordner für die Ausgabe
        parent_folder = self.series_folders[0].parent
        
        # Führe ANOVA-Analyse durch
        self.perform_anova_analysis(parent_folder)
        
        self.logger.info("Automatische ANOVA-Gruppenanalyse abgeschlossen")
    
    def perform_anova_analysis(self, output_folder: Path = None):
        """
        Führt eine ANOVA-Analyse für die automatisch gruppierten Messreihen durch.

        Args:
            output_folder: Der Ausgabeordner für die Ergebnisse.
                          Wenn None, wird der übergeordnete Ordner der Messreihen verwendet.
        """
        if not self.anova_groups:
            self.logger.warning("Keine Gruppen für ANOVA-Analyse definiert")
            return
        
        if not self.analyzers:
            self.logger.warning("Keine Daten für ANOVA-Analyse verfügbar")
            return
        
        # Initialisiere den StatisticalAnalyzer, falls noch nicht geschehen
        if not self.statistical_analyzer:
            from src.core.statistical_analysis import StatisticalAnalyzer
            self.statistical_analyzer = StatisticalAnalyzer(self.logger)
        
        # Bestimme den Ausgabeordner
        if output_folder is None:
            # Verwende den Standardpfad (gemeinsamer Elternordner der ersten Gruppe)
            first_group_folders = next(iter(self.anova_groups.values()))
            if not first_group_folders:
                self.logger.warning("Leere Gruppe gefunden, ANOVA-Analyse wird übersprungen")
                return
            
            parent_folder = first_group_folders[0].parent
            stats_folder = parent_folder / "statistical_analysis"
        else:
            # Verwende den angegebenen Ausgabeordner
            stats_folder = output_folder / "statistical_analysis"
        
        # Erstelle die Ausgabeordner
        anova_folder = stats_folder / "anova"
        for folder in [stats_folder, anova_folder]:
            folder.mkdir(exist_ok=True, parents=True)
        
        self.logger.info(f"ANOVA-Ergebnisse werden in {stats_folder} gespeichert")
        self.logger.info("Starte ANOVA-Analyse...")
        
        # Gruppiere die Daten nach den automatisch erkannten Gruppen
        f_max_groups = {}
        work_groups = {}
        ifss_groups = {}
        
        for group_name, folders in self.anova_groups.items():
            f_max_group_data = []
            work_group_data = []
            ifss_group_data = []
            
            for folder in folders:
                folder_name = folder.name
                
                if folder_name in self.analyzers:
                    analyzer = self.analyzers[folder_name]
                    
                    # F_max-Werte
                    if hasattr(analyzer, 'max_forces_data') and analyzer.max_forces_data:
                        f_max_group_data.extend(analyzer.max_forces_data)
                    
                    # Arbeitswerte
                    if hasattr(analyzer, 'works') and analyzer.works:
                        work_group_data.extend(analyzer.works)
                    
                    # IFSS-Werte
                    if hasattr(analyzer, 'ifssvalues') and analyzer.ifssvalues:
                        # Filtere ungültige Werte (z.B. 0)
                        valid_ifss = [val for val in analyzer.ifssvalues if val > 0]
                        if valid_ifss:
                            ifss_group_data.extend(valid_ifss)
            
            # Nur hinzufügen, wenn Daten vorhanden sind
            if f_max_group_data:
                f_max_groups[group_name] = np.array(f_max_group_data)
            
            if work_group_data:
                work_groups[group_name] = np.array(work_group_data)
            
            if ifss_group_data:
                ifss_groups[group_name] = np.array(ifss_group_data)
        
        # Führe ANOVA-Analysen durch
        results = {}
        anova_target_size = 10  # Target-Größe für Bootstrap-ANOVA
        
        # F_max ANOVA
        if len(f_max_groups) >= 2:
            self.logger.info("Führe ANOVA für Maximalkräfte durch...")
            results['F_max'] = self.statistical_analyzer.perform_anova(
                f_max_groups, anova_target_size, anova_folder, "F_max [N]")
        
        # Arbeit ANOVA
        if len(work_groups) >= 2:
            self.logger.info("Führe ANOVA für Arbeitswerte durch...")
            results['Arbeit'] = self.statistical_analyzer.perform_anova(
                work_groups, anova_target_size, anova_folder, "Arbeit [µJ]")
        
        # IFSS ANOVA
        if len(ifss_groups) >= 2:
            self.logger.info("Führe ANOVA für IFSS-Werte durch...")
            results['IFSS'] = self.statistical_analyzer.perform_anova(
                ifss_groups, anova_target_size, anova_folder, "IFSS [MPa]")
        
        # Erstelle einen Zusammenfassungsbericht
        self.statistical_analyzer.create_summary_report(
            {'bootstrap': {}, 'anova': results}, stats_folder)
        
        self.logger.info(f"ANOVA-Analyse abgeschlossen. Ergebnisse gespeichert in: {stats_folder}")
    
    def run(self):
        """Führt den Hauptablauf der Anwendung aus."""
        try:
            # Analysetyp wählen
            analysis_type = self.file_handler.select_analysis_type()
            
            # Welche Analysen sollen durchgeführt werden
            analysis_options = self.file_handler.select_analysis_types()
            
            # Update der Analysekonfiguration
            for key, value in analysis_options.items():
                if hasattr(app_config.analysis, key):
                    setattr(app_config.analysis, key, value)
            
            # Speichere die ANOVA-Option separat
            do_anova_analysis = analysis_options.get('do_anova_analysis', False)
            
            # Bootstrap-Option abfragen
            self.use_bootstrap = self.file_handler.select_bootstrap_option()
            
            if analysis_type == "1":
                # Einzelne Messreihe analysieren
                self.analyze_single_series()
            elif analysis_type == "2":
                # Alle Messreihen im Ordner analysieren
                self.analyze_all_series()
                
                # ANOVA-Gruppenanalyse, wenn mehr als eine Messreihe vorhanden ist und ANOVA gewählt wurde
                if len(self.analyzers) > 1 and do_anova_analysis:
                    self.perform_group_analysis()
            else:
                self.logger.error(f"Ungültiger Analysetyp: {analysis_type}")
                return
            
            # Export durchführen
            if app_config.analysis.export_to_excel:
                self.export_results()
            
            self.logger.info("=== Analyse abgeschlossen ===")
        
        except Exception as e:
            self.logger.error(f"Fehler in der Hauptanwendung: {e}", exc_info=True)
            messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten: {str(e)}")
        finally:
            # Abschließende Meldung
            self.logger.info("SFPO-Analyzer wird beendet.")
    
    def perform_bootstrap_analysis(self, base_folder: Path):
        """
        Führt eine Bootstrap-Analyse für die vorhandenen Messreihen durch.
        
        Args:
            base_folder: Der Basisordner für die Ausgabe der Ergebnisse
        """
        if not self.analyzers:
            self.logger.warning("Keine Daten für Bootstrap-Analyse verfügbar")
            return
        
        # Initialisiere den StatisticalAnalyzer
        from src.core.statistical_analysis import StatisticalAnalyzer
        self.statistical_analyzer = StatisticalAnalyzer(self.logger)
        
        # Erstelle den Ausgabeordner für statistische Analysen
        stats_folder = base_folder / "statistical_analysis"
        bootstrap_folder = stats_folder / "bootstrap"
        
        for folder in [stats_folder, bootstrap_folder]:
            folder.mkdir(exist_ok=True, parents=True)
        
        self.logger.info("Starte Bootstrap-Analyse...")
        
        # Extrahiere Daten für verschiedene Messgrößen
        f_max_data = {}
        work_data = {}
        ifss_data = {}
        
        for name, analyzer in self.analyzers.items():
            # Extrahiere F_max-Werte
            if hasattr(analyzer, 'max_forces_data') and analyzer.max_forces_data:
                f_max_data[name] = np.array(analyzer.max_forces_data)
            
            # Extrahiere Arbeitswerte
            if hasattr(analyzer, 'works') and analyzer.works:
                work_data[name] = np.array(analyzer.works)
            
            # Extrahiere IFSS-Werte
            if hasattr(analyzer, 'ifssvalues') and analyzer.ifssvalues:
                # Filtere ungültige Werte (z.B. 0)
                valid_ifss = [val for val in analyzer.ifssvalues if val > 0]
                if valid_ifss:
                    ifss_data[name] = np.array(valid_ifss)
        
        # Führe Bootstrap-Analysen durch
        results = {}
        
        # F_max Bootstrap
        if f_max_data:
            self.logger.info("Führe Bootstrap für Maximalkräfte durch...")
            results['F_max'] = self.statistical_analyzer.perform_bootstrap_analysis(
                f_max_data, bootstrap_folder)
        
        # Arbeit Bootstrap
        if work_data:
            self.logger.info("Führe Bootstrap für Arbeitswerte durch...")
            results['Arbeit'] = self.statistical_analyzer.perform_bootstrap_analysis(
                work_data, bootstrap_folder)
        
        # IFSS Bootstrap
        if ifss_data:
            self.logger.info("Führe Bootstrap für IFSS-Werte durch...")
            results['IFSS'] = self.statistical_analyzer.perform_bootstrap_analysis(
                ifss_data, bootstrap_folder)
        
        self.logger.info("Bootstrap-Analyse abgeschlossen")
    
    def perform_anova_analysis(self):
        """
        Führt eine ANOVA-Analyse für die ausgewählten Gruppen durch.
        """
        if not self.anova_groups:
            self.logger.warning("Keine Gruppen für ANOVA-Analyse definiert")
            return
        
        if not self.analyzers:
            self.logger.warning("Keine Daten für ANOVA-Analyse verfügbar")
            return
        
        # Initialisiere den StatisticalAnalyzer, falls noch nicht geschehen
        if not self.statistical_analyzer:
            from src.core.statistical_analysis import StatisticalAnalyzer
            self.statistical_analyzer = StatisticalAnalyzer(self.logger)
        
        # Bestimme den übergeordneten Ordner (gemeinsamer Elternordner der ersten Gruppe)
        first_group_folders = next(iter(self.anova_groups.values()))
        if not first_group_folders:
            self.logger.warning("Leere Gruppe gefunden, ANOVA-Analyse wird übersprungen")
            return
        
        parent_folder = first_group_folders[0].parent
        
        # Erstelle den Ausgabeordner für ANOVA-Analysen
        stats_folder = parent_folder / "statistical_analysis"
        anova_folder = stats_folder / "anova"
        
        for folder in [stats_folder, anova_folder]:
            folder.mkdir(exist_ok=True, parents=True)
        
        self.logger.info("Starte ANOVA-Analyse...")
        
        # Gruppiere die Daten nach den ausgewählten Gruppen
        f_max_groups = {}
        work_groups = {}
        ifss_groups = {}
        
        for group_name, folders in self.anova_groups.items():
            f_max_group_data = []
            work_group_data = []
            ifss_group_data = []
            
            for folder in folders:
                folder_name = folder.name
                
                if folder_name in self.analyzers:
                    analyzer = self.analyzers[folder_name]
                    
                    # F_max-Werte
                    if hasattr(analyzer, 'max_forces_data') and analyzer.max_forces_data:
                        f_max_group_data.extend(analyzer.max_forces_data)
                    
                    # Arbeitswerte
                    if hasattr(analyzer, 'works') and analyzer.works:
                        work_group_data.extend(analyzer.works)
                    
                    # IFSS-Werte
                    if hasattr(analyzer, 'ifssvalues') and analyzer.ifssvalues:
                        # Filtere ungültige Werte (z.B. 0)
                        valid_ifss = [val for val in analyzer.ifssvalues if val > 0]
                        if valid_ifss:
                            ifss_group_data.extend(valid_ifss)
            
            # Nur hinzufügen, wenn Daten vorhanden sind
            if f_max_group_data:
                f_max_groups[group_name] = np.array(f_max_group_data)
            
            if work_group_data:
                work_groups[group_name] = np.array(work_group_data)
            
            if ifss_group_data:
                ifss_groups[group_name] = np.array(ifss_group_data)
        
        # Führe ANOVA-Analysen durch
        results = {}
        anova_target_size = 10  # Target-Größe für Bootstrap-ANOVA
        
        # F_max ANOVA
        if len(f_max_groups) >= 2:
            self.logger.info("Führe ANOVA für Maximalkräfte durch...")
            results['F_max'] = self.statistical_analyzer.perform_anova(
                f_max_groups, anova_target_size, anova_folder, "F_max [N]")
        
        # Arbeit ANOVA
        if len(work_groups) >= 2:
            self.logger.info("Führe ANOVA für Arbeitswerte durch...")
            results['Arbeit'] = self.statistical_analyzer.perform_anova(
                work_groups, anova_target_size, anova_folder, "Arbeit [µJ]")
        
        # IFSS ANOVA
        if len(ifss_groups) >= 2:
            self.logger.info("Führe ANOVA für IFSS-Werte durch...")
            results['IFSS'] = self.statistical_analyzer.perform_anova(
                ifss_groups, anova_target_size, anova_folder, "IFSS [MPa]")
        
        # Erstelle einen Zusammenfassungsbericht
        self.statistical_analyzer.create_summary_report(
            {'bootstrap': {}, 'anova': results}, stats_folder)
        
        self.logger.info("ANOVA-Analyse abgeschlossen")


# Einstiegspunkt der Anwendung
def main():
    """Hauptfunktion zum Starten der Anwendung."""
    try:
        app = SFPOAnalyzer()
        app.run()
    except Exception as e:
        print(f"Kritischer Fehler in der Anwendung: {e}")
        if hasattr(e, "__traceback__"):
            import traceback
            traceback.print_tb(e.__traceback__)
        sys.exit(1)


# Falls das Skript direkt ausgeführt wird
if __name__ == "__main__":
    main()