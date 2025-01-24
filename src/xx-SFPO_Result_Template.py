import os  # search txt files in directory
import pandas as pd  # dataframe and so on
import matplotlib.pyplot as plt  # plotting stuff

# Bold font
plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"

# data input arbeit
'''
Data = 'P:\\AG-Fasermodifizierung\\Projekte\\2020\\20_\
SFB_Transregio_280_340018\\00_Rohdaten\\01_SFPO\\05\
_C3B2\\11_C3B2_CF1_T1_30wt_pw_160C_1dc_14d_1000\\'
'''
Data = 'C:\\Users\\Tortelloni\\Nextcloud\\02_Work_synch\\data\\SFPO\\23' \
       '_C3B2_CF1_modMMT1_3wt_160C_1dc_14d_1000\\'

# Sichern der Graphen
'''
Plotsafe = 'P:\\AG-Fasermodifizierung\\Projekte\\2020\\20_\
SFB_Transregio_280_340018\\07_Experimentelles\\02_SFPO_\
Graphen\\__Tonis_Auswertung__\\00_C3B2\\'
'''
Plotsafe = 'C:\\Users\\Tortelloni\\Desktop\\Testumgebung'

# Liste mit den Daten im Ordner
ListFiles = []

# Durch-iterieren des Ordners
for file in os.listdir(Data):
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

for i in range(len(PlotGraphs)):
    # i-tes Dokument einlesen
    df_i = pd.read_csv(
        str(Data) + str(PlotGraphs[i]),
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
    print(str(Data) + str(PlotGraphs[i]))
    print(df_i)
    print(i)
    print("________________\n")

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
'''
# Plot zeigen
plt.show()
'''
# Sichern der Graphik
print(GraphTitel)
print('___\n')
GraphTitel = GraphTitel[:-1]
print('___\n')
print(GraphTitel)
print('___\n')
plt.rcParams["savefig.directory"] = \
    os.chdir(os.path.dirname(str(Plotsafe)))

fig.savefig(str(GraphTitel), dpi=300)
# Und zu
plt.close(fig)
