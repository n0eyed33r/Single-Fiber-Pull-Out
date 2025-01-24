import os  # search txt files in directory
import pandas as pd  # dataframe and so on
import matplotlib.pyplot as plt  # plotting stuff
import numpy as np

# Bold font
plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"


# data input ARBEIT
DataSingle = 'P:\\AG-Fasermodifizierung\\Projekte\\2020\\20_SFB_Tr' \
              'ansregio_280_340018\\00_Rohdaten\\01_SFPO\\05_C3B2\\1' \
              '0_C3B2_CF1_T1_30wt_160C_1dc_14d_1000\\16a_POI_C3B2_' \
              'CF1_T1_30wt_160C_1dc_14d_1000.txt'
DataSet = 'C:\\Users\\utech\\Nextcloud\\02_Work_synch\\data\\SFPO_Date' \
          'n\\03_M1b\\CF1_MWl2_3Dip80C'

'''
'data input HEME'
#LAPTOP
DataSingle = 'C:\\Users\\Tortelloni\\Nextcloud\\02_Work_synch\\dat' \
              'a\\SFPO\\23_C3B2_CF1_modMMT1_3wt_160C_1dc_14d_10' \
              '00\\11a_PO_C3B2_CF1_modMMT1_3wt_160C_1dc_14d_10' \
              '00.txt'
DataSet= 'C:\\Users\\Tortelloni\\Nextcloud\\02_Work_synch\\data\\SFPO\\2' \
         '3_C3B2_CF1_modMMT1_3wt_160C_1dc_14d_1000'
'''
'''
#RECHNER
DataSingle = 'C:\\Users\\toniu\\Nextcloud\\02_Work_synch\\dat' \
              'a\\SFPO\\23_C3B2_CF1_modMMT1_3wt_160C_1dc_14d_10' \
              '00\\11a_PO_C3B2_CF1_modMMT1_3wt_160C_1dc_14d_10' \
              '00.txt'
DataSet= 'P:\\AG-Fasermodifizierung\\Projekte\\2020\\20_SFB_Transregi' \
      'o_280_340018\\00_Rohdaten\\01_SFPO\\05_C3B2\\01_C3B2_CF1_' \
      'MMT1_3wt_160C_1dc_14d_1000_kurz'
'''

'Speicherort Lokal'
#Laptop
TxtSave= 'C:\\Users\\Tortelloni\\Desktop\\Testumgebung\\Test12.txt'
Pltsafe = 'C:\\Users\\Tortelloni\\Desktop\\Testumgebung'
'''
#Rechner
TxtSave= 'C:\\Users\\toniu\\Desktop\\Testumgebung\\Test12.txt'
'''

# Liste mit den Daten im Ordner
ListFiles = []
# DurchIterieren des Ordners
for file in os.listdir(DataSet):
    # suche die .txt
    if file.endswith(".txt"):
        ListFiles.append(file)
print(ListFiles)
print("Anzahl der Items ist:" + " " + str(len(ListFiles)))
print(type(ListFiles))
print("________________\n")

# alle Graphen raushauen, die xa inne haben -> Faserbruch
PlotGraphs = [y for y in ListFiles if "xa" not in y]
print(PlotGraphs)
print("Anzahl der Items ist:" + " " + str(len(PlotGraphs)))
print(type(PlotGraphs))
print("________________\n")

# Figure und Achsen generieren
fig, ax = plt.subplots()

#Einzeldatei
'''
# SFPO SingleData
df = pd.read_csv(
    SataSingle,
    delimiter="\t",
    header=None,
    skiprows=40,
    encoding='unicode_escape',
    names=["Dauer", "Weg", "Kraft"],
    usecols=["Weg", "Kraft"])
# drop the shit (negative values)
MinusValWeg = df[(df["Weg"] <= 0)].index
df.drop(MinusValWeg, inplace=True)
MinusValWeg = df[(df["Weg"] >= 1000)].index
df.drop(MinusValWeg, inplace=True)
MinusValKraft = df[(df["Kraft"] < 0)].index
df.drop(MinusValKraft, inplace=True)
'''

for i in range(len(PlotGraphs)):
    # i-tes Dokument einlesen
    df_i = pd.read_csv(
        str(DataSet) + str(PlotGraphs[i]),
        delimiter="\t",
        header=None,
        skiprows=40,
        encoding='unicode_escape',
        names=["Dauer", "Weg", "Kraft"],
        usecols=["Weg", "Kraft"])
    # have a look
    print(df_i)
    # drop the shit (negative values)
    MinusValWeg = df_i[(df_i["Weg"] <= 0)].index
    df_i.drop(MinusValWeg, inplace=True)
    MinusValWeg = df_i[(df_i["Weg"] >= 1000)].index
    df_i.drop(MinusValWeg, inplace=True)
    MinusValKraft = df_i[(df_i["Kraft"] < 0)].index
    df_i.drop(MinusValKraft, inplace=True)
    # Spalten separat als Variablen speichern
    x_i = df_i.iloc[:, 0:1]
    y_i = df_i.iloc[:, 1:2]
    # Graph mit Daten füllen
    ax.plot(
        x_i,
        y_i,
        linewidth=1
    )
    # Sir-vailanz
    print(str(DataSet) + str(PlotGraphs[i]))
    print(df_i)
    print(i)
    print("________________\n")
