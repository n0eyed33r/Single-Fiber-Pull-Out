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
        
        # Verwende nur EINEN Layout-Manager
        plt.rcParams['figure.autolayout'] = False  # Deaktiviere autolayout
        plt.rcParams['figure.constrained_layout.use'] = False  # Deaktiviere constrained_layout
        
        # Setze größere Schriftarten als Standard
        plt.rcParams['font.size'] = 28
        plt.rcParams['axes.labelsize'] = 34
        plt.rcParams['axes.titlesize'] = 34
        plt.rcParams['xtick.labelsize'] = 30
        plt.rcParams['ytick.labelsize'] = 30
    
    @staticmethod
    def save_plots_for_series(analyzers_dict: dict, plots_folder: Path, max_embedding_length: float = 1000.0):
        """
        Erstellt und speichert Plots für alle Messreihen.

        Args:
            analyzers_dict: Dictionary mit Namen und Analyzern der Messreihen
            plots_folder: Ordner zum Speichern der Plots
            max_embedding_length: Maximale Einbetttiefe für die Achsenskalierung
        """
        # Verwende Plasma-Farbschema
        colors = plt.cm.plasma(np.linspace(0, 1, 10))  # 10 Farben aus dem Plasma-Schema
        
        DataPlotter.setup_plot_style()  # Setze Grundstil
        
        for name, analyzer in analyzers_dict.items():
            # Erstelle Figur und Achsenobjekt
            fig, ax = plt.subplots(figsize=(12, 9), constrained_layout=True)
            
            # Plot jede Messung mit einer Farbe aus dem Plasma-Schema
            for i, (measurement, color) in enumerate(zip(analyzer.measurements_data, colors)):
                distances, forces = zip(*measurement)
                ax.plot(distances, forces, color=color, label=f'Messung {i + 1}')
            
            # Achsenlimits setzen basierend auf der konfigurierten Einbetttiefe
            ax.set_xlim(0, max_embedding_length)
            ax.set_ylim(0, 0.3)
            
            # Tick-Positionen setzen
            tick_step = max_embedding_length / 5  # 5 Ticks auf der x-Achse
            ax.set_xticks(np.arange(0, max_embedding_length + 1, tick_step))
            ax.set_yticks(np.arange(0, 0.31, 0.05))
            
            # Formatierung der Ticks und Labels
            ax.tick_params(axis='both', which='major', pad=2)
            
            # Fettdruck für die Tick-Labels
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontweight('bold')
            
            # Achsenbeschriftungen
            ax.set_xlabel('Displacement [µm]', fontweight='bold', labelpad=2)
            ax.set_ylabel('Force [N]', fontweight='bold', labelpad=2)
            
            # Gitter hinzufügen
            ax.grid(True)
            
            # Optimiere Layout
            fig.tight_layout(pad=2.0)
            
            # Speichere Plot
            plot_path = plots_folder / f"{name}_plot.png"
            fig.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
    
    @staticmethod
    def create_work_interval_plots(analyzers_dict: dict, plots_folder: Path):
        """
        Erstellt Plots für die durchschnittlichen Arbeitsintervalle mit Standardabweichungen.

        Diese Methode visualisiert für jede Messreihe die mittlere Arbeit in jedem 10%-Intervall
        der Einbettlänge. Die Arbeitswerte werden als Balken dargestellt, wobei die Fehlerbalken
        die Standardabweichung anzeigen. Die x-Achse wird in 20%-Schritten beschriftet, während
        die Daten für jedes 10%-Intervall gezeigt werden.

        Args:
            analyzers_dict: Dictionary mit Namen und Analyzern der Messreihen
            plots_folder: Ordner zum Speichern der Plots
        """
        for name, analyzer in analyzers_dict.items():
            plt.figure(figsize=(12, 8))
            
            # X-Positionen für die Balken (zentriert in jedem Intervall)
            x_positions = np.array([5, 15, 25, 35, 45, 55, 65, 75, 85, 95])
            
            # Extrahiere die nicht-normierten Arbeitsintervalle
            interval_values = [[] for _ in range(10)]
            for intervals in analyzer.work_intervals:
                for i, value in enumerate(intervals):
                    interval_values[i].append(value)
            
            # Berechne Mittelwert und Standardabweichung für jedes Intervall
            means = [np.mean(values) for values in interval_values]
            stds = [np.std(values) for values in interval_values]
            
            # Erstelle Balkendiagramm mit Fehlerbalken
            bars = plt.bar(x_positions, means,
                           width=8,  # Breite der Balken
                           color='lightblue',  # Helle Farbe für die Balken
                           edgecolor='blue',  # Blaue Umrandung
                           linewidth=1.5,  # Dicke der Umrandung
                           alpha=0.7,  # Leichte Transparenz
                           label='Mittlere Arbeit pro Intervall')
            
            # Füge Fehlerbalken hinzu
            plt.errorbar(x_positions, means,
                         yerr=stds,
                         fmt='none',  # Keine Verbindungslinien
                         ecolor='red',  # Rote Fehlerbalken
                         elinewidth=1.5,  # Dicke der Fehlerbalken
                         capsize=5,  # Größe der Endkappen
                         capthick=1.5)  # Dicke der Endkappen
            
            # Beschriftungen und Formatierung
            plt.title(f'Arbeitsintervalle - {name}',
                      fontsize=24, fontweight='bold')
            plt.xlabel('Relative Position [%]',
                       fontsize=24, fontweight='bold')
            plt.ylabel('Arbeit [µJ]',
                       fontsize=24, fontweight='bold')
            
            # X-Achse in 20%-Schritten beschriften
            plt.xticks(np.arange(0, 101, 20),
                       fontsize=22, fontweight='bold')
            plt.yticks(fontsize=22, fontweight='bold')
            
            # Füge ein Gitter hinzu (nur horizontale Linien für bessere Lesbarkeit)
            plt.grid(True, axis='y', linestyle='--', alpha=0.7)
            
            # Entferne vertikale Randlinien für einen klareren Look
            plt.gca().spines['right'].set_visible(False)
            plt.gca().spines['top'].set_visible(False)
            
            # Füge eine Legende hinzu
            # plt.legend(fontsize=16, loc='upper right')
            
            # Speichere Plot
            plt.tight_layout()  # Optimiere Layout
            plot_path = plots_folder / f"work_intervals_{name}.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
    
    @staticmethod
    def create_boxplots(analyzers_dict: dict, plots_folder: Path):
        """
        Erstellt Boxplots für F_max, Arbeit und IFSS mit allen Messreihen in jeweils einer Grafik.

        Args:
            analyzers_dict: Dictionary mit Namen und Analyzern der Messreihen
            plots_folder: Ordner zum Speichern der Plots
        """
        # Stelle sicher, dass der Ausgabeordner existiert
        plots_folder.mkdir(exist_ok=True, parents=True)
        
        # Sammle Daten von allen Messreihen
        f_max_data = []
        work_data = []
        ifss_data = []
        labels = []
        
        for name, analyzer in analyzers_dict.items():
            f_max_data.append(analyzer.max_forces_data)
            work_data.append(analyzer.works)
            ifss_data.append(analyzer.ifssvalues)
            # Ersetze Unterstriche durch Leerzeichen für die Beschriftung
            labels.append(name.replace('_', ' '))
        
        # 1. Erstelle Boxplot für F_max
        plt.figure(figsize=(12, 8))
        boxplot = plt.boxplot(f_max_data, patch_artist=True, labels=labels)
        
        # Formatierung des Boxplots
        for box in boxplot['boxes']:
            box.set(facecolor='lightblue', edgecolor='blue', linewidth=2, alpha=0.7)
        for whisker in boxplot['whiskers']:
            whisker.set(color='blue', linewidth=2)
        for cap in boxplot['caps']:
            cap.set(color='blue', linewidth=2)
        for median in boxplot['medians']:
            median.set(color='red', linewidth=2)
        for flier in boxplot['fliers']:
            flier.set(marker='o', markerfacecolor='red', markersize=6, alpha=0.7)
        
        # Beschriftungen und Formatierung
        plt.title('Vergleich der Maximalkräfte', fontsize=24, fontweight='bold')
        plt.ylabel('F_max [N]', fontsize=24, fontweight='bold')
        
        # X-Achsenbeschriftungen drehen
        plt.xticks(rotation=30, ha='right', fontsize=22, fontweight='bold')
        plt.yticks(fontsize=22, fontweight='bold')
        
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Speichere F_max Plot
        fmax_path = plots_folder / "boxplot_fmax_comparison.png"
        plt.savefig(fmax_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Erstelle Boxplot für Arbeit
        plt.figure(figsize=(12, 8))
        boxplot = plt.boxplot(work_data, patch_artist=True, labels=labels)
        
        # Formatierung des Boxplots
        for box in boxplot['boxes']:
            box.set(facecolor='lightgreen', edgecolor='green', linewidth=2, alpha=0.7)
        for whisker in boxplot['whiskers']:
            whisker.set(color='green', linewidth=2)
        for cap in boxplot['caps']:
            cap.set(color='green', linewidth=2)
        for median in boxplot['medians']:
            median.set(color='red', linewidth=2)
        for flier in boxplot['fliers']:
            flier.set(marker='o', markerfacecolor='red', markersize=6, alpha=0.7)
        
        # Beschriftungen und Formatierung
        plt.title('Vergleich der verrichteten Arbeit', fontsize=24, fontweight='bold')
        plt.ylabel('Arbeit [µJ]', fontsize=24, fontweight='bold')
        
        # X-Achsenbeschriftungen drehen
        plt.xticks(rotation=30, ha='right', fontsize=22, fontweight='bold')
        plt.yticks(fontsize=22, fontweight='bold')
        
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Speichere Arbeits-Plot
        work_path = plots_folder / "boxplot_work_comparison.png"
        plt.savefig(work_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Erstelle Boxplot für IFSS
        plt.figure(figsize=(12, 8))
        boxplot = plt.boxplot(ifss_data, patch_artist=True, labels=labels)
        
        # Formatierung des Boxplots
        for box in boxplot['boxes']:
            box.set(facecolor='lightsalmon', edgecolor='orangered', linewidth=2, alpha=0.7)
        for whisker in boxplot['whiskers']:
            whisker.set(color='orangered', linewidth=2)
        for cap in boxplot['caps']:
            cap.set(color='orangered', linewidth=2)
        for median in boxplot['medians']:
            median.set(color='red', linewidth=2)
        for flier in boxplot['fliers']:
            flier.set(marker='o', markerfacecolor='red', markersize=6, alpha=0.7)
        
        # Beschriftungen und Formatierung
        plt.title('Vergleich der Grenzflächenscherfestigkeit', fontsize=24, fontweight='bold')
        plt.ylabel('IFSS [MPa]', fontsize=24, fontweight='bold')
        
        # X-Achsenbeschriftungen drehen
        plt.xticks(rotation=30, ha='right', fontsize=22, fontweight='bold')
        plt.yticks(fontsize=22, fontweight='bold')
        
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Speichere IFSS-Plot
        ifss_path = plots_folder / "boxplot_ifss_comparison.png"
        plt.savefig(ifss_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Erstelle auch noch die einzelnen Boxplots pro Messreihe (falls trotzdem benötigt)
        for i, (name, analyzer) in enumerate(analyzers_dict.items()):
            # F_max Boxplot für diese Messreihe
            plt.figure(figsize=(10, 7))
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
            
            # IFSS-Boxplot für diese Messreihe
            plt.figure(figsize=(10, 10))
            plt.boxplot([analyzer.ifssvalues], labels=[name])
            plt.title(f'Grenzflächenscherfestigkeit - {name}', fontsize=24, fontweight='bold')
            plt.ylabel('IFSS [MPa]', fontsize=24, fontweight='bold')
            plt.xlabel('Probe', fontsize=24, fontweight='bold')
            plt.xticks(fontsize=22, fontweight='bold')
            plt.yticks(fontsize=22, fontweight='bold')
            plt.grid(True)
            
            # Speichere IFSS-Plot
            ifss_path = plots_folder / f"boxplot_ifss_{name}.png"
            plt.savefig(ifss_path, bbox_inches='tight')
            plt.close()
    
    @staticmethod
    def create_combined_normalized_plots(analyzers_dict: dict, plots_folder: Path):
        """
        Erstellt einen gemeinsamen Plot für die mittleren normierten Arbeitsintervalle aller Messreihen.

        Args:
            analyzers_dict: Dictionary mit Namen und Analyzern der Messreihen
            plots_folder: Ordner zum Speichern der Plots
        """
        plt.figure(figsize=(14, 10))
        
        # X-Achse: Positionen für alle 10%-Intervalle
        x_points = np.array([5, 15, 25, 35, 45, 55, 65, 75, 85, 95])  # Mittelpunkte der Intervalle
        
        # Farbschema für verschiedene Messreihen
        colors = plt.cm.tab10(np.linspace(0, 1, len(analyzers_dict)))
        
        # Plotte jede Messreihe mit unterschiedlicher Farbe
        for i, (name, analyzer) in enumerate(analyzers_dict.items()):
            # Berechne Mittelwert und Standardabweichung für jedes Intervall
            interval_values = [[] for _ in range(10)]  # 10 Intervalle
            for measurement in analyzer.normed_intervals:
                for j, value in enumerate(measurement):
                    interval_values[j].append(value)
            
            means = [np.mean(values) for values in interval_values]
            stds = [np.std(values) for values in interval_values]
            
            # Plotte Mittelwertlinie mit Fehlerbalken (korrigiert, um die Warnung zu vermeiden)
            plt.errorbar(x_points, means,
                         yerr=stds,
                         fmt='-',  # Nur die Linie definieren, kein Marker
                         linewidth=2,
                         ecolor=colors[i],
                         elinewidth=1.5,
                         capsize=5,
                         capthick=1.5,
                         color=colors[i],
                         marker='o',  # Marker separat definieren
                         markersize=8,
                         label=name.replace('_', ' '))
        
        # Beschriftungen und Formatierung
        plt.title('Vergleich der mittleren normierten Arbeit aller Messreihen', fontsize=24, fontweight='bold')
        plt.xlabel('Relative Position [%]', fontsize=24, fontweight='bold')
        plt.ylabel('Normierte Arbeit pro Intervall', fontsize=24, fontweight='bold')
        
        # X-Achse in 20%-Schritten beschriften
        plt.xticks(np.arange(0, 101, 20), fontsize=22, fontweight='bold')
        plt.yticks(fontsize=22, fontweight='bold')
        
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(fontsize=20, loc='upper left')
        
        # Speichere Plot
        plot_path = plots_folder / "combined_normalized_work.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    @staticmethod
    def create_normalized_plots(analyzers_dict: dict, plots_folder: Path):
        """
        Erstellt Plots für die normierte Arbeit jeder Messreihe.

        Zeigt die normierte Arbeit für jedes 10%-Intervall, wobei die x-Achse
        in 20%-Schritten beschriftet wird. Jedes Intervall zeigt die normierte
        Arbeit W(Intervall)/W(gesamt) für diesen spezifischen Abschnitt.
        """
        # Verwende Plasma-Farbschema für verschiedene Messungen
        colors = plt.cm.plasma(np.linspace(0, 1, 10))
        
        for name, analyzer in analyzers_dict.items():
            plt.figure(figsize=(10, 8))
            
            # X-Achse: Positionen für alle 10%-Intervalle
            x_points = np.array([5, 15, 25, 35, 45, 55, 65, 75, 85, 95])  # Mittelpunkte der Intervalle
            
            # Plot jede normierte Messung
            for i, normed_measurement in enumerate(analyzer.normed_intervals):
                plt.plot(x_points, normed_measurement,
                         color=colors[i % len(colors)],
                         label=f'Messung {i + 1}',
                         marker='o')  # Marker für bessere Sichtbarkeit der Messpunkte
            
            # Beschriftungen und Formatierung
            plt.title(f'Normierte Arbeit - {name}', fontsize=24, fontweight='bold')
            plt.xlabel('Relative Position [%]', fontsize=24, fontweight='bold')
            plt.ylabel('Normierte Arbeit pro Intervall', fontsize=24, fontweight='bold')
            
            # X-Achse in 20%-Schritten beschriften
            plt.xticks(np.arange(0, 101, 20), fontsize=22, fontweight='bold')
            plt.yticks(fontsize=22, fontweight='bold')
            
            plt.grid(True, linestyle='--', alpha=0.7)
            # plt.legend(fontsize=16)
            
            # Speichere Plot
            plot_path = plots_folder / f"normalized_work_{name}.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
    
    @staticmethod
    def create_mean_normalized_plots(analyzers_dict: dict, plots_folder: Path):
        """
        Erstellt Plots für die Mittelwerte der normierten Arbeit mit Fehlerbalken.

        Zeigt den Mittelwert und die Standardabweichung der normierten Arbeit für
        jedes 10%-Intervall. Die x-Achse wird in 20%-Schritten beschriftet.
        """
        for name, analyzer in analyzers_dict.items():
            plt.figure(figsize=(10, 8))
            
            # X-Achse: Positionen für alle 10%-Intervalle
            x_points = np.array([5, 15, 25, 35, 45, 55, 65, 75, 85, 95])  # Mittelpunkte der Intervalle
            
            # Extrahiere die Werte für jedes Intervall
            interval_values = [[] for _ in range(10)]  # 10 Intervalle
            for measurement in analyzer.normed_intervals:
                for i, value in enumerate(measurement):
                    interval_values[i].append(value)
            
            # Berechne Mittelwert und Standardabweichung für jedes Intervall
            means = [np.mean(values) for values in interval_values]
            stds = [np.std(values) for values in interval_values]
            
            # Plotte Mittelwertlinie mit Fehlerbalken
            plt.errorbar(x_points, means,
                         yerr=stds,
                         fmt='b-',
                         linewidth=2,
                         ecolor='red',
                         elinewidth=1,
                         capsize=5,
                         capthick=1,
                         marker='o',  # Marker für die Datenpunkte
                         label='Mittelwert mit Standardabweichung')
            
            # Beschriftungen und Formatierung
            plt.title(f'Mittlere normierte Arbeit - {name}', fontsize=24, fontweight='bold')
            plt.xlabel('Relative Position [%]', fontsize=24, fontweight='bold')
            plt.ylabel('Normierte Arbeit pro Intervall', fontsize=24, fontweight='bold')
            
            # X-Achse in 20%-Schritten beschriften
            plt.xticks(np.arange(0, 101, 20), fontsize=22, fontweight='bold')
            plt.yticks(fontsize=22, fontweight='bold')
            
            plt.grid(True, linestyle='--', alpha=0.7)
            # plt.legend(fontsize=16)
            
            # Speichere Plot
            plot_path = plots_folder / f"mean_normalized_work_{name}.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
    
    @staticmethod
    def create_area_normalized_work_boxplot(analyzers_dict: dict, plots_folder: Path):
        """
        Erstellt einen Boxplot mit der flächennormierten Arbeit für alle Messreihen.

        Args:
            analyzers_dict: Dictionary mit Namen und Analyzern der Messreihen
            plots_folder: Ordner zum Speichern der Plots
        """
        # Stelle sicher, dass der Ausgabeordner existiert
        plots_folder.mkdir(exist_ok=True, parents=True)
        
        # Sammle Daten von allen Messreihen
        area_norm_work_data = []
        labels = []
        
        for name, analyzer in analyzers_dict.items():
            # Stelle sicher, dass die flächennormierte Arbeit berechnet wurde
            if not hasattr(analyzer, 'area_normalized_works') or not analyzer.area_normalized_works:
                print(f"Warnung: Keine flächennormierten Arbeitsdaten für {name}")
                continue
            
            area_norm_work_data.append(analyzer.area_normalized_works)
            # Ersetze Unterstriche durch Leerzeichen für die Beschriftung
            labels.append(name.replace('_', ' '))
        
        if not area_norm_work_data:
            print("Keine flächennormierten Arbeitsdaten zum Plotten vorhanden")
            return
        
        # Erstelle Boxplot für flächennormierte Arbeit
        plt.figure(figsize=(12, 8))
        boxplot = plt.boxplot(area_norm_work_data, patch_artist=True, labels=labels)
        
        # Formatierung des Boxplots
        for box in boxplot['boxes']:
            box.set(facecolor='lightcyan', edgecolor='teal', linewidth=2, alpha=0.7)
        for whisker in boxplot['whiskers']:
            whisker.set(color='teal', linewidth=2)
        for cap in boxplot['caps']:
            cap.set(color='teal', linewidth=2)
        for median in boxplot['medians']:
            median.set(color='red', linewidth=2)
        for flier in boxplot['fliers']:
            flier.set(marker='o', markerfacecolor='red', markersize=6, alpha=0.7)
        
        # Beschriftungen und Formatierung
        plt.title('Vergleich der flächennormierten Arbeit', fontsize=24, fontweight='bold')
        plt.ylabel('Flächennormierte Arbeit [µJ/µm²]', fontsize=24, fontweight='bold')
        
        # X-Achsenbeschriftungen drehen
        plt.xticks(rotation=30, ha='right', fontsize=22, fontweight='bold')
        plt.yticks(fontsize=22, fontweight='bold')
        
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Speichere Plot
        plot_path = plots_folder / "boxplot_area_normalized_work_comparison.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Erstelle auch einzelne Boxplots für jede Messreihe
        for i, (name, analyzer) in enumerate(analyzers_dict.items()):
            if not hasattr(analyzer, 'area_normalized_works') or not analyzer.area_normalized_works:
                continue
            
            plt.figure(figsize=(10, 10))
            plt.boxplot([analyzer.area_normalized_works], labels=[name])
            plt.title(f'Flächennormierte Arbeit - {name}', fontsize=24, fontweight='bold')
            plt.ylabel('Flächennormierte Arbeit [µJ/µm²]', fontsize=24, fontweight='bold')
            plt.xlabel('Probe', fontsize=24, fontweight='bold')
            plt.xticks(fontsize=22, fontweight='bold')
            plt.yticks(fontsize=22, fontweight='bold')
            plt.grid(True)
            
            # Speichere einzelnen Plot
            single_plot_path = plots_folder / f"boxplot_area_normalized_work_{name}.png"
            plt.savefig(single_plot_path, bbox_inches='tight')
            plt.close()
    
    @staticmethod
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
                    
                    # Erstelle Plots für IFSS
                    if 'ifss' in z_score_data:
                        DataPlotter.plot_z_scores(
                            name=f"{name}_IFSS",
                            data_dict=z_score_data['ifss'],
                            save_path=plots_folder / f"z_scores_{name}_ifss.png"
                        )
                
                except Exception as e:
                    print(f"Fehler bei der Verarbeitung von {name}: {str(e)}")
                    continue
        
        except Exception as e:
            print(f"Fehler beim Erstellen der Z-Score Plots: {str(e)}")
    
    @staticmethod
    def create_area_normalized_work_plot(analyzers_dict: dict, plots_folder: Path):
        """
        Erstellt einen Vergleichsplot für die flächennormierte Arbeit aller Messreihen als Balkendiagramm.

        Diese Methode visualisiert die mittlere flächennormierte Arbeit (µJ/µm²) für jede Messreihe
        als Balkendiagramm mit Fehlerbalken für die Standardabweichung. Dies ermöglicht einen
        schnellen visuellen Vergleich der flächennormierten Arbeit zwischen verschiedenen Proben.

        Args:
            analyzers_dict: Dictionary mit Namen und Analyzern der Messreihen
            plots_folder: Ordner zum Speichern der Plots
        """
        # Stelle sicher, dass der Ausgabeordner existiert
        plots_folder.mkdir(exist_ok=True, parents=True)
        
        # Sammle Daten für alle Messreihen
        labels = []
        mean_values = []
        std_values = []
        
        # Extrahiere Daten aus den Analyzern
        for name, analyzer in analyzers_dict.items():
            if hasattr(analyzer, 'area_normalized_works') and analyzer.area_normalized_works:
                # Entferne NaN-Werte für die statistische Auswertung
                valid_data = [x for x in analyzer.area_normalized_works if not np.isnan(x)]
                
                if valid_data:
                    labels.append(name.replace('_', ' '))
                    mean_values.append(np.mean(valid_data))
                    std_values.append(np.std(valid_data))
        
        if not labels:
            print("Keine gültigen flächennormierten Arbeitsdaten zum Plotten vorhanden")
            return
        
        # Erstelle Balkendiagramm
        plt.figure(figsize=(14, 8))
        
        # Position für die Balken
        x_pos = np.arange(len(labels))
        
        # Farbpalette in Türkis/Blau-Tönen
        colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(labels)))
        
        # Balkendiagramm mit Fehlerbalken
        bars = plt.bar(x_pos, mean_values,
                       yerr=std_values,
                       width=0.6,
                       color=colors,
                       edgecolor='black',
                       linewidth=1.5,
                       capsize=8,
                       alpha=0.8,
                       error_kw={'elinewidth': 2, 'capthick': 2, 'ecolor': 'black'})
        
        # Beschriftungen und Formatierung
        plt.title('Vergleich der flächennormierten Arbeit', fontsize=24, fontweight='bold')
        plt.ylabel('Flächennormierte Arbeit [µJ/µm²]', fontsize=20, fontweight='bold')
        plt.xticks(x_pos, labels, rotation=30, ha='right', fontsize=16, fontweight='bold')
        plt.yticks(fontsize=16, fontweight='bold')
        
        # Gitter für bessere Lesbarkeit
        plt.grid(True, axis='y', linestyle='--', alpha=0.5)
        
        # Entferne obere und rechte Achsenlinien für einen klareren Look
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['top'].set_visible(False)
        
        # Füge Datenwerte über den Balken hinzu
        for i, (bar, mean, std) in enumerate(zip(bars, mean_values, std_values)):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2., height + 0.01 * max(mean_values),
                     f'{mean:.4f} ± {std:.4f}',
                     ha='center', va='bottom', fontsize=12, rotation=0)
        
        # Füge Informationstext hinzu
        info_text = (
            "Die flächennormierte Arbeit W_A-norm = W / (π · d · l_e) normiert\n"
            "die Auszugsarbeit W auf die Mantelfläche der eingebetteten Faser."
        )
        plt.figtext(0.5, 0.01, info_text, ha='center', fontsize=12,
                    bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
        
        # Optimiere Layout
        plt.tight_layout(rect=[0, 0.05, 1, 0.97])
        
        # Speichere Plot
        plot_path = plots_folder / "area_normalized_work_comparison.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Erstelle zusätzlich einen normalisierten Vergleich
        DataPlotter.create_relative_area_normalized_work_plot(analyzers_dict, plots_folder)
    
    @staticmethod
    def create_relative_area_normalized_work_plot(analyzers_dict: dict, plots_folder: Path):
        """
        Erstellt einen normalisierten Vergleichsplot der flächennormierten Arbeit.

        Diese Methode visualisiert die flächennormierte Arbeit relativ zum Mittelwert aller Messreihen,
        was einen direkten prozentualen Vergleich ermöglicht, um Trends und Unterschiede zwischen
        verschiedenen Proben deutlicher hervorzuheben.

        Args:
            analyzers_dict: Dictionary mit Namen und Analyzern der Messreihen
            plots_folder: Ordner zum Speichern der Plots
        """
        # Sammle Daten für alle Messreihen
        labels = []
        mean_values = []
        
        # Extrahiere Daten aus den Analyzern
        for name, analyzer in analyzers_dict.items():
            if hasattr(analyzer, 'area_normalized_works') and analyzer.area_normalized_works:
                # Entferne NaN-Werte für die statistische Auswertung
                valid_data = [x for x in analyzer.area_normalized_works if not np.isnan(x)]
                
                if valid_data:
                    labels.append(name.replace('_', ' '))
                    mean_values.append(np.mean(valid_data))
        
        if not labels or len(mean_values) < 2:
            # Nicht genug Daten für einen Vergleich
            return
        
        # Berechne den Gesamtmittelwert über alle Messreihen
        overall_mean = np.mean(mean_values)
        
        # Berechne relative Werte (Prozent vom Gesamtmittelwert)
        relative_values = [(mean / overall_mean - 1) * 100 for mean in mean_values]
        
        # Erstelle Balkendiagramm
        plt.figure(figsize=(14, 8))
        
        # Position für die Balken
        x_pos = np.arange(len(labels))
        
        # Farbcodierung: rot für negative Abweichung, grün für positive
        colors = ['#ff6b6b' if val < 0 else '#4ecdc4' for val in relative_values]
        
        # Balkendiagramm
        bars = plt.bar(x_pos, relative_values,
                       width=0.6,
                       color=colors,
                       edgecolor='black',
                       linewidth=1.5,
                       alpha=0.8)
        
        # Horizontale Linie bei 0%
        plt.axhline(y=0, color='black', linestyle='-', linewidth=1.5)
        
        # Beschriftungen und Formatierung
        plt.title('Relative Abweichung der flächennormierten Arbeit', fontsize=24, fontweight='bold')
        plt.ylabel('Abweichung vom Mittelwert [%]', fontsize=20, fontweight='bold')
        plt.xticks(x_pos, labels, rotation=30, ha='right', fontsize=16, fontweight='bold')
        plt.yticks(fontsize=16, fontweight='bold')
        
        # Gitter für bessere Lesbarkeit
        plt.grid(True, axis='y', linestyle='--', alpha=0.5)
        
        # Entferne obere und rechte Achsenlinien für einen klareren Look
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['top'].set_visible(False)
        
        # Füge Datenwerte über/unter den Balken hinzu
        for i, (bar, rel_val) in enumerate(zip(bars, relative_values)):
            height = bar.get_height()
            va = 'bottom' if rel_val >= 0 else 'top'
            offset = 1 if rel_val >= 0 else -1
            plt.text(bar.get_x() + bar.get_width() / 2., height + offset,
                     f'{rel_val:.1f}%',
                     ha='center', va=va, fontsize=12, rotation=0)
        
        # Füge Informationstext hinzu
        info_text = (
            f"Durchschnittliche flächennormierte Arbeit über alle Messreihen: {overall_mean:.4f} µJ/µm²\n"
            "Die Balken zeigen die prozentuale Abweichung der einzelnen Messreihen vom Gesamtmittelwert."
        )
        plt.figtext(0.5, 0.01, info_text, ha='center', fontsize=12,
                    bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
        
        # Optimiere Layout
        plt.tight_layout(rect=[0, 0.05, 1, 0.97])
        
        # Speichere Plot
        plot_path = plots_folder / "area_normalized_work_relative_comparison.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()