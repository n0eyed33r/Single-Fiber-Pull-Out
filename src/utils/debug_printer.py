"""
this code was made with the help of chatgpt, claude, gemini, stackoverflow .... u name it
"""
# src/utils/debug_printer.py
import logging
from src.config.settings import naming_storage, sort_storage
from src.main import app_config


class DebugPrinter:
    def __init__(self):
        # Wir holen uns eine Referenz auf unseren bestehenden Logger
        self.logger = logging.getLogger('SFPO_Analyzer')

    def print_file_handling_results(self):
        # Detaillierte Ausgabe der Dateisystem-Informationen
        self.logger.info("\n=== Datei-Verarbeitung ===")
        self.logger.info(f"Ausgewählter Pfad: {naming_storage.root_path}")
        self.logger.info(f"Hauptordner: {naming_storage.main_folder}")
        self.logger.info(f"Anzahl gefundener Dateien: {len(naming_storage.filenames)}")
        # Detaillierte Dateiliste auf Debug-Level für weniger wichtige Details
        self.logger.debug(f"Vollständige Dateiliste: {naming_storage.filenames}")

    def print_sorting_results(self):
        # Ausgabe der Sortierungsergebnisse
        self.logger.info("\n=== Sortierungsergebnisse ===")
        self.logger.info(f"Erfolgreiche Messungen: {sort_storage.good_ones_nr}")
        self.logger.info(f"Fehlgeschlagene Messungen: {sort_storage.bad_ones_nr}")

        # Gesamtanzahl der Messungen
        total = sort_storage.good_ones_nr + sort_storage.bad_ones_nr
        self.logger.info(f"Gesamtanzahl der Messungen: {total}")

        # Detaillierte Listen auf Debug-Level
        self.logger.debug("Erfolgreiche Messungen Details:")
        self.logger.debug(f"Dateien Erfolg: {sort_storage.good_ones}")
        self.logger.debug("Fehlgeschlagene Messungen Details:")
        self.logger.debug(f"Dateien Abbruch: {sort_storage.bad_ones}")

    def print_plot_config(self):
        """Gibt die aktuellen Plot-Konfigurationseinstellungen aus."""
        self.logger = logging.getLogger('SFPO_Analyzer')
        self.logger.info("=== Plot-Konfigurationseinstellungen ===")
        self.logger.info(f"Standard-Plots: {app_config.analysis.create_standard_plots}")
        self.logger.info(f"Boxplots: {app_config.analysis.create_boxplots}")
        self.logger.info(f"Arbeitsintervall-Plots: {app_config.analysis.create_work_interval_plots}")
        self.logger.info(f"Normierte Arbeits-Plots: {app_config.analysis.create_normalized_plots}")
        self.logger.info(f"Violin-Plots: {app_config.analysis.create_violin_plots}")
        self.logger.info(f"Z-Score-Plots: {app_config.analysis.create_zscore_plots}")
        self.logger.info("=====================================")
