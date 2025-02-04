"""
this code was made with the help of chatgpt, claude, stackoverflow .... u name it
"""
# src/core/data_plotting.py
import matplotlib.pyplot as plt
import numpy as np
from src.core.data_statistics import MeasurementAnalyzer

class DataPlotter:

    def __init__(self, analyzer: 'MeasurementAnalyzer'):
        self.analyzer = analyzer

    def save_plot(self, save_path: str):
        """Erstellt und speichert den Plot als PNG"""
        plt.figure(figsize=(10, 6))
        # Erstelle eine Farbpalette basierend auf der Anzahl der Messungen
        # plasma_colors wird automatisch die Farben über den gesamten Bereich der Colormap verteilen
        number_of_measurements = len(self.analyzer.measurements_data)
        plasma_colors = plt.cm.plasma(np.linspace(0, 1, number_of_measurements))

        # Plotte jede Messung mit ihrer eigenen Farbe aus der Plasma-Palette
        for i, measurement in enumerate(self.analyzer.measurements_data, 1):
            distances, forces = zip(*measurement)
            plt.plot(distances, forces, label=f'Messung {i}')

        plt.xlabel('Distance [µm]')
        plt.ylabel('Force [N]')
        plt.title('Pull-Out Messungen')
        plt.legend()
        plt.grid(True)

        # Speichere Plot
        plt.savefig(save_path)
        plt.close()  # Schließe Figure um Speicher freizugeben