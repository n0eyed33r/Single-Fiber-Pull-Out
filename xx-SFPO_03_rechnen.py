import mpmath
import numpy as np
import pandas as pd
import SFPO_config
import SFPO_config as Config
import math
import statistics


def fiberpulloutratio():
    # ratio how many fibers were successfully pulled out
    good = len(Config.acceptresults)
    bad = len(Config.abortresults)
    ratio = (good / (good + bad))
    resultratio = round(ratio, 2)
    Config.fiberratioresult.append(resultratio)


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
        Config.ifss.append(round(ifssvalue,2))


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
    #print('Wtotal' + str(SFPO_config.wtotal))


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
            start_x = round(embedding_length * start_percent / 100,4)
            end_x = round(embedding_length * end_percent / 100,4)
            #print('Start x: ' + str(start_x))
            #print('End x: ' + str(end_x))
            #print('Difference x: ' + str(round(end_x-start_x,2)))
            # Wählen Sie die X-Werte aus, die in diesem Intervall liegen
            mask = (start_x <= xarrayemblen) & (xarrayemblen <= end_x)
            #print(mask)
            x_intervall = xarrayemblen[mask]
            y_intervall = yarrayemblen[mask]
            #print(len(x_intervall), len(y_intervall))
            if len(x_intervall) == len(y_intervall):
                pass  # flag of truth
            else:
                print("Error: x_intervall und y_intervall are not equal")
            xarray_intervall = np.array(x_intervall)
            yarray_intervall = np.array(y_intervall)
            integral = np.trapz(yarray_intervall, xarray_intervall)
            #print(integral)
            #print('\n')
            integralintervalls.append(round(integral, 2))
        # Speichern der Werte in einer Unterliste in SFPO_config
        Config.tenthints.append(integralintervalls)
    #print(SFPO_config.tenthints)
    #print(type(SFPO_config.tenthints))
    #print(SFPO_config.tenthints)


def normedintervalls():
    # Durch die Listen in workintervall und wtotal iterieren
    for work_values, wtotal_value in zip(
            SFPO_config.tenthints, SFPO_config.wtotal):
        # Teilen der Werte in work_values durch wtotal_value und speichern der Ergebnisse
        divided_result = [round(x / wtotal_value,4) for x in work_values]
        # Die Ergebnisse zur Liste divided_values hinzufügen
        SFPO_config.normedintervalls.append(divided_result)


def statisticnormedinterv():
    data = SFPO_config.normedintervalls
    # Extrahiere die Punkte an jeder Position in den Unterlisten
    all_points = [[dataset[i] for dataset in data] for i in range(len(data[0]))]
    # Berechne den Mittelwert und die Standardabweichung für jeden Punkt
    means = [round(np.mean(points),3) for points in all_points]
    std_devs = [round(np.std(points),3) for points in all_points]
    # Berechne die relativen Standardabweichungen
    # (Standardabweichung / Mittelwert)
    relative_std_devs = [round(std_dev / mean,4) if mean != 0 else 0 for mean,std_dev in zip(means, std_devs)]
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
    Config.workrelstdv = round(workrelstdv, 2)
