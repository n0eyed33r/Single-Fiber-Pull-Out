import SFPO_config
import SFPO_04_grapherzeugen


def graphspeichern():
    # speicherformat
    speicherformat = ".png"
    # speicherortangabe vorab
    # achtung!wo gearbeitet wird home vs arbeit
    speicherort = ("C:/Users/toniu/Desktop/test")
    # namensvergabe vorab
    ordnerbezeichnung = str(SFPO_config.rootstr[0])
    last_slash_index = ordnerbezeichnung.rfind('/')
    if last_slash_index != -1:
        ordnerbezeichnung = ordnerbezeichnung[last_slash_index + 1 :]
    # Dialog zum Auswählen des Speicherorts öffnen
    file_path = str(speicherort) + str(ordnerbezeichnung) + str(speicherformat)
    # Plotten des Graphen im Plot-Modul
    plt = \
        SFPO_04_grapherzeugen.plottenmessreihe()
    # Speichern des Graphen
    plt.savefig(file_path, transparent=True)
    plt.close()