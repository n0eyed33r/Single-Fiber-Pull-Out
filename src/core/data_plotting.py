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
            plt.figure(figsize=(10, 10))
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

    def create_violin_plots(analyzers_dict: dict, plots_folder: Path):
        """Erstellt Violin Plots mit robusten Statistiken."""
        for name, analyzer in analyzers_dict.items():
            # F_max Violin Plot
            plt.figure(figsize=(10, 6))
            violin_parts = plt.violinplot(analyzer.max_forces_data, showmeans=False, showmedians=True)

            # Formatierung wie gewünscht
            plt.title(f'Maximalkräfte - {name}', fontsize=24, fontweight='bold')
            plt.ylabel('F_max [N]', fontsize=24, fontweight='bold')
            plt.xlabel('Probe', fontsize=24, fontweight='bold')
            plt.xticks([1], [name], fontsize=22, fontweight='bold')
            plt.yticks(fontsize=22, fontweight='bold')

            plt.grid(True)
            plt.savefig(plots_folder / f"violin_fmax_{name}.png", bbox_inches='tight')
            plt.close()

    @staticmethod
    def plot_z_scores(name: str, data_dict: dict, save_path: Path) -> None:
        """
        Erstellt Z-Score Plots für einen Datensatz.

        Args:
            name: Name der Messreihe
            data_dict: Dictionary mit Z-Scores und Statistiken
            save_path: Pfad zum Speichern des Plots
        """
        try:
            # Prüfe, ob alle erforderlichen Daten vorhanden sind
            required_keys = ['z_scores', 'robust_z_scores', 'mean', 'std', 'median', 'iqr']
            if not all(key in data_dict for key in required_keys):
                print(f"Warnung: Fehlende Daten für {name}")
                return

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            fig.suptitle(f'Z-Score Analyse - {name}', fontsize=16)

            # Korrekte Plot-Einstellungen für matplotlib
            plot_settings = {
                's': 100,  # Punktgröße (statt markersize)
                'alpha': 0.6
            }

            points = range(1, len(data_dict['z_scores']) + 1)

            # Klassische Z-Scores
            ax1.scatter(points, data_dict['z_scores'], color='blue', **plot_settings)
            ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=2)
            ax1.axhline(y=2, color='red', linestyle='--', label='±2σ Grenze', linewidth=2)
            ax1.axhline(y=-2, color='red', linestyle='--', linewidth=2)
            ax1.set_title('Klassische Z-Scores', fontsize=24, fontweight='bold')
            ax1.set_xlabel('Messung Nr.', fontsize=24, fontweight='bold')
            ax1.set_ylabel('Z-Score', fontsize=24, fontweight='bold')
            ax1.tick_params(axis='both', which='major', labelsize=22)
            ax1.grid(True, alpha=0.3)
            ax1.legend(fontsize=16)

            # Statistische Information
            stats_text = f'μ = {data_dict["mean"]:.2f}\nσ = {data_dict["std"]:.2f}'
            ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes,
                     verticalalignment='top', fontsize=12)

            # Robuste Z-Scores
            ax2.scatter(points, data_dict['robust_z_scores'], color='green', **plot_settings)
            ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=2)
            ax2.axhline(y=2, color='red', linestyle='--', label='±2σ Grenze', linewidth=2)
            ax2.axhline(y=-2, color='red', linestyle='--', linewidth=2)
            ax2.set_title('Robuste Z-Scores', fontsize=24, fontweight='bold')
            ax2.set_xlabel('Messung Nr.', fontsize=24, fontweight='bold')
            ax2.set_ylabel('Robuster Z-Score', fontsize=24, fontweight='bold')
            ax2.tick_params(axis='both', which='major', labelsize=22)
            ax2.grid(True, alpha=0.3)
            ax2.legend(fontsize=16)

            # Robuste statistische Information
            robust_stats = f'Median = {data_dict["median"]:.2f}\nIQR = {data_dict["iqr"]:.2f}'
            ax2.text(0.02, 0.98, robust_stats, transform=ax2.transAxes,
                     verticalalignment='top', fontsize=12)

            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()

        except Exception as e:
            print(f"Fehler beim Erstellen des Z-Score Plots für {name}: {str(e)}")
            plt.close()  # Stelle sicher, dass Figure geschlossen wird

    @staticmethod
    def create_z_score_plots(analyzers_dict: dict, plots_folder: Path) -> None:
        """
        Erstellt Z-Score Plots für alle Messreihen.

        Args:
            analyzers_dict: Dictionary mit Namen und Analyzern der Messreihen
            plots_folder: Ordner zum Speichern der Plots
        """
        try:
            plots_folder.mkdir(exist_ok=True)

            if not analyzers_dict:
                print("Warnung: Keine Analyzer für Z-Score Plots verfügbar")
                return

            for name, analyzer in analyzers_dict.items():
                try:
                    # Hole Z-Score Daten vom Analyzer
                    z_score_data = analyzer.get_z_score_data()

                    # Erstelle Plots für Maximalkräfte
                    if 'forces' in z_score_data:
                        DataPlotter.plot_z_scores(
                            name=f"{name}_Maximalkraft",
                            data_dict=z_score_data['forces'],
                            save_path=plots_folder / f"z_scores_{name}_fmax.png"
                        )

                    # Erstelle Plots für Arbeiten
                    if 'works' in z_score_data:
                        DataPlotter.plot_z_scores(
                            name=f"{name}_Arbeit",
                            data_dict=z_score_data['works'],
                            save_path=plots_folder / f"z_scores_{name}_work.png"
                        )

                except Exception as e:
                    print(f"Fehler bei der Verarbeitung von {name}: {str(e)}")
                    continue

        except Exception as e:
            print(f"Fehler beim Erstellen der Z-Score Plots: {str(e)}")