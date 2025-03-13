"""
this code was made with the help of chatgpt, claude, stackoverflow .... u name it
"""
# src/core/file_handler.py
from pathlib import Path
from tkinter import filedialog
import tkinter as tk
from typing import Optional
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
    
    @staticmethod
    def select_statistical_options():
        """
        Zeigt ein Fenster zur Auswahl statistischer Analysemethoden (Bootstrap und ANOVA).

        Returns:
            dict: Dictionary mit den ausgewählten Optionen
        """
        # Erstelle das Hauptfenster
        root = tk.Tk()
        root.title("SFPO Analyzer - Statistische Methoden")
        
        # Zentriere das Fenster
        window_width = 450
        window_height = 350
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width / 2) - (window_width / 2)
        y = (screen_height / 2) - (window_height / 2)
        root.geometry(f'{window_width}x{window_height}+{int(x)}+{int(y)}')
        
        # Fenster in den Vordergrund
        root.lift()
        root.attributes('-topmost', True)
        
        # Erstelle Variablen für die Optionen
        perform_bootstrap = tk.BooleanVar(value=False)
        perform_anova = tk.BooleanVar(value=False)
        bootstrap_samples = tk.IntVar(value=1000)
        anova_target_size = tk.IntVar(value=10)
        create_statistical_plots = tk.BooleanVar(value=True)
        
        # Ergebnisse speichern
        result_dict = {}
        
        # Hauptframe für alle Elemente
        main_frame = tk.Frame(root, padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Überschrift
        header_label = tk.Label(
            main_frame,
            text="Statistische Analyse-Optionen",
            font=("Helvetica", 14, "bold")
        )
        header_label.pack(pady=(0, 15))
        
        # Bootstrap-Bereich
        bootstrap_frame = tk.Frame(main_frame)
        bootstrap_frame.pack(fill=tk.X, pady=5, anchor=tk.W)
        
        bootstrap_check = tk.Checkbutton(
            bootstrap_frame,
            text="Bootstrap-Analyse durchführen",
            variable=perform_bootstrap,
            font=("Helvetica", 10)
        )
        bootstrap_check.pack(side=tk.LEFT)
        
        # Bootstrap-Samples Bereich
        samples_frame = tk.Frame(main_frame)
        samples_frame.pack(fill=tk.X, pady=5, anchor=tk.W)
        
        samples_label = tk.Label(
            samples_frame,
            text="Anzahl Bootstrap-Stichproben:",
            font=("Helvetica", 10)
        )
        samples_label.pack(side=tk.LEFT, padx=(20, 5))
        
        samples_entry = tk.Entry(
            samples_frame,
            textvariable=bootstrap_samples,
            width=8
        )
        samples_entry.pack(side=tk.LEFT)
        
        # ANOVA-Bereich
        anova_frame = tk.Frame(main_frame)
        anova_frame.pack(fill=tk.X, pady=5, anchor=tk.W)
        
        anova_check = tk.Checkbutton(
            anova_frame,
            text="ANOVA-Analyse durchführen",
            variable=perform_anova,
            font=("Helvetica", 10)
        )
        anova_check.pack(side=tk.LEFT)
        
        # ANOVA-Zielgröße Bereich
        target_frame = tk.Frame(main_frame)
        target_frame.pack(fill=tk.X, pady=5, anchor=tk.W)
        
        target_label = tk.Label(
            target_frame,
            text="Zielgröße für ANOVA-Bootstrap:",
            font=("Helvetica", 10)
        )
        target_label.pack(side=tk.LEFT, padx=(20, 5))
        
        target_entry = tk.Entry(
            target_frame,
            textvariable=anova_target_size,
            width=8
        )
        target_entry.pack(side=tk.LEFT)
        
        # Plot-Option Bereich
        plot_frame = tk.Frame(main_frame)
        plot_frame.pack(fill=tk.X, pady=5, anchor=tk.W)
        
        plot_check = tk.Checkbutton(
            plot_frame,
            text="Erstelle statistische Plots",
            variable=create_statistical_plots,
            font=("Helvetica", 10)
        )
        plot_check.pack(side=tk.LEFT)
        
        # Informationstext
        info_text = (
            "Hinweis: Bootstrap und ANOVA sind rechenintensive Verfahren, "
            "die bei großen Datensätzen längere Zeit in Anspruch nehmen können."
        )
        
        info_label = tk.Label(
            main_frame,
            text=info_text,
            wraplength=380,
            justify=tk.LEFT,
            fg="blue",
            font=("Helvetica", 9, "italic")
        )
        info_label.pack(pady=15)
        
        # Button-Bereich
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        def on_continue():
            result_dict["perform_bootstrap"] = perform_bootstrap.get()
            result_dict["perform_anova"] = perform_anova.get()
            result_dict["bootstrap_samples"] = bootstrap_samples.get()
            result_dict["anova_target_size"] = anova_target_size.get()
            result_dict["create_statistical_plots"] = create_statistical_plots.get()
            root.destroy()
        
        def on_cancel():
            # Bei Abbruch setzen wir Standardwerte (keine statistischen Analysen)
            result_dict["perform_bootstrap"] = False
            result_dict["perform_anova"] = False
            result_dict["bootstrap_samples"] = 1000
            result_dict["anova_target_size"] = 10
            result_dict["create_statistical_plots"] = True
            root.destroy()
        
        # Erstelle Buttons mit ansprechenderem Design
        continue_button = tk.Button(
            button_frame,
            text="Weiter",
            command=on_continue,
            width=15,
            height=2,
            bg="#4CAF50",  # Grün
            fg="white",
            font=("Helvetica", 11, "bold")
        )
        continue_button.pack(side=tk.RIGHT, padx=10)
        
        cancel_button = tk.Button(
            button_frame,
            text="Abbrechen",
            command=on_cancel,
            width=15,
            height=2,
            font=("Helvetica", 11)
        )
        cancel_button.pack(side=tk.LEFT, padx=10)
        
        # Starte den Dialog-Loop
        root.mainloop()
        
        # Nach dem Schließen des Fensters zurückgeben
        if not result_dict:
            # Falls das Fenster geschlossen wurde (X-Button), geben wir Standardwerte zurück
            return {
                "perform_bootstrap": False,
                "perform_anova": False,
                "bootstrap_samples": 1000,
                "anova_target_size": 10,
                "create_statistical_plots": True
            }
        
        return result_dict
    
    @staticmethod
    def perform_statistical_analysis(analyzers_dict: dict, logger, plots_base_folder: Path, config):
        """
        Führt statistische Analysen (Bootstrap und ANOVA) für die Messreihen durch.

        Args:
            analyzers_dict: Dictionary mit Namen und MeasurementAnalyzer-Instanzen
            logger: Logger-Instanz
            plots_base_folder: Basisordner für die Plots
            config: Konfigurationsobjekt mit Analyseeinstellungen
        """
        if not config.perform_bootstrap and not config.perform_anova:
            logger.info("Keine statistischen Analysen ausgewählt. Überspringe diesen Schritt.")
            return
        
        try:
            # Erstelle den Hauptordner für statistische Auswertungen
            stats_folder = plots_base_folder / "statistische_auswertung"
            stats_folder.mkdir(exist_ok=True)
            
            # Importiere und initialisiere den StatisticalAnalyzer
            from src.core.statistical_analysis import StatisticalAnalyzer
            
            logger.info("Initialisiere den Statistical Analyzer...")
            statistical_analyzer = StatisticalAnalyzer(logger=logger)
            
            # Führe die statistischen Analysen durch
            logger.info("Beginne mit der statistischen Analyse...")
            
            # Parameter für die statistische Analyse
            params = {
                'analyzer_dict': analyzers_dict,
                'output_folder': stats_folder,
                'bootstrap_n': config.bootstrap_samples,
                'anova_target_size': config.anova_target_size
            }
            
            # Führe die vollständige statistische Analyse durch
            results = statistical_analyzer.compare_groups(**params)
            
            # Protokolliere die Ergebnisse
            logger.info(f"Statistische Analyse abgeschlossen. Ergebnisse gespeichert in: {stats_folder}")
            
            # Zähle die durchgeführten Analysen
            bootstrap_count = len(results.get('bootstrap', {}))
            anova_count = len(results.get('anova', {}))
            
            if bootstrap_count > 0:
                logger.info(f"Bootstrap-Analyse für {bootstrap_count} Messgrößen durchgeführt.")
            
            if anova_count > 0:
                logger.info(f"ANOVA-Analyse für {anova_count} Messgrößen durchgeführt.")
            
            return results
        
        except Exception as e:
            logger.error(f"Fehler bei der statistischen Analyse: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None