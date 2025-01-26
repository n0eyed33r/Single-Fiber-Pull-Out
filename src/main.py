# src/main.py
from src.core.file_handler import FileHandler
from src.core.data_sorter import DataSorter
from src.utils.debug_printer import DebugPrinter
from src.utils.logger_setup import LoggerSetup


def main():
    # Setup logging
    logger = LoggerSetup.setup_logger()
    debug_printer = DebugPrinter()

    logger.info("Starting SFPO Analysis")

    # Initialisierung und Dateiauswahl
    selected_path = FileHandler.select_folder()
    if not selected_path:
        logger.warning("No folder selected - program terminated")
        return

    # Dateien finden
    FileHandler.find_specimen_files()
    debug_printer.print_file_handling_results()

    # Sortierung durchführen
    DataSorter.analyze_filenames()
    debug_printer.print_sorting_results()

    logger.info("Analysis completed")


if __name__ == "__main__":
    main()