# src/main.py
from core.file_handler import FileHandler
from config.settings import MaterialParameters


def main():
    # initialise
    file_handler = FileHandler()
    material_params = MaterialParameters()

    # I ch-ch-choooose you (folder)
    selected_path = file_handler.select_folder()
    if not selected_path:
        print("nothing found here")
        return

    # find the files
    specimen_files = file_handler.find_specimen_files()
    print(f"amount of files: {len(specimen_files)}")


if __name__ == "__main__":
    main()