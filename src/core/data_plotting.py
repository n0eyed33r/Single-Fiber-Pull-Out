"""
this code was made with the help of chatgpt, claude, stackoverflow .... u name it
"""
# src/core/data_plotting.py
import matplotlib.pyplot as plt
import numpy as np
from src.core.data_statistics import MeasurementAnalyzer

class DataPlotter:

    def __init__(self, analyzer: MeasurementAnalyzer):
        """
        Initialise with a MeasurementAnalyzer instance
        """
        self.analyzer = analyzer
        # Überprüfen, ob der analyzer Daten enthält
        if not hasattr(self.analyzer, 'measurements_data'):
            raise AttributeError("Analyzer hat keine measurements_data")
        if not self.analyzer.measurements_data:
            raise ValueError("Keine Messdaten im Analyzer vorhanden")

    def plot_measurements(self):
        """
        Plots all successful measurements in one graph using a plasma colormap.
        The colormap transitions from dark purple to yellow, making it easy to
        distinguish between different measurements.
        """

        plt.figure(figsize=(10, 6))

        # Erstelle eine Farbpalette basierend auf der Anzahl der Messungen
        # plasma_colors wird automatisch die Farben über den gesamten Bereich der Colormap verteilen
        number_of_measurements = len(self.analyzer.measurements_data)
        plasma_colors = plt.cm.plasma(np.linspace(0, 1, number_of_measurements))

        # Plotte jede Messung mit ihrer eigenen Farbe aus der Plasma-Palette
        for i, (measurement, color) in enumerate(zip(self.analyzer.measurements_data, plasma_colors), 1):
            distances, forces = zip(*measurement)
            plt.plot(distances, forces, color=color, label=f'measurement {i}')

        plt.xlabel('Distance [µm]')
        plt.ylabel('Force [N]')
        plt.title('Single Fiber Pull-Out measurements')
        #plt.legend(False)
        plt.grid(True)
        plt.show()