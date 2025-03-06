"""
SFPO-Analyzer: Hauptanwendungsmodul für den Single-Fiber-Pull-Out Test Analyzer
mit erweiterter statistischer Analyse (Bootstrap und ANOVA)
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

# Füge den src-Ordner zum Python-Pfad hinzu, wenn er noch nicht dort ist
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
if src_dir not in sys.path:
    sys.path.append(str(src_dir))

# Importiere Modulkomponenten
from src.utils.logger_setup import LoggerSetup
from src.core.file_handler import FileHandler
from src.core.data_sorter import DataSorter
from src.core.data_statistics import MeasurementAnalyzer
from src.core.excel_exporter import ExcelExporter
from src.core.data_plotting import DataPlotter
from src.core.statistical_analysis import StatisticalAnalyzer  # Neues Statistikmodul
from src.config.config_manager import app_config


def select_output_folder():
    """
    Lässt den Benutzer einen Ordner für alle Ausgaben auswählen.

    Returns:
        Path-Objekt zum ausgewählten Ordner oder None, wenn abgebrochen
    """
    root = tk.Tk()
    root.withdraw()
    root.lift()
    root.attributes('-topmost', True)
    root.focus_force()

    folder_path = filedialog.askdirectory(
        title="Ordner für alle Ausgaben (Excel, Plots und Statistik) auswählen"
    )

    root.destroy()

    if not folder_path:
        return None

    output_path = Path(folder_path)

    # Stelle sicher, dass der Ordner existiert
    output_path.mkdir(exist_ok=True, parents=True)

    return output_path


def main():
    """Hauptfunktion des SFPO-Analyzers"""
    # Logger einrichten
    logger = LoggerSetup.setup_logger()
    logger.info("Starting SFPO Analysis")

    # Initialisiere Kernkomponenten
    file_handler = FileHandler(logger)
    data_sorter = DataSorter(logger)
    data_plotter = DataPlotter(logger)
    excel_exporter = ExcelExporter(logger)
    stat_analyzer = StatisticalAnalyzer(logger)  # Neue Statistikkomponente

    try:
        # 1. Analysemodus auswählen (Einzelne Messreihe oder mehrere)
        analysis_mode = file_handler.select_analysis_type()
        logger.info(f"Ausgewählter Analysetyp: {'Einzelne Messreihe' if analysis_mode == '1' else 'Alle Messreihen'}")

        # Dictionary für alle Analyzer (Messreihe: Analyzer)
        analyzer_dict = {}

        if analysis_mode == '1':
            # 2a. Einzelne Messreihe analysieren
            selected_folder = file_handler.select_folder(analysis_mode)

            if not selected_folder:
                logger.warning("Keine Messreihe ausgewählt, Programm wird beendet.")
                return

            # Verarbeite die Messreihe
            logger.info(f"Verarbeite Messreihe: {selected_folder.name}")
            analyzer = process_measurement_series(selected_folder, data_sorter, logger)

            if analyzer:
                analyzer_dict[selected_folder.name] = analyzer

        else:
            # 2b. Alle Messreihen im Überordner analysieren
            parent_folder = file_handler.select_folder(analysis_mode)

            if not parent_folder:
                logger.warning("Kein Überordner ausgewählt, Programm wird beendet.")
                return

            # Finde alle Unterordner mit Messreihen
            series_folders = file_handler.get_measurement_series_folders(parent_folder)

            if not series_folders:
                logger.warning("Keine Messreihenordner gefunden.")
                return

            # Verarbeite jede Messreihe
            for folder in series_folders:
                logger.info(f"Verarbeite Messreihe: {folder.name}")

                # Konfiguration für neue Messreihe zurücksetzen
                app_config.reset_for_new_series()

                # Messreihe verarbeiten
                analyzer = process_measurement_series(folder, data_sorter, logger)

                if analyzer:
                    analyzer_dict[folder.name] = analyzer

        # 3. Wenn Analyzer vorhanden sind, erstelle Plots, führe Statistikanalysen durch und exportiere Excel
        if analyzer_dict:
            # Lasse den Benutzer einen Ausgabeordner wählen
            output_folder = select_output_folder()

            if not output_folder:
                logger.warning("Kein Ausgabeordner gewählt, verwende Standard-Unterordner.")
                # Falls kein Ausgabeordner gewählt wurde, verwenden wir ein Standardverzeichnis
                if analysis_mode == '1':
                    output_folder = selected_folder
                else:
                    output_folder = parent_folder

            # Erstelle Ausgabe-Unterordner (wir brauchen sie für die Struktur)
            plots_folder = output_folder / "plots"
            boxplots_folder = output_folder / "box_plots"
            violin_folder = output_folder / "violin_plots"
            zscore_folder = output_folder / "zscore_plots"

            # Stelle sicher, dass alle Unterordner existieren
            for folder in [plots_folder, boxplots_folder, violin_folder, zscore_folder]:
                folder.mkdir(exist_ok=True, parents=True)

            logger.info(f"Alle Ausgaben werden in {output_folder} gespeichert.")
            logger.info(f"Erstelle Plots für {len(analyzer_dict)} Messreihen...")

            # Plots erstellen entsprechend der Konfiguration
            if app_config.analysis.create_standard_plots:
                logger.info("Erstelle Standard-Plots...")
                DataPlotter.save_plots_for_series(analyzer_dict, plots_folder)

            if app_config.analysis.create_boxplots:
                logger.info("Erstelle Boxplots...")
                DataPlotter.create_boxplots(analyzer_dict, boxplots_folder)

            if app_config.analysis.create_work_interval_plots:
                logger.info("Erstelle Arbeitsintervall-Plots...")
                DataPlotter.create_work_interval_plots(analyzer_dict, plots_folder)

            if app_config.analysis.create_normalized_plots:
                logger.info("Erstelle normierte Plots...")
                DataPlotter.create_normalized_plots(analyzer_dict, plots_folder)
                DataPlotter.create_mean_normalized_plots(analyzer_dict, plots_folder)

            if app_config.analysis.create_violin_plots:
                logger.info("Erstelle Violin-Plots...")
                DataPlotter.create_violin_plots(analyzer_dict, violin_folder)

            if app_config.analysis.create_zscore_plots:
                logger.info("Erstelle Z-Score-Plots...")
                DataPlotter.create_z_score_plots(analyzer_dict, zscore_folder)

            # Führe erweiterte statistische Analysen durch
            logger.info("Führe erweiterte statistische Analysen durch...")
            stat_results = stat_analyzer.compare_groups(analyzer_dict, output_folder)

            # Excel-Export
            if app_config.analysis.export_to_excel:
                logger.info("Exportiere Daten nach Excel...")

                # Füge jede Messreihe zum Excel-Exporter hinzu
                for name, analyzer in analyzer_dict.items():
                    excel_exporter.add_measurement_series(name, analyzer)

                # Anpassen der Excel-Funktionen für vordefinierten Speicherort
                # Diese Hilfsfunktion erzeugt automatisch Excel-Pfade im Ausgabeordner
                def get_excel_path(base_name):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_name = f"{base_name}_{timestamp}.xlsx"
                    return output_folder / file_name

                # Angepasste Funktion für Excel-Speicherung mit vorgegebenem Pfad
                def save_excel_with_predefined_path(save_method, file_path):
                    # Wir müssen monkeypatchen, um den Speicherdialog zu umgehen
                    original_method = filedialog.asksaveasfilename

                    # Temporäre Ersatzmethode, die immer den vordefinierten Pfad zurückgibt
                    def temp_filedialog_method(*args, **kwargs):
                        return str(file_path)

                    try:
                        # Ersetze den Dateidialog durch unsere Methode
                        filedialog.asksaveasfilename = temp_filedialog_method
                        # Rufe die originale Speichermethode auf
                        result = save_method()
                        return result
                    finally:
                        # Stelle den Originalzustand wieder her
                        filedialog.asksaveasfilename = original_method

                # Speichere Hauptergebnisse
                main_excel_path = get_excel_path("SFPO_Ergebnisse")
                if save_excel_with_predefined_path(excel_exporter.save_to_excel, main_excel_path):
                    logger.info(f"Hauptergebnisse gespeichert in: {main_excel_path}")

                # Speichere Arbeitsintervalle
                intervals_excel_path = get_excel_path("SFPO_Arbeitsintervalle")
                if save_excel_with_predefined_path(excel_exporter.save_work_intervals_to_excel, intervals_excel_path):
                    logger.info(f"Arbeitsintervalle gespeichert in: {intervals_excel_path}")

                # Speichere Boxplot-Daten
                boxplot_excel_path = get_excel_path("SFPO_Boxplot_Daten")
                if save_excel_with_predefined_path(excel_exporter.save_boxplot_data_to_excel, boxplot_excel_path):
                    logger.info(f"Boxplot-Daten gespeichert in: {boxplot_excel_path}")

            logger.info("Analyse abgeschlossen.")
        else:
            logger.warning("Keine Daten zur Analyse verfügbar.")

    except Exception as e:
        logger.error(f"Fehler in der Hauptroutine: {str(e)}", exc_info=True)

    finally:
        logger.info("SFPO Analysis beendet")


def process_measurement_series(folder_path, data_sorter, logger):
    """
    Verarbeitet eine einzelne Messreihe und gibt den Analyzer zurück.

    Args:
        folder_path: Pfad zum Messreihenordner
        data_sorter: DataSorter-Instanz
        logger: Logger-Instanz

    Returns:
        MeasurementAnalyzer-Instanz oder None bei Fehler
    """
    try:
        # Pfade aktualisieren
        app_config.paths.update_paths(folder_path)

        # Dateien finden
        file_handler = FileHandler(logger)
        file_handler.find_specimen_files()

        if not app_config.paths.filenames:
            logger.warning(f"Keine Dateien in {folder_path} gefunden.")
            return None

        # Dateien sortieren
        data_sorter.analyze_filenames()

        if not app_config.classification.successful_measurements:
            logger.warning(f"Keine erfolgreichen Messungen in {folder_path} gefunden.")
            return None

        # Pull-Out Verhältnis berechnen
        data_sorter.calculate_pullout_ratio()

        # Analyzer erstellen und Daten verarbeiten
        analyzer = MeasurementAnalyzer(logger)
        analyzer.read_all_measurements()

        if not analyzer.measurements_data:
            logger.warning(f"Keine Messdaten in {folder_path} gelesen.")
            return None

        # Statistiken berechnen
        analyzer.find_all_max_forces()
        analyzer.find_all_embeddinglengths()
        analyzer.process_all_fiberdiameters()

        # Prüfe Konsistenz der Daten
        if not analyzer.check_data_consistency():
            logger.warning(f"Inkonsistente Daten in {folder_path}.")
            # Fahre trotzdem fort, aber mit Warnung

        # Weitere Berechnungen
        analyzer.interfaceshearstrength()
        analyzer.calculate_all_works()

        # Arbeitsintervalle berechnen, wenn konfiguriert
        if app_config.analysis.calculate_work_intervals:
            analyzer.calculate_all_work_intervals()
            analyzer.calculate_normed_intervals()
            analyzer.calculate_interval_statistics()

        # Force-Moduli berechnen, wenn konfiguriert
        if app_config.analysis.calculate_force_moduli:
            analyzer.calculate_force_modulus()

        return analyzer

    except Exception as e:
        logger.error(f"Fehler bei der Verarbeitung von {folder_path}: {str(e)}", exc_info=True)
        return None


if __name__ == "__main__":
    main()