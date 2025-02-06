"""
this code was made with the help of chatgpt, claude, stackoverflow .... u name it
"""
# src/core/file_handler.py
from pathlib import Path
from tkinter import filedialog
import tkinter as tk
from typing import Optional, List
from src.config.settings import naming_storage


class FileHandler:
    """
    Use the path naming for further naming and string manipulations
    """

    @staticmethod
    def select_analysis_type() -> str:
        """Zeigt ein Fenster zur Auswahl des Analysetyps"""
        root = tk.Tk()
        root.title("SFPO Analyzer - Analysetyp wählen")
        # Fenster in den Vordergrund
        root.lift()
        root.attributes('-topmost', True)

        # Zentriere das Fenster
        window_width = 300
        window_height = 150
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width / 2) - (window_width / 2)
        y = (screen_height / 2) - (window_height / 2)
        root.geometry(f'{window_width}x{window_height}+{int(x)}+{int(y)}')

        choice = tk.StringVar(value="1")

        tk.Label(root, text="Bitte Analysetyp wählen:").pack(pady=10)
        tk.Radiobutton(root, text="Einzelne Messreihe", variable=choice, value="1").pack()
        tk.Radiobutton(root, text="Alle Messreihen im Ordner", variable=choice, value="2").pack()

        result = []  # Liste für das Ergebnis

        def on_button_click():
            result.append(choice.get())
            root.destroy()

        tk.Button(root, text="Bestätigen", command=on_button_click).pack(pady=20)

        root.mainloop()
        return result[0] if result else "1"

    @staticmethod
    def select_folder(analysis_type: str = '1') -> Optional[Path]:
        root = tk.Tk()
        root.withdraw()  # Hauptfenster verstecken aber initialisieren

        # Dialog-Titel je nach Analysetyp
        title = "Einzelne Messreihe auswählen" if analysis_type == '1' else "Überordner mit Messreihen auswählen"

        # Dialogfenster in den Vordergrund bringen
        root.lift()
        root.attributes('-topmost', True)

        folder_path = filedialog.askdirectory(
            title=title,
            parent=root
        )

        if not folder_path:
            return None

        path_obj = Path(folder_path)
        if analysis_type == '1':
            naming_storage.update_paths(path_obj)
        return path_obj

    @staticmethod
    def get_measurement_series_folders(parent_folder: Path) -> list[Path]:
        """Findet alle Unterordner, die Messreihen enthalten"""
        # Ignoriere spezielle Ordner wie 'plots', 'zscore_plots-auswertung' etc.
        ignore_folders = {'plots', 'zscore_plots-auswertung', 'box_plots-auswertung',
                          'violin_plots-auswertung'}
        return [f for f in parent_folder.iterdir()
                if f.is_dir() and f.name not in ignore_folders]

    @staticmethod
    def find_specimen_files() -> list[str]:
        """find the .txt files"""
        if not naming_storage.root_path:
            raise ValueError("no folder selected")

        specimen_files = []
        for file_path in naming_storage.root_path.rglob("*.txt"):
            specimen_files.append(file_path.stem)

        naming_storage.filenames = specimen_files
        return specimen_files