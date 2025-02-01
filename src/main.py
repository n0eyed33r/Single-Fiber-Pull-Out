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
    # setup logging
    logger = LoggerSetup.setup_logger()
    debug_printer = DebugPrinter()
    # startin logging
    logger.info("Starting SFPO Analysis")

    # initialising and data grab
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

    # instantiate class
    analyzer = MeasurementAnalyzer()

    # proof of finding the path
    paths = analyzer.get_measurement_paths()
    print(f"Gefundene Messpfade:{len(paths)}")

    # read measurements
    analyzer.read_all_measurements()
    print(f"Eingelesene Messunge: {len(analyzer.measurements_data)}")

    # calculating
    analyzer.process_all_fiberdiameters()
    analyzer.check_data_consistency()
    analyzer.find_all_max_forces()
    analyzer.find_all_embeddinglengths()
    analyzer.interfaceshearstrength()

    # Statistische Auswertungen
    print("\nStatistische Auswertung:")
    print(f"Maximalkräfte: {analyzer.calculate_mean('forces'):.2f} ± {analyzer.calculate_stddev('forces'):.2f} N")
    print(f"Einbettlängen: {analyzer.calculate_mean('lengths'):.2f} ± {analyzer.calculate_stddev('lengths'):.2f} µm")
    print(
        f"Faserdurchmesser: {analyzer.calculate_mean('diameters'):.2f} ± {analyzer.calculate_stddev('diameters'):.2f} µm")
    print(f"IFSS: {analyzer.calculate_mean('ifss'):.2f} ± {analyzer.calculate_stddev('ifss'):.2f} MPa")

    # Nach den anderen Berechnungen
    analyzer.calculate_all_works()

    # Bei den statistischen Auswertungen
    print(f"Verrichtete Arbeit: {analyzer.calculate_mean('works'):.2f} ± {analyzer.calculate_stddev('works'):.2f} µJ")

    logger.info("Analysis completed")

'''    # plotting
    if analyzer.measurements_data:
        plotter = DataPlotter(analyzer)
        plotter.plot_measurements()
    else:
        print("Fehler beim Plotten")'''


if __name__ == "__main__":
    main()