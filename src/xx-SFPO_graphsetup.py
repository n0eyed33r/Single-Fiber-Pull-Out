import SFPO_config
import matplotlib.pyplot as plt


dpi = 300  # gewünschte DPI
pxwidth = 1600  # gewünschte Breite (4:3)
pxheight = 1200  # gewünschte Höhe (4:3)

inchwidth = pxwidth / dpi  # Umrechnung der Pixelangaben in Zoll
inchheight = pxheight / dpi  # Umrechnung der Pixelangaben in Zoll

def create_graph():
    # Figure und Achsen generieren
    fig, ax = plt.subplots(figsize=(inchwidth,inchheight), dpi=dpi)
    # Graph zuschneiden
    ax.axis([0, 1000, 0, 0.3])
    # Beschriftung aka Labels Schriftart
    labelfont = {'fontname': 'Arial'}
    titlefont = {'fontname': 'Arial'}
    # Benennung der Achsen
    ax.set_xlabel(
        'Displacement (µm)',
        fontsize=14,
        fontweight='bold',
        **labelfont
    )
    ax.set_ylabel(
        'Force (N)',
        fontsize=14,
        fontweight='bold',
        **labelfont
    )
    ax.tick_params(axis='both', labelsize=14, width=3)
    for tick in ax.get_xticklabels() + ax.get_yticklabels():
        tick.set_fontweight('bold')
    graphtitel = SFPO_config.mainfolder
    # Getitelt
    ax.set_title(
        'SFPO' + '\n' + str(graphtitel),
        fontsize=11,
        fontweight='bold',
        **titlefont)
    # Rahmen Details
    ax.spines["top"].set_linewidth(3)
    ax.spines["bottom"].set_linewidth(3)
    ax.spines["left"].set_linewidth(3)
    ax.spines["right"].set_linewidth(3)
    # Ticks Timmmyyyyy
    ax.tick_params(
        axis='x',
        labelsize=13,
        which='major',
        direction='out',
        width=3
    )
    ax.tick_params(
        axis='y',
        labelsize=13,
        which='major',
        direction='out',
        width=3
    )
    # Anpassen des Layouts, um Platz für die Achsenbeschriftung zu schaffen
    plt.subplots_adjust(left=0.11, right=0.9, top=0.9, bottom=0.12)
    # Tight Layout hinzufügen
    plt.tight_layout()

