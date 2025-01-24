import SFPO_config
import os
import tkinter
from tkinter import filedialog


# prevents an empty tkinter window from appearing
tkinter.Tk().withdraw()
# Ordnerpfad mit Dialog erfragen
folderpath = filedialog.askdirectory()
# ausgewaehlten Pfad in Liste speichern
SFPO_config.rootstr.append(str(folderpath))
# Erstellt eine Liste mit Namen der .txt Dateien im Ordner


def specimenname():
    for (root, dirs, files) in os.walk(folderpath):
        for file in files:
            # check the extension of files
            '''print whole path of files read the path, begin at the 
            end and safe the str before the first \\ appear'''
            if file.endswith(".txt"):
                txtfile = \
                    str(os.path.join(root, file)).rpartition('\\')[-1]
                txtfilename = txtfile.split(".")
                SFPO_config.filenames.append(txtfilename[0])


def rootnaming():
    #  config of the rootname for python
    SFPO_config.rootname = \
        [string.replace("/", "\\") for
         string in SFPO_config.rootstr]
    SFPO_config.mainfolder = \
        SFPO_config.rootname[0].rsplit("\\", 1)[-1].replace("_", " ")
