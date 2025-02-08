# src/utils/debug_printer.py
import logging
from src.config.settings import naming_storage, sort_storage


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
