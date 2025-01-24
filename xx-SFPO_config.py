#______________Materialparameter______________
Ea = float(250)  # in GPa Zugmodul Carbonfaser
Em = float(43)  # in GPa Zugmodul Betonmatrix
Ga = float(17)  # in GPa Schubmodul Carbonfaser
Gm = float(18)  # in GPa Schubmodul Betonmatrix
Rm = float(1300)  # µm Radius des Pfännchen von 2.6 µm Durchmesser
#______________SFPO_01_filesuche.py
filenames = []  # Dateinamen der .txt Dateien
rootname = []
rootstr = []  # Root als str
mainfolder = ""

# ______________SFPO_02_sortierung.py
measurements = []  # Liste der Messungen
fiberdiameters = []  # Liste der Faserdurchmesser für IFSS
forcefiberkinks = []  # Liste der Faserdurchmesser für IFSS

# ______________SFPO_03_rechnen.py
fiberdmean = []
fiberdmeanstdv = float
acceptresults = []  # Liste der erfolgreich Pull-Outs
abortresults = []  # Liste der nicht erfolgreicher Pull-Outs
maxforces = []  # maximalen Kräfte jeder Messung
maxforce_indices = []  # tupel indices of f max to calculate the work before and after
integral_bis_maximal = []
integrale_nach_maximal = []
tenthints = []
gesamtintegrale = []
embeddinglength = []  # maximale Einbettlänge
ifss = []  # interfacial shear stress
wtotal = []  # die jeweilige verrichtete totale Arbeit
wintervall = []  # die Listen der Arbeitsintervalle der Messungen
fiberratioresult = []
meanforce = []  # Durchschnittliche MaxKraft der Messreihe
forcestdv = float  # Standardabweichung der meanforce
forcerelstdv = float
meanifss = []
ifssstdv = float
ifssrelstdv = float
meanwork = []  # Durchschnittliche Arbeit der Messreihe
workstdv = float  # Standardabweichung der meanwork
workrelstdv = float
normedintervalls = []  # normed values for the workintervalls
meansnormedintervalls = []
stddevsnormedintervalls = []
relstddevsnormedintervalls = []