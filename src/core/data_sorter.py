"""
this code was made with the help of chatgpt, claude, stackoverflow .... u name and gasp it
"""
# src/core/data_sorter.py
from typing import List, Tuple, Optional
import logging
from src.config.config_manager import app_config


class DataSorter:
    """
    Sortiert die Messungen in erfolgreiche und fehlgeschlagene Pull-Outs.
    Implementiert verschiedene Sortiermethoden basierend auf Benennungskonventionen.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialisiert den DataSorter mit optionalem Logger.
        Args:logger: Logger-Instanz für Protokollierung (optional)
        """
        self.logger = logger or logging.getLogger('SFPO_Analyzer')

    def analyze_filenames(self) -> Tuple[List[str], List[str]]:
        """
        Analysiert Dateinamen und sortiert sie in erfolgreiche und fehlgeschlagene Messungen.
        Unterstützt verschiedene Benennungsschemata und versucht flexibel zu sein.

        Returns:
            Tuple mit Listen erfolgreicher und fehlgeschlagener Messungen

        Raises:
            ValueError: Wenn keine Dateinamen zum Analysieren vorhanden sind
        """
        if not app_config.paths.filenames:
            error_msg = "Keine Dateinamen zum Analysieren vorhanden"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        self.logger.info(f"Analysiere {len(app_config.paths.filenames)} Dateinamen...")

        # Sammelcontainer für die Ergebnisse
        successful = []
        failed = []
        unknown = []

        # Versuche verschiedene Schemata für jeden Dateinamen
        for name in app_config.paths.filenames:
            # Standardschema überprüfen
            if self._check_standard_scheme(name):
                if name[2] == 'a' and name[3] == '_':
                    successful.append(name)
                    continue
                elif name[2] == 'x' and name[3] == 'a':
                    failed.append(name)
                    continue

            # Altes Schema überprüfen
            if len(name) >= 2:
                if name[-2] != 'x' and name[-1] == 'a':
                    successful.append(name)
                    continue
                elif name[-2] == 'x' and name[-1] == 'a':
                    failed.append(name)
                    continue

            # POI/POII Schemata prüfen (speziell für deine Daten)
            if "_POI_" in name or "_POII_" in name or name.startswith("POI_") or name.startswith("POII_"):
                successful.append(name)  # Annahme: Diese sind erfolgreich
                continue

            # Weitere Muster für komplexere Dateinamen (z.B. mit MMT, BnM, etc.)
            if any(x in name for x in ["_MMT_", "_BnM_", "_CF1_"]):
                # Hier könnte man weitere Regeln hinzufügen
                # Vorerst ordnen wir sie als erfolgreich ein
                successful.append(name)
                continue

            # Warnmeldung für unbekannte Schemata ausgeben und als unbekannt markieren
            self.logger.warning(f"Dateiname '{name}' entspricht keinem bekannten Schema, wird ignoriert")
            unknown.append(name)

        # Speichere Ergebnisse in der Konfiguration
        app_config.classification.successful_measurements = successful
        app_config.classification.failed_measurements = failed

        # Protokolliere die Ergebnisse
        self.logger.info(f"Erfolgreich erkannte Messungen: {len(successful)}")
        self.logger.info(f"Als fehlgeschlagen erkannte Messungen: {len(failed)}")
        self.logger.info(f"Nicht erkannte Messungen: {len(unknown)}")

        if unknown:
            self.logger.debug(f"Nicht erkannte Dateien: {unknown}")

        if successful:
            self.logger.debug(f"Beispiele für erfolgreiche Messungen: {successful[:5]}...")

        return successful, failed

    def _check_standard_scheme(self, name: str) -> bool:
        """
        Prüft, ob ein Dateiname dem Standardschema entspricht.

        Args:
            name: Zu prüfender Dateiname

        Returns:
            True, wenn der Name dem Standardschema entspricht, sonst False
        """
        # Prüfen, ob der Name mindestens 4 Zeichen lang ist
        if len(name) < 4:
            return False

        # Prüfen, ob Position 2 ein 'a' oder 'x' enthält
        if name[2] not in ['a', 'x']:
            return False

        # Prüfen, ob Position 3 ein '_' oder 'a' enthält
        if name[3] not in ['_', 'a']:
            return False

        return True

    def _sort_new_scheme(self, filenames: List[str]) -> Tuple[List[str], List[str]]:
        """
        Sortiert Dateinamen nach dem neuen Benennungsschema, bei dem die Indikatoren
        an Position 2 stehen.

        Args:
            filenames: Liste der zu sortierenden Dateinamen

        Returns:
            Tuple mit Listen erfolgreicher und fehlgeschlagener Messungen
        """
        successful = []
        failed = []

        for name in filenames:
            if len(name) < 4:  # Sicherheitsüberprüfung für zu kurze Namen
                self.logger.warning(f"Dateiname {name} zu kurz für Schema-Analyse, übersprungen")
                continue

            # Neues Schema: 'a' an Position 2 und '_' an Position 3 für erfolgreiche
            if name[2] == 'a' and name[3] == '_':
                successful.append(name)
            # Neues Schema: 'x' an Position 2 und 'a' an Position 3 für fehlgeschlagene
            elif name[2] == 'x' and name[3] == 'a':
                failed.append(name)
            else:
                self.logger.warning(f"Dateiname {name} entspricht nicht dem erwarteten Schema")

        return successful, failed

    def _sort_old_scheme(self, filenames: List[str]) -> Tuple[List[str], List[str]]:
        """
        Sortiert Dateinamen nach dem alten Benennungsschema, bei dem die Indikatoren
        am Ende stehen.

        Args:
            filenames: Liste der zu sortierenden Dateinamen

        Returns:
            Tuple mit Listen erfolgreicher und fehlgeschlagener Messungen
        """
        successful = []
        failed = []

        for name in filenames:
            if len(name) < 2:  # Sicherheitsüberprüfung für zu kurze Namen
                self.logger.warning(f"Dateiname {name} zu kurz für Schema-Analyse, übersprungen")
                continue

            # Altes Schema: Nicht-'x' an vorletzter Position und 'a' am Ende für erfolgreiche
            if name[-2] != 'x' and name[-1] == 'a':
                successful.append(name)
            # Altes Schema: 'x' an vorletzter Position und 'a' am Ende für fehlgeschlagene
            elif name[-2] == 'x' and name[-1] == 'a':
                failed.append(name)
            else:
                self.logger.warning(f"Dateiname {name} entspricht nicht dem erwarteten Schema")

        return successful, failed

    def calculate_pullout_ratio(self) -> float:
        """
        Berechnet das Verhältnis von erfolgreichen zu allen Messungen.

        Returns:
            Das Verhältnis als float zwischen 0 und 1
        """
        successful_count = app_config.classification.successful_count
        failed_count = app_config.classification.failed_count
        total_count = successful_count + failed_count

        if total_count == 0:
            return 0.0

        ratio = successful_count / total_count

        # Speichere das Ergebnis
        app_config.results.fiber_pullout_ratio = ratio

        self.logger.info(f"Pull-Out Verhältnis: {ratio:.2f} ({successful_count}/{total_count})")

        return ratio