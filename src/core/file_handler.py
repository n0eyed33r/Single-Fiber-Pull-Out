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
    """Use the path naming for further use"""

    @staticmethod
    def select_folder() -> Optional[Path]:
        """Opens a window to search the files or folder which will be analyzed"""
        root = tk.Tk()
        root.withdraw()  # hide the main window

        folder_path = filedialog.askdirectory()
        if not folder_path:
            return None

        path_obj = Path(folder_path)
        naming_storage.update_paths(path_obj)
        return path_obj

    @staticmethod
    def find_specimen_files() -> List[str]:
        """find the .txt files"""
        if not naming_storage.root_path:
            raise ValueError("no folder selected")

        specimen_files = []
        for file_path in naming_storage.root_path.rglob("*.txt"):
            specimen_files.append(file_path.stem)

        naming_storage.filenames = specimen_files
        return specimen_files