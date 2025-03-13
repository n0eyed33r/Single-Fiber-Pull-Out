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
from dataclasses import dataclass
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional


@dataclass
class AnalysisConfig:
    """Konfigurationsklasse für die Steuerung der Analyseschritte"""
    # Berechnungen
    calculate_zscores: bool = True
    calculate_force_moduli: bool = True
    calculate_work_intervals: bool = True
    
    # Statistische Analysen
    perform_bootstrap: bool = False  # Neue Option für Bootstrap
    perform_anova: bool = False      # Neue Option für ANOVA
    bootstrap_samples: int = 1000    # Anzahl der Bootstrap-Stichproben
    anova_target_size: int = 10      # Zielgröße für ANOVA-Bootstrap
    
    # Plot-Erstellung
    create_standard_plots: bool = True  # Kraft-Weg-Diagramme
    create_boxplots: bool = True  # Boxplots für F_max und Arbeit
    create_work_interval_plots: bool = True
    create_normalized_plots: bool = True  # Normierte Arbeitsplots
    create_violin_plots: bool = True  # Violin-Plots
    create_zscore_plots: bool = True  # Z-Score-Plots
    create_statistical_plots: bool = True  # Neue Option für statistische Plots
    
    # Export
    export_to_excel: bool = True


def process_single_series(
        logger,
        debug_printer,
        folder_path: Optional[Path] = None,
        config: Optional[AnalysisConfig] = None
) -> Optional[MeasurementAnalyzer]:
    """Verarbeitet eine einzelne Messreihe mit konfigurierbaren Analyseschritten

    Args:
        logger: Logger-Instanz
        debug_printer: Debug-Printer-Instanz
        folder_path: Wenn gegeben, wird dieser Pfad verwendet, sonst wird nach Auswahl gefragt
        config: Konfigurationsobjekt zur Steuerung der Analyseschritte
    """
    # Standardkonfiguration wenn keine angegeben
    if config is None:
        config = AnalysisConfig()
    
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
        
        # Grundlegende Berechnungen
        analyzer.process_all_fiberdiameters()
        analyzer.check_data_consistency()
        analyzer.find_all_max_forces()
        analyzer.find_all_embeddinglengths()
        analyzer.calculate_all_works()
        analyzer.interfaceshearstrength()
        
        # Statistische Auswertungen
        print("\nStatistische Auswertung:")
        print(f"Maximalkräfte: {analyzer.calculate_mean('forces'):.2f} ± {analyzer.calculate_stddev('forces'):.2f} N")
        print(
            f"Einbettlängen: {analyzer.calculate_mean('lengths'):.2f} ± {analyzer.calculate_stddev('lengths'):.2f} µm")
        print(
            f"Faserdurchmesser: {analyzer.calculate_mean('diameters'):.2f} ± {analyzer.calculate_stddev('diameters'):.2f} µm")
        print(f"IFSS: {analyzer.calculate_mean('ifss'):.2f} ± {analyzer.calculate_stddev('ifss'):.2f} MPa")
        print(f"Arbeit: {analyzer.calculate_mean('works'):.2f} ± {analyzer.calculate_stddev('works'):.2f} µJ")

        # Optionale Berechnungen basierend auf Konfiguration
        if config.calculate_force_moduli:
            analyzer.calculate_force_modulus()
            print(f"Verbundmodul: {analyzer.calculate_mean('force_modulus'):.3f} ± "
                  f"{analyzer.calculate_stddev('force_modulus'):.3f} N/µm")

        # In der main.py, wo die anderen statistischen Ausgaben sind
        if config.calculate_work_intervals:
            print("\nKumulative normierte Arbeit:")
            stats = analyzer.get_cumulative_normed_work_statistics()
            print("Position | Mittelwert ± Standardabweichung")
            print("-" * 45)
            for position in sorted(stats.keys(), key=lambda x: float(x.strip('%'))):
                mean = stats[position]["mean"]
                std = stats[position]["std"]
                print(f"{position:8} | {mean:.4f} ± {std:.4f}")

        # Optionale Arbeitsberechnungen
        if config.calculate_work_intervals:
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
    
    # Statistische Optionen wählen
    if analysis_type == '2':  # Nur für Mehrfachanalyse statistische Optionen anbieten
        logger.info("Statistische Analyseoptionen auswählen")
        stat_options = FileHandler.select_statistical_options()  # Verwende FileHandler
        logger.info(f"Gewählte statistische Optionen: {stat_options}")
    else:
        # Standard-Optionen für Einzelanalyse (keine statistische Analyse)
        stat_options = {
            "perform_bootstrap": False,
            "perform_anova": False,
            "bootstrap_samples": 1000,
            "anova_target_size": 10,
            "create_statistical_plots": True
        }
    
    # Konfigurationen definieren
    quick_test_config = AnalysisConfig(
        calculate_zscores=False,
        calculate_force_moduli=True,
        calculate_work_intervals=True,
        create_standard_plots=True,
        create_boxplots=True,
        create_normalized_plots=True,
        create_violin_plots=False,
        create_zscore_plots=False,
        export_to_excel=True,
        # Statistische Optionen
        perform_bootstrap=False,
        perform_anova=False
    )
    
    # Vollständige Konfiguration für Mehrfachanalyse mit statistischen Optionen
    full_analysis_config = AnalysisConfig(
        # Alle grundlegenden Optionen standardmäßig True
        # Füge statistische Optionen hinzu
        perform_bootstrap=stat_options.get("perform_bootstrap", False),
        perform_anova=stat_options.get("perform_anova", False),
        bootstrap_samples=stat_options.get("bootstrap_samples", 1000),
        anova_target_size=stat_options.get("anova_target_size", 10),
        create_statistical_plots=stat_options.get("create_statistical_plots", True)
    )
    
    if analysis_type == '1':
        # Einzelanalyse mit Schnelltest-Konfiguration
        analyzer = process_single_series(
            logger,
            debug_printer,
            config=quick_test_config
        )
        if analyzer:
            # Erstelle und zeige den Plot für die einzelne Messreihe
            plt.figure(figsize=(10, 6))
            colors = plt.cm.plasma(np.linspace(0, 1, len(analyzer.measurements_data)))
            
            for i, (measurement, color) in enumerate(zip(analyzer.measurements_data, colors)):
                distances, forces = zip(*measurement)
                plt.plot(distances, forces, color=color, label=f'Messung {i + 1}')
            
            plt.xlim(0, 1000)
            plt.ylim(0, 0.3)
            plt.xticks(np.arange(0, 1001, 200), fontsize=12)
            plt.yticks(np.arange(0, 0.31, 0.05), fontsize=12)
            
            plt.title("Auszugskurven", fontsize=14, fontweight='bold')
            plt.xlabel('Weg [µm]', fontsize=12)
            plt.ylabel('Kraft [N]', fontsize=12)
            plt.legend()
            plt.grid(True)
            
            # Zeige den Plot an
            plt.show()
            
            logger.info("Einzelanalyse erfolgreich abgeschlossen")
        else:
            logger.warning("Einzelanalyse fehlgeschlagen")
    else:
        # Mehrfachanalyse mit voller Konfiguration
        parent_folder = FileHandler.select_folder(analysis_type='2')
        if not parent_folder:
            logger.warning("Kein Ordner ausgewählt")
            return
        
        exporter = ExcelExporter()
        series_folders = FileHandler.get_measurement_series_folders(parent_folder)
        analyzers_dict = {}
        last_successful_analyzer = None
        
        for folder in series_folders:
            logger.info(f"\nAnalysiere Messreihe: {folder.name}")
            analyzer = process_single_series(
                logger,
                debug_printer,
                folder,
                config=full_analysis_config
            )
            if analyzer:
                name = folder.name
                exporter.add_measurement_series(name, analyzer)
                analyzers_dict[name] = analyzer
                last_successful_analyzer = analyzer
            else:
                logger.warning(f"Überspringe Messreihe {folder.name} - Analyse fehlgeschlagen")
        
        if analyzers_dict:
            # Export und Plot-Erstellung basierend auf Konfiguration
            if full_analysis_config.export_to_excel:
                save_path = exporter.save_to_excel()
                if save_path and isinstance(save_path, Path):
                    # Erstelle den Hauptordner für alle Plots
                    plots_base_folder = save_path.parent / "plots-auswertung"
                    plots_base_folder.mkdir(exist_ok=True)
                    
                    # Speichere Arbeitsintervalle wenn aktiviert
                    if full_analysis_config.calculate_work_intervals:
                        intervals_path = exporter.save_work_intervals_to_excel()
                        exporter.save_boxplot_data_to_excel()
                    
                    # Erstelle verschiedene Plots basierend auf Konfiguration
                    if full_analysis_config.create_standard_plots:
                        standard_plots_folder = plots_base_folder / "kraft_weg-plots"
                        standard_plots_folder.mkdir(exist_ok=True)
                        DataPlotter.save_plots_for_series(analyzers_dict, standard_plots_folder)
                    
                    if full_analysis_config.create_boxplots:
                        boxplots_folder = plots_base_folder / "box_plots"
                        boxplots_folder.mkdir(exist_ok=True)
                        DataPlotter.create_boxplots(analyzers_dict, boxplots_folder)
                    
                    if full_analysis_config.create_work_interval_plots:
                        work_intervals_folder = plots_base_folder / "arbeitsintervalle"
                        work_intervals_folder.mkdir(exist_ok=True)
                        DataPlotter.create_work_interval_plots(analyzers_dict, work_intervals_folder)
                    
                    if full_analysis_config.create_normalized_plots:
                        normalized_folder = plots_base_folder / "normierte_arbeit"
                        normalized_folder.mkdir(exist_ok=True)
                        DataPlotter.create_normalized_plots(analyzers_dict, normalized_folder)
                    
                    if full_analysis_config.create_normalized_plots:
                        mean_normalized_folder = plots_base_folder / "mittlere_normierte_arbeit"
                        mean_normalized_folder.mkdir(exist_ok=True)
                        DataPlotter.create_mean_normalized_plots(analyzers_dict, mean_normalized_folder)
                    
                    if full_analysis_config.create_violin_plots:
                        violin_folder = plots_base_folder / "violin_plots"
                        violin_folder.mkdir(exist_ok=True)
                        DataPlotter.create_violin_plots(analyzers_dict, violin_folder)
                    
                    if full_analysis_config.create_zscore_plots and full_analysis_config.calculate_zscores:
                        zscore_folder = plots_base_folder / "zscore_plots"
                        zscore_folder.mkdir(exist_ok=True)
                        DataPlotter.create_z_score_plots(analyzers_dict, zscore_folder)
                    
                    # Führe statistische Analysen durch, wenn aktiviert
                    if full_analysis_config.perform_bootstrap or full_analysis_config.perform_anova:
                        logger.info("Starte statistische Analysen...")
                        FileHandler.perform_statistical_analysis(  # Verwende FileHandler
                            analyzers_dict=analyzers_dict,
                            logger=logger,
                            plots_base_folder=plots_base_folder,
                            config=full_analysis_config
                        )
                    
                    logger.info(f"Ergebnisse gespeichert in: {save_path.parent}")
        else:
            logger.warning("Keine erfolgreichen Analysen durchgeführt")
    
    logger.info("Analysis completed")


if __name__ == "__main__":
    main()