"""
this code was made with the help of chatgpt, claude, gemini, stackoverflow .... u name it
"""
# src/core/file_handler.py
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional, List, Tuple, Dict
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
    
    @staticmethod
    def select_analysis_type() -> str:
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
        
        # Größerer, deutlicherer Button
        tk.Button(root, text="Weiter", command=on_button_click, width=15, height=2, font=("Arial", 10, "bold")).pack(
            pady=20)
        
        # Sicherstellen, dass das Layout aktualisiert wird
        root.update_idletasks()
        
        root.mainloop()
        return result[0] if result else "1"
    
    def select_analysis_types(self) -> dict:
        """
        Zeigt ein Fenster zur Auswahl der durchzuführenden Analysen.

        Returns:
            Dictionary mit Booleschen Werten für die verschiedenen Analysetypen
        """
        root = tk.Tk()
        root.title("SFPO Analyzer - Analysetypen wählen")
        # Fenster in den Vordergrund
        root.lift()
        root.attributes('-topmost', True)

        # Zentriere das Fenster
        window_width = 400
        window_height = 400
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width / 2) - (window_width / 2)
        y = (screen_height / 2) - (window_height / 2)
        root.geometry(f'{window_width}x{window_height}+{int(x)}+{int(y)}')

        # Variablen für die verschiedenen Analysetypen
        standard_plots = tk.BooleanVar(value=True)
        boxplots = tk.BooleanVar(value=True)
        work_interval_plots = tk.BooleanVar(value=True)
        normalized_plots = tk.BooleanVar(value=True)
        violin_plots = tk.BooleanVar(value=False)
        zscore_plots = tk.BooleanVar(value=False)
        do_anova_analysis = tk.BooleanVar(value=True)  # Neue Option für ANOVA-Analyse

        # Label und Rahmen für bessere Struktur
        tk.Label(root, text="Bitte wählen Sie die zu erstellenden Analysen:", font=("Arial", 12)).pack(pady=10)
        
        frame = tk.Frame(root, bd=2, relief=tk.GROOVE)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Checkboxen für die verschiedenen Analysetypen
        tk.Checkbutton(frame, text="Standard Kraft-Weg-Diagramme", variable=standard_plots).pack(anchor=tk.W, padx=20, pady=5)
        tk.Checkbutton(frame, text="Boxplots", variable=boxplots).pack(anchor=tk.W, padx=20, pady=5)
        tk.Checkbutton(frame, text="Arbeitsintervall-Plots", variable=work_interval_plots).pack(anchor=tk.W, padx=20, pady=5)
        tk.Checkbutton(frame, text="Normierte Arbeits-Plots", variable=normalized_plots).pack(anchor=tk.W, padx=20, pady=5)
        tk.Checkbutton(frame, text="Violin-Plots", variable=violin_plots).pack(anchor=tk.W, padx=20, pady=5)
        tk.Checkbutton(frame, text="Z-Score-Plots", variable=zscore_plots).pack(anchor=tk.W, padx=20, pady=5)
        tk.Checkbutton(frame, text="ANOVA-Analyse durchführen", variable=do_anova_analysis).pack(anchor=tk.W, padx=20, pady=5)

        # Dictionary für das Ergebnis
        result = {}

        def on_button_click():
            result.update({
                'create_standard_plots': standard_plots.get(),
                'create_boxplots': boxplots.get(),
                'create_work_interval_plots': work_interval_plots.get(),
                'create_normalized_plots': normalized_plots.get(),
                'create_violin_plots': violin_plots.get(),
                'create_zscore_plots': zscore_plots.get(),
                'do_anova_analysis': do_anova_analysis.get()  # Neue Option speichern
            })
            root.destroy()

        # Größerer, deutlicherer Button
        button_frame = tk.Frame(root)
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Weiter", command=on_button_click, width=15, height=2, font=("Arial", 10, "bold")).pack()

        # Sicherstellen, dass das Layout aktualisiert wird
        root.update_idletasks()
        
        root.mainloop()
        
        return result

    def select_bootstrap_option(self) -> bool:
        """
        Zeigt ein Fenster zur Auswahl, ob Bootstrap-Verfahren verwendet werden sollen.

        Returns:
            Boolean, ob Bootstrap verwendet werden soll
        """
        root = tk.Tk()
        root.title("SFPO Analyzer - Bootstrap-Option")
        
        # Fenster in den Vordergrund
        root.lift()
        root.attributes('-topmost', True)

        # Zentriere das Fenster und mache es etwas größer
        window_width = 400
        window_height = 250
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width / 2) - (window_width / 2)
        y = (screen_height / 2) - (window_height / 2)
        root.geometry(f'{window_width}x{window_height}+{int(x)}+{int(y)}')

        # Verwende grid statt pack für mehr Kontrolle über das Layout
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        choice = tk.BooleanVar(value=False)

        # Label mit Erklärung
        tk.Label(main_frame,
                 text="Soll Bootstrap für die statistische Analyse verwendet werden?",
                 wraplength=350,
                 justify=tk.LEFT).grid(row=0, column=0, sticky="w", pady=(0,10))
        
        tk.Label(main_frame,
                 text="(Bootstrap verbessert die statistische Aussagekraft bei kleinen Stichprobengrößen)",
                 wraplength=350,
                 justify=tk.LEFT,
                 font=("Arial", 8)).grid(row=1, column=0, sticky="w", pady=(0,15))

        # Radiobuttons
        tk.Radiobutton(main_frame,
                       text="Ja, Bootstrap verwenden",
                       variable=choice,
                       value=True).grid(row=2, column=0, sticky="w", padx=20, pady=5)
        
        tk.Radiobutton(main_frame,
                       text="Nein, ohne Bootstrap",
                       variable=choice,
                       value=False).grid(row=3, column=0, sticky="w", padx=20, pady=5)

        result = []  # Liste für das Ergebnis

        def on_button_click():
            result.append(choice.get())
            root.destroy()

        # Separates Frame für den Button, um sicherzustellen, dass er angezeigt wird
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=4, column=0, pady=20)
        
        # Deutlich größerer Button
        tk.Button(button_frame,
                  text="Weiter",
                  command=on_button_click,
                  width=15,
                  height=2,
                  font=("Arial", 10, "bold")).pack()

        # Debug-Ausgabe, um zu überprüfen, ob der Button erstellt wurde
        print("Bootstrap-Dialog: Button wurde erstellt")
        
        # Stellen Sie sicher, dass das Layout aktualisiert wird
        root.update_idletasks()
        
        root.mainloop()
        
        print("Bootstrap-Dialog: Nach mainloop, Ergebnis:", result)
        return result[0] if result else False

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
                         'violin_plots-auswertung', 'logs', 'statistical_analysis'}

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
    
    def get_anova_groups(self, series_folders: List[Path]) -> Dict[str, List[Path]]:
        """
        Gruppiert Messreihen für ANOVA basierend auf gemeinsamen Präfixen oder anderen Merkmalen.
        Ordner mit gleichem Präfix (alles vor dem ersten Unterstrich) werden als eine Gruppe betrachtet.
        
        Args:
            series_folders: Liste der verfügbaren Messreihenordner
            
        Returns:
            Dictionary mit Gruppennamen als Schlüssel und Listen von Pfaden als Werten
        """
        if not series_folders:
            self.logger.warning("Keine Messreihen für ANOVA-Analyse verfügbar")
            return {}
        
        # Dictionary für die Gruppen
        groups = {}
        
        # Gruppiere nach Präfix (alles bis zum ersten Unterstrich)
        for folder in series_folders:
            # Extrahiere den Gruppennamen aus dem Ordnernamen
            group_name = folder.name.split('_')[0] if '_' in folder.name else folder.name
            
            # Füge den Ordner zur entsprechenden Gruppe hinzu
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(folder)
        
        # Protokolliere die gefundenen Gruppen
        self.logger.info(f"ANOVA-Gruppen automatisch erkannt: {len(groups)}")
        for group_name, folders in groups.items():
            self.logger.info(f"Gruppe '{group_name}': {len(folders)} Messreihen")
            self.logger.debug(f"  Messreihen: {[f.name for f in folders]}")
        
        # Filtere Gruppen mit nur einem Element
        valid_groups = {name: folders for name, folders in groups.items() if len(folders) > 1}
        
        if len(valid_groups) != len(groups):
            self.logger.warning(f"{len(groups) - len(valid_groups)} Gruppen mit nur einer Messreihe wurden für ANOVA ignoriert")
        
        if not valid_groups:
            self.logger.warning("Keine gültigen Gruppen für ANOVA gefunden (mindestens 2 Messreihen pro Gruppe erforderlich)")
        
        return valid_groups
    
    # Legacy-Methoden für Kompatibilität
    def select_series_for_anova(self, series_folders: List[Path]) -> Dict[str, List[Path]]:
        """Legacy-Methode, nutzt automatische Gruppierung"""
        return self.get_anova_groups(series_folders)
    
    def select_groups_for_anova(self, series_folders: List[Path]) -> Dict[str, List[Path]]:
        """Legacy-Methode, nutzt automatische Gruppierung"""
        return self.get_anova_groups(series_folders)
    
    def select_anova_output_folder(self) -> Path:
        """
        Gibt den Standardordner für ANOVA-Ergebnisse zurück.
        
        Returns:
            Standardpfad für ANOVA-Ergebnisse
        """
        # Verwende den Elternordner des ersten Serienordners (falls vorhanden)
        if hasattr(self, 'series_folders') and self.series_folders:
            parent_folder = self.series_folders[0].parent
            return parent_folder
            
        # Fallback zum aktuellen Arbeitsverzeichnis
        return Path.cwd()
    
    def ask_continue_anova(self) -> bool:
        """
        Legacy-Methode, gibt immer False zurück (keine weiteren Analysen).
        
        Returns:
            Immer False
        """
        return False