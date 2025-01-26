"""
this code was made with the help of chatgpt, claude, stackoverflow .... u name and gasp it
"""

# src/core/data_sorter.py
from src.config.settings import naming_storage, sort_storage

class DataSorter:
    """sort the useful and evaluable pull-outs"""


    @staticmethod
    def analyze_filenames() -> None:
        """
        Analyzes filenames and sorts them into successful and failed measurements.
        The method looks at the part before the first underscore to determine
        if it's a new or old naming scheme.
        """
        if not naming_storage.filenames:
            raise ValueError("No filenames to analyze")

        # Analyze the first filename to determine the naming scheme
        first_name = naming_storage.filenames[0]
        prefix = first_name.split('_')[0]  # Get part before first underscore

        # Determine if we're dealing with new or old naming scheme
        is_new_scheme = len(prefix) >= 3 and (
                prefix[2] == 'x' or prefix[2] == 'a'
        )

        if is_new_scheme:
            successful, failed = DataSorter._sort_new_scheme(
                naming_storage.filenames
            )
        else:
            successful, failed = DataSorter._sort_old_scheme(
                naming_storage.filenames
            )

        # Store results in our global storage
        sort_storage.good_ones = successful
        sort_storage.bad_ones = failed
        sort_storage.good_ones_nr = len(successful)
        sort_storage.bad_ones_nr = len(failed)

    @staticmethod
    def _sort_new_scheme(filenames: list[str]) -> tuple[list[str], list[str]]:
        """
        Sorts filenames using new naming scheme where indicators are at position 2
        Returns tuple of (successful_measurements, failed_measurements)
        """
        successful = [
            name for name in filenames
            if name[2] == 'a' and name[3] == '_'
        ]
        failed = [
            name for name in filenames
            if name[2] == 'x' and name[3] == 'a'
        ]
        return successful, failed

    @staticmethod
    def _sort_old_scheme(filenames: list[str]) -> tuple[list[str], list[str]]:
        """
        Sorts filenames using old naming scheme where indicators are at the end
        Returns tuple of (successful_measurements, failed_measurements)
        """
        successful = [
            name for name in filenames
            if name[-2] != 'x' and name[-1] == 'a'
        ]
        failed = [
            name for name in filenames
            if name[-2] == 'x' and name[-1] == 'a'
        ]
        return successful, failed