import SFPO_config
import matplotlib.pyplot as plt


def plottenmessreihe():
    # Iterieren über jedes Dataset
    for i, data in enumerate(SFPO_config.measurements):
        # falls nur ein Graph anzuschauen ist if an und bist plt.plot einrücken
        #if i == 0:
                #continue
        # Extrahieren der x- und y-Werte aus den Tupeln
        x_values = [tupel[0] for tupel in data]  # Weg
        y_values = [tupel[1] for tupel in data]  # Kraft
        # Farbverlauf definieren
        # Farbverlauf basierend auf 'plasma' oder 'summer' colormap
        color = plt.cm.plasma(i / len(SFPO_config.measurements))
        #Text hinzufügen
        plt.text(0.99, 0.98,
                 f"mean F_max:\n"
                 f"{SFPO_config.meanforce} N +- {SFPO_config.forcestdv}",
                 ha='right', va='top', weight='bold', size=12,
                 transform=plt.gca().transAxes)
        plt.text(0.99, 0.86,
                 f"s.r. from a total of "
                 f"{len(SFPO_config.abortresults) + len(SFPO_config.acceptresults)}:\n"
                 f"{str(SFPO_config.fiberratioresult).replace('[', ' ').replace(']', '%')}",
                 ha='right', va='top', weight='bold', size=12,
                 transform=plt.gca().transAxes)
        plt.text(0.99, 0.74,
                 f"mean work:\n"
                 f"({SFPO_config.meanwork} +- {SFPO_config.workstdv})* 10^(-6) Nm",
                 ha='right', va='top', weight='bold', size=12,
                 transform=plt.gca().transAxes)
        # Plotten der Daten
        plt.plot(x_values
                 ,y_values
                 ,linewidth=1.5
                 #,label=f'Datenreihe {i+1}'  # für die Legende
                 , color=color
                 )
    # Einstellen der Transparenz des Hintergrunds der Achsen
    plt.gca().set_facecolor('none')  # Hintergrund der Achsen transparent machen
    plt.gca().patch.set_alpha(0)  # Transparenz der Achsenhintergrund ändern (Wert zwischen 0 und 1)
    #plt.legend()
    #plt.show()
    return plt

def plottenintegralpkte():
    # Erstelle eine neue Figur und Achsen speziell für die Punkte
    fig, ax = plt.subplots(figsize=(8, 6))  # Pass die Größe nach Bedarf an

    # Iteriere über jedes Dataset
    for i, data in enumerate(SFPO_config.tenthints):
        # Erstelle x-Werte als Mittelpunkte der Bereiche (0-10)%, (10-20)%, usw.
        x_values = [k * 10 + 5 for k in range(len(data) - 1)]
        # Verwende die restlichen Werte als y-Werte
        y_values = data[1:]  # Die restlichen Werte ab Index 1 als y-Werte
        # Farbverlauf definieren
        # Farbverlauf basierend auf 'plasma' oder 'summer' colormap
        color = plt.cm.plasma(i / len(SFPO_config.measurements))
        # Plotten der Daten als Punkte
        ax.scatter(x_values,
                   y_values,
                   s=40,
                   label=f'Datenreihe {i+1}',
                   color=color)
    # Beschriftung der x-Achse
    x_tick_labels = [(f'({i}-{i+10}) %') for i in range(0, 100, 10)]
    x_tick_positions = [i for i in range(5, 100, 10)]
    ax.set_xticks(x_tick_positions)
    ax.set_xticklabels(x_tick_labels)
    # Beschriftungen der x-Achse festlegen
    x_ticks = [f'({i}-{i + 10})%' for i in range(0, 100, 10)]  # z.B., ['(0-10)%', '(10-20)%', ...]
    plt.xticks(range(0, 100, 10), x_ticks, rotation=35, ha='right')
    # Füge Labels und Legende hinzu
    ax.set_xlabel('X-Achsenbeschriftung')
    ax.set_ylabel('Y-Achsenbeschriftung')
    ax.legend()

    # Zeige den Plot an
    #plt.show()
    return plt


def plottennormedwork():
    data = SFPO_config.normedintervalls
    # Festlegen der Abbildungsgröße (in Zoll)
    fig, ax = plt.subplots(figsize=(10, 8))  # Hier können Sie die Größe anpassen
    for i, dataset in enumerate(data):
        x_values = [j * 10 for j in range(10)]  # x-Werte: 0, 10, 20, ..., 90
        y_values = dataset  # y-Werte aus SFPO_config.normedintervalls
        # Linie erstellen
        plt.plot(x_values,
                 y_values, marker='o'
                 , label=f'Dataset {i + 1}')
    # Bereichsgrenzen für x- und y-Achsen festlegen
    plt.xlim(-2.5, 92.5)  # x-Achse von 0% bis 100%
    plt.ylim(0, 0.5)  # y-Achse von 0 bis 1
    # Beschriftungen der x-Achse festlegen
    x_ticks = [f'({i}-{i + 10})%' for i in range(0, 100, 10)]  # z.B., ['(0-10)%', '(10-20)%', ...]
    plt.xticks(range(0, 100, 10), x_ticks, rotation=35, ha='right')
    # Diagrammtitel und Achsenbeschriftungen hinzufügen
    plt.title('Normed Intervalls')
    plt.xlabel('Intervall in Prozent')
    plt.ylabel('Normierte Werte [Wproz/Wsumme]')
    # Anpassen des Layouts, um Platz für die Achsenbeschriftung zu schaffen
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.15)
    # Legende hinzufügen
    plt.legend()
    # Diagramm anzeigen
    plt.show()
    return plt


def plottenmeannormedwork():
    data = SFPO_config.normedintervalls
    means = SFPO_config.meansnormedintervalls
    std_devs = SFPO_config.stddevsnormedintervalls
    # Festlegen der Abbildungsgröße (in Zoll)
    fig, ax = plt.subplots(figsize=(10, 8))  # Hier können Sie die Größe anpassen
    for i, dataset in enumerate(data):
        x_values = [j * 10 for j in range(10)]  # x-Werte: 0, 10, 20, ..., 90
        y_values = dataset  # y-Werte aus SFPO_config.normedintervalls
        mean_values = means[0]
        std_dev_values = std_devs[0]
        # Linie erstellen mit 50% Transparenz
        plt.plot(x_values, y_values, marker='o', alpha=0.3, label=f'Dataset {i + 1}')
        # Mittelwerte als Punkte darstellen
        plt.errorbar(x_values, mean_values, yerr=std_dev_values, linestyle='', marker='o', capsize=5, label=f'Mean {i + 1}')
    # Bereichsgrenzen für x- und y-Achsen festlegen
    plt.xlim(-2.5, 92.5)  # x-Achse von 0% bis 100%
    plt.ylim(0, 0.5)  # y-Achse von 0 bis 1
    # Beschriftungen der x-Achse festlegen
    # z.B., ['(0-10)%', '(10-20)%', ...]
    x_ticks = [f'({i}-{i + 10})%' for i in range(0, 100, 10)]
    plt.xticks(range(0, 100, 10), x_ticks, rotation=35, ha='right')
    # Diagrammtitel und Achsenbeschriftungen hinzufügen
    plt.title('Normed Intervalls')
    plt.xlabel('Intervall in Prozent')
    plt.ylabel('Normierte Werte [Wproz/Wsumme]')
    # Anpassen des Layouts, um Platz für die Achsenbeschriftung zu schaffen
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.15)

    # Legende hinzufügen
    plt.legend()

    # Diagramm anzeigen
    plt.show()
    return plt