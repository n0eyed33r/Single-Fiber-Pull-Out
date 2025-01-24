import SFPO_config
import pandas as pd


def datawrangling():
    # new .txt file name - measurement naming
    if any(letter[2] == "x" or letter[2]
           == "a" for letter in SFPO_config.filenames):
        # alle str in Liste speichern die ausgezogen wurden
        SFPO_config.acceptresults = \
            [y for y in SFPO_config.filenames if
             y[2] == "a" and y[3] == "_"]
        #  save all str in list that were not undressed, abort
        SFPO_config.abortresults = \
            [y for y in SFPO_config.filenames if
             y[2] == "x" and y[3] == "a"]
    #  old .txt file name - measurement naming
    else:
        #  save all str in list that have been extracted
        SFPO_config.acceptresults = \
            [y for y in SFPO_config.filenames if
             y[-2] != "x" and y[-1] == "a"]
        # alle str in Liste speichern die nicht ausgezogen wurden, abbruch
        SFPO_config.abortresults = \
            [y for y in SFPO_config.filenames if
             y[-2] == "x" and y[-1] == "a"]


def datainput():
    for messung in range(len(SFPO_config.acceptresults)):
        # i.th document import
        df = pd.read_csv(
            str(SFPO_config.rootname[0]) + "\\" +
            str(SFPO_config.acceptresults[messung] + '.txt'),
            delimiter="\t",
            header=None,
            skiprows=40,
            encoding='unicode_escape',
            names=["Time", "Distance", "Force"],
            usecols=["Distance", "Force"])
        # have a look
        # drop the shit (negative values)
        minusvalweg = df[(df["Distance"] <= 0)].index
        df.drop(minusvalweg, inplace=True)
        minusvalweg = df[(df["Distance"] >= 1000)].index
        df.drop(minusvalweg, inplace=True)
        minusvalkraft = df[(df["Force"] < 0)].index
        df.drop(minusvalkraft, inplace=True)
        # create tuple and save to list
        tuples = [
            (x, y) for x, y in zip(df["Distance"], df["Force"])]
        SFPO_config.measurements.append(tuples)


def fiberdiameter():
    for messung in range(len(SFPO_config.acceptresults)):
        # i.th document import
        df = pd.read_csv(
            str(SFPO_config.rootname[0]) + "\\" +
            str(SFPO_config.acceptresults[messung] + '.txt'),
            delimiter='\t',
            header=None,
            encoding='unicode_escape',
            skiprows=19,
            nrows=1)
        value = df.iloc[0, 1]
        # value in line 0, column 1
        SFPO_config.fiberdiameters.append(value)


def forcefiberkink():
    # import from csv (handmade selected Fd)
    for messung in range(len(SFPO_config.acceptresults)):
        # i.th document import
        df = pd.read_csv(
            str(SFPO_config.rootname[0]) + "\\" +
            str(SFPO_config.acceptresults[messung] + '.txt'),
            delimiter='\t',
            header=None,
            encoding='unicode_escape',
            skiprows=24,
            nrows=1)
        value = df.iloc[0, 1]
        # value in line 0, column 1
        SFPO_config.forcefiberkinks.append(value)
