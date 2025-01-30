"""
this code was made with the help of chatgpt, claude, stackoverflow .... u name it
"""

# src/core/data_statistics.py
from src.config.settings import naming_storage, sort_storage
import logging
from pathlib import Path
import pandas as pd
import numpy as np

class MeasurementAnalyzer:
    """
    All calculations and statistical evaluations are performed in this class.
    """
    def __init__(self):
        self.measurements_data = []  # Liste für alle Messungen
        self.max_forces_data = []  # Liste aller Maximalkräfter jeder erfolgreichen Messung
        self.embeddinglengths = []  # Liste aller Einbettlängen

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

    def mittelwert(self) -> float:
        """
        erzeugt den Mittelwert von Zahlen
        """
        return float(np.mean(self.max_forces_data))

    def standardabweichung_maxmeanforce(self) -> float:
        """
        erzeugt die Standardabweichung der maximalen Kräfte der erfolgreichen Pull Outs
        """
        return float(np.std(self.max_forces_data))

    def find_single_embeddinglength(self, measurement: list[tuple[float, float]]) -> float:
        # erstelle Liste mit Distanzwerten
        # Jedes Tupel hat (distance, force) == ([0],[1]), wir wollen nur force, also Index 0
        distance = [point[0] for point in measurement]
        # Finde das Maximum
        embeddinglength = max(distance)
        return embeddinglength

    def find_all_embeddinglengths(self):
        for measurement in self.measurements_data:
            max_distance = self.find_single_embeddinglength()
            self.embeddinglengths.append(max_distance)

'''
    def calculate_integral(self, force_data, displacement_data):
        # Integration der Kraft-Weg-Kurve
        pass

    def standardize_data(self, data):
        # Standardisierung der Daten
        pass



    def maximalforce():
        # maximal force for each SFPO
        Config.maxforces = [
            (max_value := max(messung, key=lambda tupel: tupel[1]))[1]
            for messung in Config.measurements]
        # Get the index of the max value in each measurement
        Config.maxforce_indices = [
            next(i for i, tupel in enumerate(messung) if
                 tupel[1] == max_value)
            for messung, max_value in
            zip(Config.measurements, Config.maxforces)]

    def embeddinglength():
        for messung in range(len(SFPO_config.acceptresults)):
            # i.th document import
            df = pd.read_csv(
                str(SFPO_config.rootname[0]) + "\\" +
                str(SFPO_config.acceptresults[messung] + '.txt'),
                delimiter='\t',
                header=None,
                encoding='unicode_escape',
                skiprows=26,
                nrows=1)
            value = df.iloc[0, 1]  # value in line 0, column 1
            SFPO_config.embeddinglength.append(value)

    def interfaceshearstrength():  # apparent IFSS - the easy one
        # calculated in N/µm² = 1*10^(12) Pa = 1*10^(6) MPa =
        # 1'000*10^(3) MPa = 1*1'000 GPa
        for messung in range(len(Config.measurements)):
            ifssvalue = (SFPO_config.maxforces[messung] / (
                    math.pi * SFPO_config.embeddinglength[messung]
                    * SFPO_config.fiberdiameters[messung]
            )) * (10 ** 6)  # ** means ^ like 10^(6)
            Config.ifss.append(round(ifssvalue, 2))

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