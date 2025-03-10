"""
this code was made with the help of chatgpt, claude, gemini, stackoverflow .... u name it
"""
# src/core/file_handler.py
from pathlib import Path
from tkinter import filedialog
import tkinter as tk
from typing import Optional, List, Tuple
import logging
from src.config.config_manager import app_config


class FileHandler:
    """
    Verantwortlich für alle Dateisystem-Operationen und die Pfadverwaltung.
    Verwendet Dependency Injection statt globaler Zustandsvariablen.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialisiert den FileHandler mit optionalem Logger.
        Args:logger: Logger-Instanz für Protokollierung (optional)
        """
        self.logger = logger or logging.getLogger('SFPO_Analyzer')

    def select_analysis_type(self) -> str:
        """
        Zeigt ein Fenster zur Auswahl des Analysetyps.

        Returns:
            String mit dem ausgewählten Analysetyp ("1" für Einzelmessung, "2" für alle)
        """
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

    def select_folder(self, analysis_type: str = '1') -> Optional[Path]:
        """
        Öffnet einen Dialog zur Ordnerauswahl.

        Args:
            analysis_type: Typ der Analyse ("1" für Einzelmessung, "2" für alle)

        Returns:
            Pfad zum ausgewählten Ordner oder None, wenn abgebrochen
        """
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
            # Hier verwenden wir die Konfigurationsklasse statt der globalen Variable
            app_config.paths.update_paths(path_obj)
            self.logger.info(f"Ausgewählter Pfad: {path_obj}")
        return path_obj

    def get_measurement_series_folders(self, parent_folder: Path) -> List[Path]:
        """
        Findet alle Unterordner, die Messreihen enthalten.

        Args:
            parent_folder: Übergeordneter Ordner, der durchsucht werden soll

        Returns:
            Liste der gefundenen Messreihenordner
        """
        # Ignoriere spezielle Ordner wie 'plots', 'zscore_plots-auswertung' etc.
        ignore_folders = {'plots', 'zscore_plots-auswertung', 'box_plots-auswertung',
                          'violin_plots-auswertung', 'logs'}

        found_folders = [f for f in parent_folder.iterdir()
                         if f.is_dir() and f.name not in ignore_folders]

        self.logger.info(f"Gefundene Messreihenordner: {len(found_folders)}")
        self.logger.debug(f"Messreihenordner: {[f.name for f in found_folders]}")

        return found_folders

    def find_specimen_files(self) -> List[str]:
        """
        Findet alle .txt Dateien im ausgewählten Ordner und seinen Unterordnern.

        Returns:
            Liste der gefundenen Dateinamen (ohne Erweiterung)

        Raises:
            ValueError: Wenn kein Ordner ausgewählt wurde
        """
        if not app_config.paths.root_path:
            error_msg = "Kein Ordner ausgewählt"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        specimen_files = []
        for file_path in app_config.paths.root_path.rglob("*.txt"):
            specimen_files.append(file_path.stem)

        app_config.paths.filenames = specimen_files
        self.logger.info(f"Gefundene Messdateien: {len(specimen_files)}")

        return specimen_files

    def ensure_output_folders(self, base_folder: Path) -> Tuple[Path, Path, Path, Path]:
        """
        Stellt sicher, dass alle benötigten Ausgabeordner existieren.

        Args:
            base_folder: Basisordner für die Ausgabe

        Returns:
            Tuple mit Pfaden zu den Ausgabeordnern (plots, boxplots, violinplots, zscoreplots)
        """
        # Erstelle Unterordner für die verschiedenen Plot-Typen
        plots_folder = base_folder / "plots"
        boxplots_folder = base_folder / "box_plots-auswertung"
        violinplots_folder = base_folder / "violin_plots-auswertung"
        zscoreplots_folder = base_folder / "zscore_plots-auswertung"

        # Stelle sicher, dass alle Ordner existieren
        for folder in [plots_folder, boxplots_folder, violinplots_folder, zscoreplots_folder]:
            folder.mkdir(exist_ok=True)
            self.logger.debug(f"Ausgabeordner erstellt/geprüft: {folder}")

        return plots_folder, boxplots_folder, violinplots_folder, zscoreplots_folder