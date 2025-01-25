"""
this code was made with the help of chatgpt, claude, stackoverflow .... u name it
"""

# src/core/data_alteration.py
from src.config.settings import SortOf

class DataAlteration:
    """sort the useful and evaluable pull-outs"""


    def __init__(self):
        self.state = SortOf

    def file_selection(self): -> list[str]:
    """saves each measurement naming as own string"""