'''
# Einzeldata
print(df)
print("________________\n")
# Spalten separat als Variablen speichern
x = df.iloc[:, 0:1]
y = df.iloc[:, 1:2]
'''
'''
# in Numpy übersetzen
# aus df zu np.array und joinen
npX = np.concatenate(np.array(x))
# aus df zu np.array und joinen
npY = np.concatenate(np.array(y))
'''
# integrieren Gesamt
Gesamtintegral = np.trapz(npY, npX)
# Integral gesamt zeigen
print("Gesamtintegral ist: " + str(round(Gesamtintegral, 2)))
print("________________\n")
# Figure und Achsen generieren
fig, ax = plt.subplots()
# Graph mit Daten füllen
ax.plot(
    x,
    y,
    linewidth=2)

# Intervalle der verrichteten Arbeit erstellen (10er Split)
IntervalleX = np.array_split(npX,10)
IntervalleY = np.array_split(npY,10)

#Liste für Speichern der erzeugten Intervalle
IntervallIntegrallList= []
# integrieren Intervalle
for i in range(len(IntervalleX)):
    # jedes Intervall soll im Trapezintegral miteinander berechnet
    #werden
    n = np.trapz(IntervalleY[i], IntervalleX[i])
    # Intervallintegrall wird auf 2 Stellen gerundet
    n = round(n,2)
    IntervallIntegrallList.append(n)
# nachschauen der Intervallgrößen
print(IntervallIntegrallList)
print(len(IntervallIntegrallList))
print(round(sum(IntervallIntegrallList),2))
'Speichern der Liste'
# in Pfad Datei öffnen und schreiben
with open(TxtSave, 'w') as tempFile:
    # Indezierung der Liste
    for i in IntervallIntegrallList:
        # schreiben des Wertes und Zeilenumbruch
        tempFile.write("%s\n" % i)
file = open(TxtSave, 'r')
print('\n')
print('Inhalt der Txt Datei')
print(file.read())

# Graph zuschneiden
plt.axis([0, 1000, 0, 0.3])
# Beschriftung aka Labels Schriftart
labelfont = {'fontname': 'Arial'}
titlefont = {'fontname': 'Arial'}
# Benennung der Achsen
ax.set_xlabel(
    'Weg [µm]',
    fontsize=14,
    fontweight='bold',
    **labelfont
)
ax.set_ylabel(
    'Kraft [N]',
    fontsize=14,
    fontweight='bold',
    **labelfont
)
# Titelvergabe Detail
Strsplit = Data.split('_')
print(Strsplit)
print(type(Strsplit))
print(len(Strsplit))
print('___\n')
# Dateipfadabhängigkeit beachten!
StrsplitSort = Strsplit[8:]
print(StrsplitSort)
GraphTitel = '_'.join(StrsplitSort)
print(GraphTitel)
GraphTitel = GraphTitel.replace('\\', '')
# Getiltelt
ax.set_title(
    'SFPO' + '\n' + GraphTitel,
    fontsize=16,
    fontweight='bold',
    **titlefont)
# Rahmen Details
ax.spines["top"].set_linewidth(2)
ax.spines["bottom"].set_linewidth(2)
ax.spines["left"].set_linewidth(2)
ax.spines["right"].set_linewidth(2)
# Ticks Timmmyyyyy
ax.tick_params(
    axis='x',
    labelsize=12,
    which='major',
    direction='out',
    width=2
)
ax.tick_params(
    axis='y',
    labelsize=12,
    which='major',
    direction='out',
    width=2
)

# Arbeit Intervall Daten
dfIntervallArbeit = pd.read_csv(
    TxtSave,
    delimiter="\t",
    header=None,
    encoding='unicode_escape',
    names=["Arbeit"])

# Benennung der Achsen
ax.set_xlabel(
    'Weg [µm]',
    fontsize=14,
    fontweight='bold',
    **labelfont)
ax.set_ylabel(
    'Kraft [N]',
    fontsize=14,
    fontweight='bold',
    ** labelfont)
ax.set_title(
    'SFPO' + '\n' + str(1),
    fontsize=16,
    fontweight='bold',
    **titlefont)

# Rahmen Details
ax.spines["top"].set_linewidth(2)
ax.spines["bottom"].set_linewidth(2)
ax.spines["left"].set_linewidth(2)
ax.spines["right"].set_linewidth(2)

# Ticks
ax.tick_params(
    axis='x',
    labelsize=12,
    which='major',
    direction='out',
    width=2)
ax.tick_params(
    axis='y',
    labelsize=12,
    which='major',
    direction='out',
    width=2)


# Zeige den Graph
plt.show()

'''
# Speichern
savefig()
'''