# src/utils/debug_printer.py
import logging
from src.config.settings import naming_storage, sort_storage, MaterialParameters


class DebugPrinter:
    """Provides structured debug output for different stages of the analysis"""

    def __init__(self):
        self.logger = logging.getLogger('SFPO_Analyzer')

    def print_file_handling_results(self):
        """Logs results from the file handling stage"""
        self.logger.info("=== File Handling Results ===")
        self.logger.info(f"Root Path: {naming_storage.root_path}")
        self.logger.info(f"Main Folder: {naming_storage.main_folder}")
        self.logger.info(f"Number of Files Found: {len(naming_storage.filenames)}")
        self.logger.debug(f"File Names: {naming_storage.filenames}")  # Detaillierte Info als Debug-Level

    def print_sorting_results(self):
        """Logs results from the sorting stage"""
        self.logger.info("=== Sorting Results ===")
        self.logger.info("Successful Pull-Outs:")
        self.logger.info(f"  Count: {sort_storage.good_ones_nr}")
        self.logger.debug(f"  Files: {sort_storage.good_ones}")  # Detail-Information

        self.logger.info("Failed Pull-Outs:")
        self.logger.info(f"  Count: {sort_storage.bad_ones_nr}")
        self.logger.debug(f"  Files: {sort_storage.bad_ones}")  # Detail-Information

        total = sort_storage.good_ones_nr + sort_storage.bad_ones_nr
        self.logger.info(f"Total Measurements: {total}")