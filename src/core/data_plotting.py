# src/core/data_plotting.py
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

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
            plt.xticks(np.arange(0, 1001, 200),fontsize=22, fontweight='bold')
            plt.yticks(np.arange(0, 0.31, 0.05),fontsize=22, fontweight='bold')

            # Beschriftungen
            plt.title(name, fontsize=24, fontweight='bold')
            plt.xlabel('Distance [µm]', fontsize=24, fontweight='bold')
            plt.ylabel('Force [N]', fontsize=24, fontweight='bold')
            # Ersetze Unterstriche im Titel durch Leerzeichen
            title = name.replace('_', ' ')
            plt.title(title)

            plt.legend()
            plt.grid(True)

            # Speichere Plot
            plot_path = plots_folder / f"{name}_plot.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()

    @staticmethod
    def create_boxplots(analyzers_dict: dict, plots_folder: Path):
        """Erstellt separate Boxplots für F_max und Arbeit für jede Messreihe."""

        for name, analyzer in analyzers_dict.items():
            # F_max Boxplot für diese Messreihe
            plt.figure(figsize=(10, 6))
            plt.boxplot([analyzer.max_forces_data], labels=[name])
            plt.title(f'Maximalkräfte - {name}', fontsize=24, fontweight='bold')
            plt.ylabel('F_max [N]', fontsize=24, fontweight='bold')
            plt.xlabel('Probe', fontsize=24, fontweight='bold')
            plt.xticks(fontsize=22, fontweight='bold')
            plt.yticks(fontsize=22, fontweight='bold')
            plt.grid(True)

            # Speichere F_max Plot
            fmax_path = plots_folder / f"boxplot_fmax_{name}.png"
            plt.savefig(fmax_path, bbox_inches='tight')
            plt.close()

            # Arbeits-Boxplot für diese Messreihe
            plt.figure(figsize=(10, 3))
            plt.boxplot([analyzer.works], labels=[name])
            plt.title(f'Verrichtete Arbeit - {name}', fontsize=24, fontweight='bold')
            plt.ylabel('Arbeit [µJ]', fontsize=24, fontweight='bold')
            plt.xlabel('Probe', fontsize=24, fontweight='bold')
            plt.xticks(fontsize=22, fontweight='bold')
            plt.yticks(fontsize=22, fontweight='bold')
            plt.grid(True)

            # Speichere Arbeits-Plot
            work_path = plots_folder / f"boxplot_work_{name}.png"
            plt.savefig(work_path, bbox_inches='tight')
            plt.close()