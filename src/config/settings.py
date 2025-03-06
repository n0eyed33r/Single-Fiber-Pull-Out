"""
this code was made with the help of chatgpt, claude, gemini, stackoverflow .... u name it .. u gasp it
"""
# src/config/settings.py
from dataclasses import dataclass
from pathlib import Path

@dataclass
class MaterialParameters:
    """
    material parameters of the single fiber pull-out
    """
    elastic_modulus_fiber: float = 250.0  # GPa
    elastic_modulus_matrix: float = 43.0  # GPa
    shear_modulus_fiber: float = 17.0  # GPa
    shear_modulus_matrix: float = 18.0  # GPa
    matrix_radius: float = 1300.0  # µm


@dataclass
class PathManager:
    """
    Strings and list of strings for files and path names
    """
    filenames: list[str] = None
    root_path: Path = None
    main_folder: str = ""

    def __post_init__(self):
        self.filenames = [] if self.filenames is None else self.filenames

# saving strings from path
    def update_paths(self, new_path: Path):
        self.root_path = new_path
        self.main_folder = new_path.name
        self.filenames = []  # filled later with the names of measurements
# global instancing
naming_storage = PathManager()


@dataclass
class MeasurementClassifier:
    """
    Sort and select the successfully pulled out fibers.
    """
    measurements: list[str] = None  # list of measurements
    good_ones: list[str] = None  # list of successfully pulled out fibers
    good_ones_nr: int = None  # count of successfully pulled out fibers
    bad_ones_nr: int = None  # count of broken fibers
# global instancing
sort_storage = MeasurementClassifier()


@dataclass
class CalculationResults:
    """
    All calculated numbers are saved here
    """
    measurements: list[tuple] = None  # measurements of successfully pulled out fibers
    fiberpulloutratio: float = None  # ratio of successfully sfpo and broken fibers
    embeddinglength: list[float] = None  # list of the embeddinglengths (can differ measurement to measurement)
    interfaceshearstrength: list[float] = None  # calculated IFSS (F_max/(PI*d_fiber*l_e))
    work: list[float] = None  # Integral of each Force-Displacement Curve
# global instancing
calculated_storage = CalculationResults()
