# src/core/data_plotting.py
import matplotlib.pyplot as plt
from src.core.data_statistics import MeasurementAnalyzer
from pathlib import Path

class DataPlotter:
    def __init__(self, analyzer: 'MeasurementAnalyzer'):
        self.analyzer = analyzer

    @staticmethod
    def save_plots_for_series(analyzers_dict: dict, plots_folder: Path):
        """
        Erstellt und speichert Plots für alle Messreihen.
        Args:
            analyzers_dict: Dictionary mit {Probenname: Analyzer}
            plots_folder: Ordner zum Speichern der Plots
        """
        for name, analyzer in analyzers_dict.items():
            plt.figure(figsize=(10, 6))

            # Plotte alle Messungen dieser Serie
            for i, measurement in enumerate(analyzer.measurements_data, 1):
                distances, forces = zip(*measurement)
                plt.plot(distances, forces, label=f'Messung {i}')

            plt.xlabel('Distance [µm]')
            plt.ylabel('Force [N]')
            plt.title(f'Pull-Out Messungen - {name}')
            plt.legend()
            plt.grid(True)

            # Speichere Plot
            plot_path = plots_folder / f"{name}_plot.png"
            plt.savefig(plot_path)
            plt.close()  # Wichtig: Figure schließen um Speicher freizugeben

    def save_plot(self, save_path: str):
        """Speichert einen einzelnen Plot"""
        plt.figure(figsize=(10, 6))

        for i, measurement in enumerate(self.analyzer.measurements_data, 1):
            distances, forces = zip(*measurement)
            plt.plot(distances, forces, label=f'Messung {i}')

        plt.xlabel('Distance [µm]')
        plt.ylabel('Force [N]')
        plt.title('Pull-Out Messungen')
        plt.legend()
        plt.grid(True)

        plt.savefig(save_path)
        plt.close()