# src/core/data_plotting.py
import matplotlib.pyplot as plt
from pathlib import Path


class DataPlotter:
    @staticmethod
    def setup_plot_style():
        """Konfiguriert den grundlegenden Plot-Stil"""
        plt.style.use('default')  # Reset style
        plt.rcParams['lines.linewidth'] = 3
        plt.rcParams['axes.linewidth'] = 3
        plt.rcParams['xtick.major.width'] = 3
        plt.rcParams['ytick.major.width'] = 3

    @staticmethod
    def save_plots_for_series(analyzers_dict: dict, plots_folder: Path):
        """Erstellt und speichert Plots für alle Messreihen."""
        # Verwende Plasma-Farbschema
        colors = plt.cm.plasma(np.linspace(0, 1, 10))  # 10 Farben aus dem Plasma-Schema

        DataPlotter.setup_plot_style()  # Setze Grundstil

        for name, analyzer in analyzers_dict.items():
            plt.figure(figsize=(10, 6))

            # Plot jede Messung mit einer Farbe aus dem Plasma-Schema
            for i, (measurement, color) in enumerate(zip(analyzer.measurements_data, colors)):
                distances, forces = zip(*measurement)
                plt.plot(distances, forces, color=color, label=f'Messung {i + 1}')

            # Achsenlimits und Ticks setzen
            plt.xlim(0, 1000)
            plt.ylim(0, 0.3)
            plt.xticks(np.arange(0, 1001, 200))
            plt.yticks(np.arange(0, 0.31, 0.05))

            # Beschriftungen
            plt.xlabel('Distance [µm]')
            plt.ylabel('Force [N]')
            # Ersetze Unterstriche im Titel durch Leerzeichen
            title = name.replace('_', ' ')
            plt.title(title)

            plt.legend()
            plt.grid(True)

            # Speichere Plot
            plot_path = plots_folder / f"{name}_plot.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()