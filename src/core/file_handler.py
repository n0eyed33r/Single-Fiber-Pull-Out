"""
this code was made with the help of chatgpt, claude, stackoverflow .... u name it
"""

# src/core/file_handler.py
from pathlib import Path
from tkinter import filedialog
import tkinter as tk
from typing import Optional
from src.config.settings import NamingInTheNameOf


class FileHandler:
    """Use the path naming for further use"""

    def __init__(self):
        self.state = NamingInTheNameOf()

    def select_folder(self) -> Optional[Path]:
        """Opens a window to search the files or folder which will be analyzed"""
        root = tk.Tk()
        root.withdraw()  # hide the main window

        folder_path = filedialog.askdirectory()
        if not folder_path:
            return None

        self.state.root_path = Path(folder_path)
        self.state.main_folder = self.state.root_path.name.replace("_", " ")
        return self.state.root_path

    def find_specimen_files(self) -> list[str]:
        """find the .txt files"""
        if not self.state.root_path:
            raise ValueError("no folder selected")

        specimen_files = []
        for file_path in self.state.root_path.rglob("*.txt"):
            specimen_files.append(file_path.stem)

        self.state.filenames = specimen_files
        return specimen_files