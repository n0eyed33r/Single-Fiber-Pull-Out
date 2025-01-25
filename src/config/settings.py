"""
this code was made with the help of chatgpt, claude, stackoverflow .... u name it
"""

# src/config/settings.py
from dataclasses import dataclass
from pathlib import Path

@dataclass
class MaterialParameters:
    # material parameters of the single fiber pull-out
    elastic_modulus_fiber: float = 250.0  # GPa
    elastic_modulus_matrix: float = 43.0  # GPa
    shear_modulus_fiber: float = 17.0  # GPa
    shear_modulus_matrix: float = 18.0  # GPa
    matrix_radius: float = 1300.0  # µm


@dataclass
class NamingInTheNameOf:
    # names for further use e.g. title of measurements etc.
    filenames: list[str] = None
    root_path: Path = None
    main_folder: str = ""

    def __post_init__(self):
        self.filenames = [] if self.filenames is None else self.filenames

@dataclass
class SortOf:
    # sort and select the successfully pulled out fibers
    measurements = []  # list of measurements
    good_ones = []  # list of successfully pulled out fibers
    bad_ones = []  # list of broken fibers