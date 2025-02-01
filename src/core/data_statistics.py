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

        # Mapping für statistische Berechnungen
        self.data_mapping = {
            'forces': self.max_forces_data,
            'lengths': self.embeddinglengths,
            'diameters': self.fiberdiameters,
            'ifss': self.ifssvalues,
            'works': self.works}

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
            names=["Time", "Distance", "Force"],
            usecols=["Distance", "Force"])
        # Datenbereinigung
        df = df[
            (df["Distance"] > 0) &
            (df["Distance"] < 1000) &
            (df["Force"] >= 0)]
        return list(zip(df["Distance"], df["Force"]))

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
                # Berechnung der IFSS
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
        # Beschränke die Daten auf den Bereich bis zur Einbettlänge
        mask = distance_array <= embedding_length
        limited_distances = distance_array[mask]
        limited_forces = force_array[mask]
        # Sicherheitsprüfung der Datenlängen
        if len(limited_distances) != len(limited_forces):
            raise ValueError("Ungleiche Anzahl von Weg- und Kraftwerten nach Längenbegrenzung")
        # Berechne das Integral (Arbeit)
        work = np.trapezoid(limited_forces, limited_distances)
        return round(work, 2)

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
        self.data_mapping = {
            'forces': self.max_forces_data,
            'lengths': self.embeddinglengths,
            'diameters': self.fiberdiameters,
            'ifss': self.ifssvalues,
            'works': self.works  # Füge die Arbeit zum Mapping hinzu
        }

    def calculate_mean(self, data_type: str) -> float:
        """Berechnet den Mittelwert für einen bestimmten Datentyp."""
        # Aktualisiere das Mapping mit den aktuellen Listen
        self.data_mapping = {
            'forces': self.max_forces_data,
            'lengths': self.embeddinglengths,
            'diameters': self.fiberdiameters,
            'ifss': self.ifssvalues}
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
        """
        Berechnet die Standardabweichung für einen bestimmten Datentyp.
        Args: data_type: String der angibt, welche Daten verwendet werden sollen
              ('forces', 'lengths', 'diameters', 'ifss')
        Returns: Standardabweichung der gewählten Daten
        """
        if data_type not in self.data_mapping:
            raise ValueError(f"Unbekannter Datentyp: {data_type}")
        data = self.data_mapping[data_type]
        if not data:
            return 0.0
        return float(np.std(data))

