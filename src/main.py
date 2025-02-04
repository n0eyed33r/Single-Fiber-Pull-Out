# src/main.py
from src.core.data_statistics import MeasurementAnalyzer
from src.core.file_handler import FileHandler
from src.core.data_sorter import DataSorter
from src.utils.debug_printer import DebugPrinter
from src.utils.logger_setup import LoggerSetup
from src.core.data_plotting import DataPlotter
from src.core.excel_exporter import ExcelExporter
from src.config.settings import naming_storage
from pathlib import Path

def process_single_series(logger, debug_printer, folder_path=None):
    """Verarbeitet eine einzelne Messreihe
    Args:
        folder_path: Wenn gegeben, wird dieser Pfad verwendet, sonst wird nach Auswahl gefragt
    """
    try:
        # Ordnerauswahl oder Pfadübernahme
        if folder_path is None:
            selected_path = FileHandler.select_folder(analysis_type='1')
            if not selected_path:
                logger.warning("No folder selected - program terminated")
                return None
        else:
            selected_path = folder_path
            naming_storage.update_paths(selected_path)

        # Dateien finden und sortieren
        found_files = FileHandler.find_specimen_files()
        if not found_files:
            logger.warning("Keine Messdateien im ausgewählten Ordner gefunden")
            return None

        debug_printer.print_file_handling_results()
        DataSorter.analyze_filenames()
        debug_printer.print_sorting_results()

        # Analyse durchführen
        analyzer = MeasurementAnalyzer()
        paths = analyzer.get_measurement_paths()
        print(f"Gefundene Messpfade: {len(paths)}")

        analyzer.read_all_measurements()
        print(f"Eingelesene Messungen: {len(analyzer.measurements_data)}")

        # Berechnungen durchführen
        analyzer.process_all_fiberdiameters()
        analyzer.check_data_consistency()
        analyzer.find_all_max_forces()
        analyzer.find_all_embeddinglengths()
        analyzer.interfaceshearstrength()

        # Statistische Auswertungen
        print("\nStatistische Auswertung:")
        print(f"Maximalkräfte: {analyzer.calculate_mean('forces'):.2f} ± {analyzer.calculate_stddev('forces'):.2f} N")
        print(f"Einbettlängen: {analyzer.calculate_mean('lengths'):.2f} ± {analyzer.calculate_stddev('lengths'):.2f} µm")
        print(f"Faserdurchmesser: {analyzer.calculate_mean('diameters'):.2f} ± {analyzer.calculate_stddev('diameters'):.2f} µm")
        print(f"IFSS: {analyzer.calculate_mean('ifss'):.2f} ± {analyzer.calculate_stddev('ifss'):.2f} MPa")

        # Arbeitsberechnungen
        analyzer.calculate_all_works()
        print(f"Verrichtete Arbeit: {analyzer.calculate_mean('works'):.2f} ± {analyzer.calculate_stddev('works'):.2f} µJ")

        analyzer.calculate_all_work_intervals()
        print("\nArbeitsintervalle:")
        for i, intervals in enumerate(analyzer.work_intervals, 1):
            print(f"Messung {i}: {intervals}")

        analyzer.calculate_normed_intervals()
        analyzer.calculate_interval_statistics()

        print("\nStatistik der normierten Intervalle:")
        for i in range(10):
            print(f"Intervall {i + 1}: "
                  f"{analyzer.mean_normed_intervals[i]:.3f} ± "
                  f"{analyzer.stddev_normed_intervals[i]:.3f} "
                  f"(rel. Stdabw: {analyzer.rel_stddev_normed_intervals[i]:.1%})")

        return analyzer

    except ValueError as e:
        logger.error(f"Fehler bei der Analyse: {e}")
        return None
    except Exception as e:
        logger.error(f"Unerwarteter Fehler: {e}")
        return None

def main():
    # Setup logging
    logger = LoggerSetup.setup_logger()
    debug_printer = DebugPrinter()
    logger.info("Starting SFPO Analysis")

    # Analysetyp wählen
    analysis_type = FileHandler.select_analysis_type()

    if analysis_type == '1':
        # Einzelanalyse
        analyzer = process_single_series(logger, debug_printer)
        if analyzer:
            logger.info("Einzelanalyse erfolgreich abgeschlossen")
        else:
            logger.warning("Einzelanalyse fehlgeschlagen")
    else:
        # Mehrfachanalyse
        parent_folder = FileHandler.select_folder(analysis_type='2')
        if not parent_folder:
           logger.warning("Kein Ordner ausgewählt")
           return

        exporter = ExcelExporter()
        series_folders = FileHandler.get_measurement_series_folders(parent_folder)
        last_successful_analyzer = None  # Hier die Variable initialisieren

        for folder in series_folders:
            logger.info(f"\nAnalysiere Messreihe: {folder.name}")
            # Übergebe den Ordnerpfad direkt
            analyzer = process_single_series(logger, debug_printer, folder)
            if analyzer:
                exporter.add_measurement_series(folder.name, analyzer)
                last_successful_analyzer = analyzer  # Hier den letzten erfolgreichen Analyzer speichern
            else:
                logger.warning(f"Überspringe Messreihe {folder.name} - Analyse fehlgeschlagen")

        # Beim Speichern der Ergebnisse
        save_path = exporter.save_to_excel()
        if save_path and isinstance(save_path, Path):  # Prüfe ob ein gültiger Pfad zurückgegeben wurde
            png_path = save_path.with_suffix('.png')
            # Speichere Plot, aber nur wenn es erfolgreiche Analysen gab
            if last_successful_analyzer:
                plotter = DataPlotter(last_successful_analyzer)
                plotter.save_plot(str(png_path))
            else:
                logger.warning("Keine erfolgreichen Analysen für Plot vorhanden")

    logger.info("Analysis completed")

if __name__ == "__main__":
   main()