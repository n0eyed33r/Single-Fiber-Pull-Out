"""
this code was made with the help of chatgpt, claude, stackoverflow .... u name it
"""
# src/main.py
from src.core.data_statistics import MeasurementAnalyzer
from src.core.file_handler import FileHandler
from src.core.data_sorter import DataSorter
from src.utils.debug_printer import DebugPrinter
from src.utils.logger_setup import LoggerSetup
from src.core.data_plotting import DataPlotter

def main():
    # Setup logging
    logger = LoggerSetup.setup_logger()
    debug_printer = DebugPrinter()

    logger.info("Starting SFPO Analysis")

    # initialising and data grap
    selected_path = FileHandler.select_folder()
    if not selected_path:
        logger.warning("No folder selected - program terminated")
        return

    # find data
    FileHandler.find_specimen_files()
    debug_printer.print_file_handling_results()

    # sort
    DataSorter.analyze_filenames()
    debug_printer.print_sorting_results()

    # analyze first measurements
    analyzer = MeasurementAnalyzer()
    paths = analyzer.get_measurement_paths()
    first_measurement = analyzer.read_single_measurement(paths[0])
    print(f"Anzahl der Datenpunkte in erster Messung: {len(first_measurement)}")

    # get all measurements
    analyzer.read_all_measurements()
    print(f"Eingelesene Messunge: {len(analyzer.measurements_data)}")

    # plotting
    if analyzer.measurements_data:
        plotter = DataPlotter(analyzer)
        plotter.plot_measurements()
    else:
        print("Fehler beim Plotten")

    logger.info("Analysis completed")


if __name__ == "__main__":
    main()