'''
    def work():  # Integral in Abhaengigkeit der Embeddinglength
        for i in range(len(Config.measurements)):
            messreihe = Config.measurements[i]
            # Verwenden Sie die embeddinglength als das Ende der Messung
            embedding_length = SFPO_config.embeddinglength[i]
            # build array
            x = [tupel[0] for tupel in messreihe]  # Weg
            y = [tupel[1] for tupel in messreihe]  # Kraft
            xarray = np.array(x)
            yarray = np.array(y)
            # embedding length as limitation
            xarrayemblen = xarray[xarray <= embedding_length]
            yarrayemblen = yarray[:len(xarrayemblen)]
            if len(xarrayemblen) == len(yarrayemblen):
                pass  # flag of truth
            else:
                print("Error: x_intervall und y_intervall are not equal")
            integral = np.trapz(yarrayemblen, xarrayemblen)
            SFPO_config.wtotal.append(round(integral, 2))
        # print('Wtotal' + str(SFPO_config.wtotal))

    def workintervall():
    for i in range(len(Config.measurements)):
        messreihe = Config.measurements[i]
        # Verwenden Sie die embeddinglength als das Ende der Messung
        embedding_length = SFPO_config.embeddinglength[i]
        # build array
        x = [tupel[0] for tupel in messreihe]  # Weg
        y = [tupel[1] for tupel in messreihe]  # Kraft
        xarray = np.array(x)
        yarray = np.array(y)
        # embedding length as limitation
        xarrayemblen = xarray[xarray <= embedding_length]
        yarrayemblen = yarray[:len(xarrayemblen)]
        if len(xarrayemblen) == len(yarrayemblen):
            pass  # flag of truth
        else:
            print("Error: x_intervall und y_intervall are not equal")
        integralintervalls = []
        for k in range(10):
            start_percent = k * 10
            end_percent = (k + 1) * 10
            start_x = round(embedding_length * start_percent / 100, 4)
            end_x = round(embedding_length * end_percent / 100, 4)
            # print('Start x: ' + str(start_x))
            # print('End x: ' + str(end_x))
            # print('Difference x: ' + str(round(end_x-start_x,2)))
            # Wählen Sie die X-Werte aus, die in diesem Intervall liegen
            mask = (start_x <= xarrayemblen) & (xarrayemblen <= end_x)
            # print(mask)
            x_intervall = xarrayemblen[mask]
            y_intervall = yarrayemblen[mask]
            # print(len(x_intervall), len(y_intervall))
            if len(x_intervall) == len(y_intervall):
                pass  # flag of truth
            else:
                print("Error: x_intervall und y_intervall are not equal")
            xarray_intervall = np.array(x_intervall)
            yarray_intervall = np.array(y_intervall)
            integral = np.trapz(yarray_intervall, xarray_intervall)
            # print(integral)
            # print('\n')
            integralintervalls.append(round(integral, 2))
        # Speichern der Werte in einer Unterliste in SFPO_config
        Config.tenthints.append(integralintervalls)
    # print(SFPO_config.tenthints)
    # print(type(SFPO_config.tenthints))
    # print(SFPO_config.tenthints)

    def normedintervalls():
        # Durch die Listen in workintervall und wtotal iterieren
        for work_values, wtotal_value in zip(
                SFPO_config.tenthints, SFPO_config.wtotal):
            # Teilen der Werte in work_values durch wtotal_value und speichern der Ergebnisse
            divided_result = [round(x / wtotal_value, 4) for x in work_values]
            # Die Ergebnisse zur Liste divided_values hinzufügen
            SFPO_config.normedintervalls.append(divided_result)

    def statisticnormedinterv():
        data = SFPO_config.normedintervalls
        # Extrahiere die Punkte an jeder Position in den Unterlisten
        all_points = [[dataset[i] for dataset in data] for i in range(len(data[0]))]
        # Berechne den Mittelwert und die Standardabweichung für jeden Punkt
        means = [round(np.mean(points), 3) for points in all_points]
        std_devs = [round(np.std(points), 3) for points in all_points]
        # Berechne die relativen Standardabweichungen
        # (Standardabweichung / Mittelwert)
        relative_std_devs = [round(std_dev / mean, 4) if mean != 0 else 0 for mean, std_dev in zip(means, std_devs)]
        # Rückgabe der Mittelwerte und Standardabweichungen
        SFPO_config.meansnormedintervalls.append(means)
        SFPO_config.stddevsnormedintervalls.append(std_devs)
        SFPO_config.relstddevsnormedintervalls.append(relative_std_devs)

    def meaningless():
        # meaningless diameters
        fiberdmeans = statistics.mean([float(x) for x in Config.fiberdiameters])
        Config.fiberdmean = round(fiberdmeans, 2)
        fiberdmeansstdv = statistics.stdev([float(x) for x in Config.fiberdiameters])
        Config.fiberdmeanstdv = round(fiberdmeansstdv, 2)
        # meaningless force
        maxforcemean = statistics.mean(Config.maxforces)
        Config.meanforce = round(maxforcemean, 2)
        forcestdv = statistics.stdev(Config.maxforces)
        Config.forcestdv = round(forcestdv, 2)
        forcerelstdv = (forcestdv / maxforcemean) * 100 if (
                maxforcemean != 0) else 0
        Config.forcerelstdv = round(forcerelstdv, 2)
        # meaningless work
        averages = []
        for item in Config.wtotal:
            sublist = item  # Die Liste an der zweiten Stelle des Tupels
            sublistmean = np.mean(sublist)
            averages.append(sublistmean)
        # meaningless ifss
        ifssmean = statistics.mean(Config.ifss)
        Config.meanifss = round(ifssmean, 2)
        ifssstdv = statistics.stdev(Config.ifss)
        Config.ifssstdv = round(ifssstdv, 2)
        ifssrelstdv = (ifssstdv / ifssmean) * 100 if (
                ifssmean != 0) else 0
        Config.ifssrelstdv = round(ifssrelstdv, 2)
        # Mittelwert der gemittelten Listen
        meanworkmean = np.mean(averages)
        Config.meanwork = round(meanworkmean, 2)
        workstdv = statistics.stdev(averages)
        Config.workstdv = round(workstdv, 2)
        workrelstdv = (workstdv / meanworkmean) * 100 if (
                meanworkmean != 0) else 0
        Config.workrelstdv = round(workrelstdv, 2)'''

