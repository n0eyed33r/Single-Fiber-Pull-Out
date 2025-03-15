"""
this code was made with the help of chatgpt, claude, stackoverflow .... u name it
"""

# src/core/data_statistics.py
from src.config.settings import naming_storage, sort_storage
import logging
from pathlib import Path
import pandas as pd
import numpy as np
import math
from dataclasses import dataclass


@dataclass
class AnalysisConfig:
    """Konfigurationsklasse für die Steuerung der Analyseschritte"""
    # Berechnungen
    calculate_zscores: bool = True
    calculate_force_moduli: bool = True
    calculate_work_intervals: bool = True
    calculate_area_normalized_works: bool = True
    
    # Plot-Erstellung
    create_standard_plots: bool = True  # Kraft-Weg-Diagramme
    create_boxplots: bool = True  # Boxplots für F_max und Arbeit
    create_work_interval_plots: bool = True  # Arbeitsintervalle
    create_normalized_plots: bool = True  # Normierte Arbeitsplots
    create_violin_plots: bool = True  # Violin-Plots
    create_zscore_plots: bool = True  # Z-Score-Plots
    
    # Export
    export_to_excel: bool = True


class MeasurementAnalyzer:
    """
    All calculations and statistical evaluations are performed in this class.
    """
    def __init__(self):
        self.measurements_data = []  # Liste für alle Messungen
        self.max_forces_data = []  # Liste aller Maximalkräfter jeder erfolgreichen Messung
        self.embeddinglengths = []  # Liste aller Einbettlängen
        self.fiberdiameters = []
        self.ifssvalues = []
        self.works = []
        self.work_intervals = []
        self.normed_intervals = []  # Neue Liste für normierte Intervalle
        self.mean_normed_intervals = []  # Mittelwerte
        self.stddev_normed_intervals = []  # Standardabweichungen
        self.rel_stddev_normed_intervals = []  # Relative Standardabweichungen
        self.force_moduli = []  # Liste für die Verbundmodule
        self.area_normalized_works = []  #Liste für flächen normalisierte Auszugsarbeit
        self._update_mapping()

    def _update_mapping(self):
        """ Private Methode zum Aktualisieren des data_mappings.
        Wird intern aufgerufen, wenn das Mapping aktuell sein muss.
        """
        self.data_mapping = {
            'forces': self.max_forces_data,
            'lengths': self.embeddinglengths,
            'diameters': self.fiberdiameters,
            'ifss': self.ifssvalues,
            'works': self.works,
            'work_intervals': self.work_intervals,
            'normed_intervals': self.normed_intervals,
            'mean_normed': self.mean_normed_intervals,
            'stddev_normed': self.stddev_normed_intervals,
            'area_normalized_works': self.area_normalized_works,
            'rel_stddev_normed': self.rel_stddev_normed_intervals,
            'force_modulus': self.force_moduli
        }

    def get_measurement_paths(self) -> list[Path]:
        """
        Creates full paths for all successful measurements.
        """
        return [
            naming_storage.root_path / f"{filename}.txt"
            for filename in sort_storage.good_ones]

    def read_single_measurement(self, file_path: Path) -> list[tuple[float, float]]:
        """
        Reads and processes a single measurement file.
        """
        df = pd.read_csv(
            file_path,
            delimiter="\t",
            header=None,
            skiprows=40,
            encoding='unicode_escape',
            names=["Time", "Displacement", "Force"],
            usecols=["Displacement", "Force"])
        # Datenbereinigung
        df = df[
            (df["Displacement"] > 0) &
            (df["Displacement"] < 1000) &
            (df["Force"] >= 0)]
        return list(zip(df["Displacement"], df["Force"]))

    def read_all_measurements(self):
        """
        Reads and processes all successful measurements.
        """
        measurement_paths = self.get_measurement_paths()
        for path in measurement_paths:
            try:
                measurement_data = self.read_single_measurement(path)
                self.measurements_data.append(measurement_data)
            except Exception as e:
                logger = logging.getLogger('SFPO_Analyzer')
                logger.error(f"Fehler beim Lesen von {path}: {e}")

    def find_max_force_single(self, measurement: list[tuple[float, float]]) -> float:
        """
        Findet die maximale Kraft in einer einzelnen Messung.
        Args: measurement: Liste von (distance, force) Tupeln einer Messung
        Returns: Maximale Kraft als float
        """
        # erstelle Liste mit Kraftwerten
        # Jedes Tupel hat (distance, force) == ([0],[1]), wir wollen nur force, also Index 1
        forces = [point[1] for point in measurement]
        # Finde das Maximum
        max_force = max(forces)
        return max_force

    def find_all_max_forces(self):
        """
        Findet die maximalen Kräfte aller erfolgreichen Messungen
        und speichert sie in dieser Klasse für weitere Berechnungen.
        """
        for measurement in self.measurements_data:
            max_force = self.find_max_force_single(measurement)
            self.max_forces_data.append(max_force)

    def find_single_embeddinglength(self, measurement: list[tuple[float, float]]) -> float:
        # erstelle Liste mit Distanzwerten
        # Jedes Tupel hat (distance, force) == ([0],[1]), wir wollen nur force, also Index 0
        distance = [point[0] for point in measurement]
        # Finde das Maximum
        embeddinglength = max(distance)
        return embeddinglength

    def find_all_embeddinglengths(self):
        for measurement in self.measurements_data:
            max_distance = self.find_single_embeddinglength(measurement)
            self.embeddinglengths.append(max_distance)

    def find_single_fiberdiameter(self, file_path: Path) -> float:
        """Liest den Faserdurchmesser aus einer einzelnen Messdatei."""
        try:
            with open(file_path, 'r') as file:
                for i, line in enumerate(file, 1):
                    if i == 20:
                        diameter_str = line.split('\t')[1].strip()
                        return float(diameter_str)
            raise ValueError(f"Zeile 20 nicht gefunden in {file_path}")
        except Exception as e:
            print(f"Fehler beim Lesen des Faserdurchmessers: {e}")
            return 0.0  # oder einen anderen sinnvollen Standardwert

    def process_all_fiberdiameters(self):
        """Verarbeitet die Faserdurchmesser aller erfolgreichen Messungen."""
        self.fiberdiameters = []  # Liste zurücksetzen

        paths = self.get_measurement_paths()
        print(f"\nVerarbeite {len(paths)} Dateien für Faserdurchmesser:")

        for i, path in enumerate(paths, 1):
            try:
                diameter = self.find_single_fiberdiameter(path)
                print(f"  Datei {i}: Durchmesser = {diameter}")
                self.fiberdiameters.append(diameter)
            except Exception as e:
                print(f"  Fehler bei Datei {i}: {e}")

    def check_data_consistency(self):
        """Überprüft ob alle Datenlisten die gleiche Länge haben und zeigt Details"""
        measurements_len = len(self.measurements_data)
        fiber_len = len(self.fiberdiameters)
        paths_len = len(self.get_measurement_paths())

        print("\nDatenmengen:")
        print(f"Gefundene Dateipfade: {paths_len}")
        print(f"Eingelesene Messungen: {measurements_len}")
        print(f"Gefundene Faserdurchmesser: {fiber_len}")

        if fiber_len != measurements_len:
            print("\nWarnung: Ungleiche Längen!")

            # Zeige die tatsächlichen Daten für Debugging
            print("\nDateipfade:")
            for path in self.get_measurement_paths():
                print(f"  {path}")

            print("\nFaserdurchmesser:")
            for dia in self.fiberdiameters:
                print(f"  {dia}")

        return measurements_len == fiber_len

    def interfaceshearstrength(self):
        """
        Berechnet die scheinbare Grenzflächenscherfestigkeit (IFSS) für alle Messungen.
        """
        # Zuerst sicherstellen, dass wir alle benötigten Werte haben
        if not self.fiberdiameters:
            self.process_all_fiberdiameters()
        # Prüfe Datenkonsistenz
        if not self.check_data_consistency():
            raise ValueError("Ungleiche Anzahl von Messungen und Faserdurchmessern!")
        self.ifssvalues = []  # Liste zurücksetzen
        # Für jede Messung IFSS berechnen
        for i, measurement in enumerate(self.measurements_data):
            try:
                max_force = self.find_max_force_single(measurement)
                embedding_length = self.find_single_embeddinglength(measurement)
                fiber_diameter = self.fiberdiameters[i]
                # Berechnung der IFSS -> F_max/(PI*l_e*d)
                ifss = (max_force / (math.pi * embedding_length * fiber_diameter)) * (10 ** 6)
                self.ifssvalues.append(round(ifss, 2))
            except Exception as e:
                print(f"Fehler bei Messung {i}: {e}")

    def calculate_single_work(self, measurement: list[tuple[float, float]], embedding_length: float) -> float:
        """
        Berechnet die verrichtete Arbeit für eine einzelne Messung durch Integration.
        Args: measurement: Liste von (distance, force) Tupeln einer Messung
            embedding_length: Maximale Einbettlänge für diese Messung
        Returns: float: Berechnete Arbeit in µJ (Mikro-Joule)
        """
        # Extrahiere Weg- und Kraftwerte aus den Tupeln
        distances = [point[0] for point in measurement]
        forces = [point[1] for point in measurement]
        # Konvertiere zu NumPy Arrays für effiziente Berechnung
        distance_array = np.array(distances)
        force_array = np.array(forces)

        # Begrenze embedding_length auf 1000 µm
        max_allowed_length = 1000.0
        embedding_length = min(embedding_length, max_allowed_length)
        # Beschränke die Daten auf den Bereich bis zur Einbettlänge
        mask = distance_array <= embedding_length
        limited_distances = distance_array[mask]
        limited_forces = force_array[mask]

        # Sicherheitsprüfung der Datenlängen
        if len(limited_distances) != len(limited_forces):
            raise ValueError("Ungleiche Anzahl von Weg- und Kraftwerten nach Längenbegrenzung")
        # Berechne das Integral (Arbeit)
        work = np.trapezoid(limited_forces, limited_distances)
        return round(work, 3)

    def calculate_all_works(self):
        """
        Berechnet die verrichtete Arbeit für alle Messungen.
        Speichert die Ergebnisse in self.works für weitere Berechnungen.
        """
        # Initialisiere die Liste für die Arbeitswerte
        self.works = []
        # Für jede Messung die Arbeit berechnen
        for measurement, embedding_length in zip(self.measurements_data, self.embeddinglengths):
            try:
                work = self.calculate_single_work(measurement, embedding_length)
                self.works.append(work)
            except Exception as e:
                print(f"Fehler bei der Arbeitsberechnung: {e}")
        # Aktualisiere das Mapping für statistische Berechnungen
        self.data_mapping.update({'works': self.works})

    def calculate_mean(self, data_type: str) -> float:
        """Berechnet den Mittelwert für einen bestimmten Datentyp."""
        # Aktualisiere das Mapping mit den aktuellen Listen
        self._update_mapping()
        if data_type not in self.data_mapping:
            raise ValueError(f"Unbekannter Datentyp: {data_type}")
        data = self.data_mapping[data_type]
        if not data:
            print("Warnung: Keine Daten in der Liste!")
            return 0.0
        result = float(np.mean(data))
        print(f"Berechneter Mittelwert: {result}")
        return result

    def calculate_stddev(self, data_type: str) -> float:
        """ berechne die Standardabweichung
        """
        self._update_mapping()  # Mapping aktualisieren
        if data_type not in self.data_mapping:
            raise ValueError(f"Unbekannter Datentyp: {data_type}")
        data = self.data_mapping[data_type]
        if not data:
            return 0.0
        return float(np.std(data))

    def calculate_single_work_intervals(self, measurement: list[tuple[float, float]],
                                        embedding_length: float) -> list[float]:
        """
        Berechnet die Arbeit in 10 gleichen Intervallen für eine einzelne Messung.
        Args:   measurement: Liste von (distance, force) Tupeln einer Messung
                embedding_length: Maximale Einbettlänge für diese Messung
        Returns:Liste mit 10 Arbeitswerten, einer für jedes 10%-Intervall
        """
        # Extrahiere Weg- und Kraftwerte
        distances = np.array([point[0] for point in measurement])
        forces = np.array([point[1] for point in measurement])
        # Begrenze embedding_length auf 1000 µm
        max_allowed_length = 1000.0
        embedding_length = min(embedding_length, max_allowed_length)
        # Beschränke auf Einbettlänge
        mask = distances <= embedding_length
        limited_distances = distances[mask]
        limited_forces = forces[mask]
        interval_works = []
        # Berechne Arbeit für jedes 10%-Intervall
        for k in range(10):
            start_percent = k * 10
            end_percent = (k + 1) * 10
            start_x = round(embedding_length * start_percent / 100, 4)
            end_x = round(embedding_length * end_percent / 100, 4)
            # Finde Werte im aktuellen Intervall
            interval_mask = (start_x <= limited_distances) & (limited_distances <= end_x)
            x_interval = limited_distances[interval_mask]
            y_interval = limited_forces[interval_mask]
            if len(x_interval) != len(y_interval):
                print(f"Warnung: Ungleiche Längen im Intervall {k + 1}")
                continue
            if len(x_interval) > 0:  # Prüfe ob Daten im Intervall vorhanden
                integral = np.trapezoid(y_interval, x_interval)
                interval_works.append(round(integral, 3))
            else:
                interval_works.append(0.0)
        return interval_works

    def calculate_all_work_intervals(self):
        """Berechnet die Arbeitsintervalle für alle Messungen."""
        self.work_intervals = []  # Liste zurücksetzen
        for measurement, embedding_length in zip(self.measurements_data, self.embeddinglengths):
            try:
                intervals = self.calculate_single_work_intervals(measurement, embedding_length)
                self.work_intervals.append(intervals)
            except Exception as e:
                print(f"Fehler bei der Intervallberechnung: {e}")
        self._update_mapping()  # Mapping aktualisieren

    def calculate_normed_intervals(self):
        """Normiert die Arbeitsintervalle durch Division durch die Gesamtarbeit."""
        self.normed_intervals = []
        # Iteriere über Intervalle und Gesamtarbeiten
        for intervals, total_work in zip(self.work_intervals, self.works):
            if total_work != 0:  # Verhindere Division durch Null
                normed_values = [round(interval / total_work, 4)
                                 for interval in intervals]
                self.normed_intervals.append(normed_values)
            else:
                print("Warnung: Gesamtarbeit ist 0, überspringen dieser Messung")
        self._update_mapping()

    def calculate_interval_statistics(self):
        """Berechnet statistische Werte für die normierten Intervalle."""
        if not self.normed_intervals:
            print("Keine normierten Intervalle vorhanden")
            return
        # Für jede Intervallposition (0-9) über alle Messungen
        n_intervals = len(self.normed_intervals[0])  # Sollte 10 sein
        # Sammle Werte für jede Position
        interval_positions = [[] for _ in range(n_intervals)]
        for normed_measurement in self.normed_intervals:
            for i, value in enumerate(normed_measurement):
                interval_positions[i].append(value)
        # Berechne Statistiken für jede Position
        self.mean_normed_intervals = []
        self.stddev_normed_intervals = []
        self.rel_stddev_normed_intervals = []
        for values in interval_positions:
            mean = np.mean(values)
            stddev = np.std(values)
            rel_stddev = (stddev / mean) if mean != 0 else 0
            self.mean_normed_intervals.append(round(mean, 3))
            self.stddev_normed_intervals.append(round(stddev, 3))
            self.rel_stddev_normed_intervals.append(round(rel_stddev, 4))
        self._update_mapping()
    
    def get_cumulative_normed_work_statistics(self) -> dict:
        """
        Berechnet die kumulativen statistischen Kennwerte der normierten Arbeit.
        Nutzt die bestehenden Berechnungsmethoden für Mittelwert und Standardabweichung.

        Returns:
            Dictionary mit den kumulativen Werten für jede 10%-Position (10% bis 100%)
        """
        if not self.normed_intervals:
            print("Keine normierten Intervalle vorhanden")
            return {}
        
        statistics = {}
        
        # Für jede Position (10% bis 100%) berechnen wir die kumulative Summe
        for position in range(1, 11):  # 1 bis 10 für 10% bis 100%
            # Sammle kumulative Summen bis zu dieser Position
            cumulative_sums = []
            for measurement in self.normed_intervals:
                cum_sum = sum(measurement[:position])
                cumulative_sums.append(cum_sum)
            
            # Berechne Statistiken mit den bestehenden Methoden
            mean = np.mean(cumulative_sums)
            std = np.std(cumulative_sums)
            
            position_key = f"{position * 10}%"
            statistics[position_key] = {
                "mean": round(mean, 4),
                "std": round(std, 4)
            }
        
        return statistics
    
    def calculate_z_scores(self, data: list) -> dict:
        """Berechnet klassische und robuste Z-Scores für einen Datensatz.
        Args:
            data: Liste der Messwerte
        Returns:
            Dictionary mit beiden Z-Score Arten und zusätzlichen Statistiken
        """
        import numpy as np
        
        # Konvertiere zu NumPy-Array und entferne NaN-Werte
        data_array = np.array(data)
        data_array = data_array[~np.isnan(data_array)]
        
        if len(data_array) < 2:
            print("Warnung: Zu wenige Datenpunkte für Z-Score Berechnung")
            return {
                'z_scores': np.zeros_like(data_array),
                'robust_z_scores': np.zeros_like(data_array),
                'mean': 0,
                'std': 0,
                'median': 0,
                'iqr': 0
            }
        
        # Klassische Statistiken
        mean = np.mean(data_array)
        std = np.std(data_array)
        z_scores = np.zeros_like(data_array) if std == 0 else (data_array - mean) / std
        
        # Robuste Statistiken
        median = np.median(data_array)
        iqr = np.percentile(data_array, 75) - np.percentile(data_array, 25)
        robust_scale = iqr / 1.349
        robust_z_scores = np.zeros_like(data_array) if robust_scale == 0 else (data_array - median) / robust_scale
        
        return {
            'z_scores': z_scores,
            'robust_z_scores': robust_z_scores,
            'mean': mean,
            'std': std,
            'median': median,
            'iqr': iqr
        }
    
    def get_z_score_data(self) -> dict:
        """
        Berechnet Z-Scores für alle relevanten Messgrößen.
        Returns: Dictionary mit Z-Scores für verschiedene Messgrößen
        """
        return {
            'forces': self.calculate_z_scores(self.max_forces_data),
            'works': self.calculate_z_scores(self.works),
            'ifss': self.calculate_z_scores(self.ifssvalues),
            'area_normalized_works': self.calculate_z_scores(self.area_normalized_works)
        }
    
    def calculate_area_normalized_works(self):
        """
        Berechnet die flächennormierte Arbeit für jede Messung.

        Die flächennormierte Arbeit wird berechnet als:
        W_A-norm = W / (PI * d * l_e)

        wobei:
        - W: Arbeit [µJ]
        - d: Faserdurchmesser [µm]
        - l_e: Einbettlänge [µm]

        Dies normiert die Arbeit auf die Mantelfläche und führt zu
        Werten in der Einheit µJ/µm².
        """
        import math
        
        self.area_normalized_works = []  # Liste zurücksetzen
        
        # Überprüfen, ob alle benötigten Daten vorhanden sind
        if not self.works or not self.fiberdiameters or not self.embeddinglengths:
            print("Warnung: Fehlende Daten für flächennormierte Arbeitsberechnung")
            return
        
        # Überprüfen, ob alle Listen die gleiche Länge haben
        if len(self.works) != len(self.fiberdiameters) or len(self.works) != len(self.embeddinglengths):
            print("Warnung: Ungleiche Längen der Datenlisten")
            print(f"Arbeiten: {len(self.works)}, Durchmesser: {len(self.fiberdiameters)}, "
                  f"Einbettlängen: {len(self.embeddinglengths)}")
            return
        
        # Berechnung der flächennormierten Arbeit für jede Messung
        for work, diameter, length in zip(self.works, self.fiberdiameters, self.embeddinglengths):
            # Berechnung der Mantelfläche: PI * d * l_e
            if diameter <= 0 or length <= 0:
                print(f"Warnung: Ungültige Werte bei der Berechnung: d={diameter}, l_e={length}")
                self.area_normalized_works.append(0.0)
                continue
            
            surface_area = math.pi * diameter * length
            
            # Berechnung der flächennormierten Arbeit
            area_norm_work = work / surface_area
            
            # Runden auf 4 Dezimalstellen und Speichern
            self.area_normalized_works.append(round(area_norm_work, 4))
        
        print(f"\nFlächennormierte Arbeit berechnet: {len(self.area_normalized_works)} Werte")
        if self.area_normalized_works:
            mean_value = self.calculate_mean('area_normalized_works')
            std_value = self.calculate_stddev('area_normalized_works')
            print(f"Mittelwert: {mean_value:.4f} µJ/µm²")
            print(f"Standardabweichung: {std_value:.4f} µJ/µm²")
        
        # Mapping aktualisieren
        self._update_mapping()
        
        return self.area_normalized_works
    
    def calculate_force_modulus(self) -> None:
        """
        Berechnet den Verbundmodul (force_modulus) für alle Messungen.

        Der Modul wird aus dem Anstieg zwischen 20% und 70% der Maximalkraft berechnet:
        E_v = (F(70%) - F(20%)) / (s(70%) - s(20%))

        Dabei werden die Messpunkte gesucht, die am nächsten an 20% bzw. 70%
        der Maximalkraft liegen, um eine möglichst genaue Berechnung zu ermöglichen.
        """
        self.force_moduli = []  # Liste zurücksetzen

        for measurement in self.measurements_data:
            try:
                # Finde maximale Kraft und deren Index
                max_point = max(measurement, key=lambda point: point[1])
                max_force = max_point[1]
                max_force_index = measurement.index(max_point)

                # Berechne die exakten Zielwerte (20% und 70% von F_max)
                target_20 = max_force * 0.2
                target_70 = max_force * 0.7

                # Betrachte nur Punkte bis zum Maximum
                points_before_max = measurement[:max_force_index + 1]

                # Finde die Punkte, die am nächsten an 20% und 70% liegen
                point_20 = min(points_before_max,
                               key=lambda p: abs(p[1] - target_20))
                point_70 = min(points_before_max,
                               key=lambda p: abs(p[1] - target_70))

                # Debug-Ausgaben
                print(f"Maximalkraft: {max_force:.2f} N")
                print(f"Zielwerte: 20% = {target_20:.2f} N, 70% = {target_70:.2f} N")
                print(f"Gefundene Punkte:")
                print(f"  20%: Kraft = {point_20[1]:.2f} N, Weg = {point_20[0]:.2f} µm")
                print(f"  70%: Kraft = {point_70[1]:.2f} N, Weg = {point_70[0]:.2f} µm")

                # Prüfe, ob die Punkte in der richtigen Reihenfolge sind
                if point_20[0] >= point_70[0]:
                    print("Warnung: 20%-Punkt liegt nach 70%-Punkt - Messung übersprungen")
                    self.force_moduli.append(0.0)
                    continue

                # Berechne den Verbundmodul
                delta_force = point_70[1] - point_20[1]  # Kraftdifferenz in N
                delta_distance = point_70[0] - point_20[0]  # Wegdifferenz in µm

                modulus = delta_force / delta_distance  # Ergebnis in N/µm
                self.force_moduli.append(round(modulus, 4))

                print(f"Verbundmodul: {modulus:.4f} N/µm")
                print("------------------------")

            except Exception as e:
                print(f"Fehler bei der Modulberechnung: {e}")
                self.force_moduli.append(0.0)

        # Aktualisiere das Mapping
        self._update_mapping()