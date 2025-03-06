"""
this code was made with the help of chatgpt, claude, gemini, stackoverflow .... u name it .. u gasp it
"""

# src/config/config_manager.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml
import json
import logging


@dataclass
class MaterialParameters:
    """Materialparameter für den Single-Fiber-Pull-Out Test."""
    elastic_modulus_fiber: float = 250.0  # GPa
    elastic_modulus_matrix: float = 43.0  # GPa
    shear_modulus_fiber: float = 17.0  # GPa
    shear_modulus_matrix: float = 18.0  # GPa
    matrix_radius: float = 1300.0  # µm


@dataclass
class PathSettings:
    """Verwaltung von Pfaden und Dateinamen."""
    root_path: Optional[Path] = None
    main_folder: str = ""
    filenames: List[str] = field(default_factory=list)

    def update_paths(self, new_path: Path) -> None:
        """
        Aktualisiert die Pfadeinstellungen mit einem neuen Hauptpfad.
        Setzt auch die Dateinamenliste zurück.
        """
        if not isinstance(new_path, Path):
            raise TypeError(f"new_path muss vom Typ Path sein, nicht {type(new_path)}")

        if not new_path.exists():
            raise ValueError(f"Der angegebene Pfad existiert nicht: {new_path}")

        self.root_path = new_path
        self.main_folder = new_path.name
        self.filenames = []  # wird später mit Messdateinamen gefüllt

        logger = logging.getLogger('SFPO_Analyzer')
        logger.info(f"Pfadeinstellungen aktualisiert: {new_path}")


@dataclass
class MeasurementClassification:
    """Klassifizierung der Messungen in erfolgreiche und fehlgeschlagene."""
    successful_measurements: List[str] = field(default_factory=list)
    failed_measurements: List[str] = field(default_factory=list)

    def clear(self):
        """Setzt alle Listen zurück."""
        self.successful_measurements = []
        self.failed_measurements = []

    @property
    def successful_count(self) -> int:
        """Anzahl der erfolgreichen Messungen."""
        return len(self.successful_measurements)

    @property
    def failed_count(self) -> int:
        """Anzahl der fehlgeschlagenen Messungen."""
        return len(self.failed_measurements)

    @property
    def total_count(self) -> int:
        """Gesamtanzahl der analysierten Messungen."""
        return self.successful_count + self.failed_count


@dataclass
class CalculationResults:
    """Ergebnisse aller Berechnungen."""
    measurements: List[tuple] = field(default_factory=list)
    fiber_pullout_ratio: Optional[float] = None
    embedding_lengths: List[float] = field(default_factory=list)
    interface_shear_strength: List[float] = field(default_factory=list)
    work_values: List[float] = field(default_factory=list)


@dataclass
class AnalysisConfig:
    """Konfiguration der Analyse-Parameter."""
    # Berechnungen
    calculate_zscores: bool = False
    calculate_force_moduli: bool = False
    calculate_work_intervals: bool = True

    # Plot-Erstellung
    create_standard_plots: bool = True  # Kraft-Weg-Diagramme
    create_boxplots: bool = True  # Boxplots für F_max und Arbeit
    create_work_interval_plots: bool = True  # Intervalle der Arbeit gemittelt
    create_normalized_plots: bool = True  # Normierte Arbeitsplots
    create_violin_plots: bool = False  # Violin-Plots
    create_zscore_plots: bool = False  # Z-Score-Plots

    # Export
    export_to_excel: bool = True

    @classmethod
    def from_file(cls, config_path: Path) -> 'AnalysisConfig':
        """Lädt Konfiguration aus einer Datei."""
        if not config_path.exists():
            return cls()  # Standardkonfiguration

        if config_path.suffix == '.yaml' or config_path.suffix == '.yml':
            with open(config_path, 'r') as file:
                config_data = yaml.safe_load(file)
        elif config_path.suffix == '.json':
            with open(config_path, 'r') as file:
                config_data = json.load(file)
        else:
            raise ValueError(f"Nicht unterstütztes Konfigurationsformat: {config_path.suffix}")

        return cls(**config_data)


class AppConfig:
    """Zentrale Konfigurationsklasse für die Anwendung."""

    def __init__(self):
        self.material = MaterialParameters()
        self.paths = PathSettings()
        self.classification = MeasurementClassification()
        self.results = CalculationResults()
        self.analysis = AnalysisConfig()

    def save_to_file(self, file_path: Path) -> None:
        """Speichert die aktuelle Konfiguration in einer Datei."""
        # Konvertiere zu serialisierbarem Dict
        config_dict = {
            "material": self._dataclass_to_dict(self.material),
            "analysis": self._dataclass_to_dict(self.analysis)
        }

        # Speichere je nach Dateityp
        if file_path.suffix == '.yaml' or file_path.suffix == '.yml':
            yaml_str = yaml.dump(config_dict, default_flow_style=False)
            with open(file_path, 'w') as file:
                file.write(yaml_str)
        elif file_path.suffix == '.json':
            json_str = json.dumps(config_dict, indent=2)
            with open(file_path, 'w') as file:
                file.write(json_str)
        else:
            raise ValueError(f"Nicht unterstütztes Konfigurationsformat: {file_path.suffix}")

    def reset_for_new_series(self):
        """
        Setzt relevante Teile der Konfiguration zurück,
        wenn eine neue Messreihe analysiert wird.
        """
        # Lösche alte Messungslisten
        self.classification.clear()

        # Setze Ergebnisse zurück
        self.results = CalculationResults()

        logger = logging.getLogger('SFPO_Analyzer')
        logger.info("Konfiguration für neue Messreihe zurückgesetzt")

    @staticmethod
    def _dataclass_to_dict(obj: Any) -> Dict:
        """Konvertiert ein Dataclass-Objekt in ein Dictionary."""
        if hasattr(obj, '__dataclass_fields__'):
            return {field: getattr(obj, field) for field in obj.__dataclass_fields__}
        return {}


# Singleton-Instanz für die gesamte Anwendung
app_config = AppConfig()