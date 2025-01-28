"""
this code was made with the help of chatgpt, claude, stackoverflow .... u name it
"""
# src/core/data_plotting.py
import matplotlib.pyplot as plt
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
        """Plots all successful measurements in one graph."""

        plt.figure(figsize=(10, 6))
        # Access to measurement data via the analyzer
        # Debugging: Ausgabe der Anzahl der Messungen
        print(f"Anzahl der Messungen zum Plotten: {len(self.analyzer.measurements_data)}")

        for i, measurement in enumerate(self.analyzer.measurements_data, 1):
            # Debugging: Ausgabe der Datenpunkte pro Messung
            print(f"Messung {i}: {len(measurement)} Datenpunkte")

            # Sicherstellung, dass measurement Daten enthält
            if not measurement:
                print(f"Warnung: Messung {i} ist leer")
                continue

            distances, forces = zip(*measurement)
            plt.plot(distances, forces, label=f'Messung {i}')

        plt.xlabel('Distance [µm]')
        plt.ylabel('Force [N]')
        plt.title('Pull-Out Messungen')
        plt.legend()
        plt.grid(True)
        plt.show()