"""
this code was made with the help of chatgpt, claude, gemini, stackoverflow .... u name it
"""
# src/utils/logger_setup.py
import logging
import sys
import os
from pathlib import Path
from datetime import datetime


class LoggerSetup:
    @staticmethod
    def setup_logger():
        try:
            # Logger Grundkonfiguration
            logger = logging.getLogger('SFPO_Analyzer')
            logger.setLevel(logging.DEBUG)

            # Wichtig: Stelle sicher, dass der Logger Nachrichten weiterleitet
            logger.propagate = True

            # Setze Handler zurück, um Doppelausgaben zu vermeiden
            logger.handlers = []

            # Konsolenausgabe einrichten
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(message)s')
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

            # Log-Verzeichnis einrichten mit Fehlerprüfung
            try:
                log_dir = Path(__file__).parent.parent.parent / "logs"
                log_dir.mkdir(exist_ok=True)

                # Überprüfe Schreibrechte
                if not os.access(log_dir, os.W_OK):
                    print(f"Warnung: Keine Schreibrechte im Verzeichnis {log_dir}")
                    return logger

                # Hier die Verwaltung der Log-Dateien aufrufen
                LoggerSetup.manage_log_files(log_dir)
                
                # Erstelle neue Log-Datei
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                log_file = log_dir / f"debug_log_{timestamp}.txt"

                # Versuche eine Test-Datei zu erstellen
                try:
                    log_file.touch()
                except Exception as e:
                    print(f"Warnung: Konnte Log-Datei nicht erstellen: {e}")
                    return logger

                # Wenn alles funktioniert, füge den File Handler hinzu
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)

                # Bestätige erfolgreiche Einrichtung
                print(f"Log-Datei erfolgreich erstellt: {log_file}")
                logger.info("Logging gestartet")

            except Exception as e:
                print(f"Fehler beim Einrichten des File-Loggings: {e}")
                # Gebe Logger mit nur Console Handler zurück

            return logger

        except Exception as e:
            print(f"Kritischer Fehler beim Logger-Setup: {e}")
            # Erstelle einen Minimal-Logger für Konsolenausgabe
            basic_logger = logging.getLogger('SFPO_Analyzer_Basic')
            basic_logger.addHandler(logging.StreamHandler(sys.stdout))
            return basic_logger

    # src/utils/logger_setup.py
    @staticmethod
    def manage_log_files(log_dir: Path, max_files: int = 5):
        """
        Verwaltet die Log-Dateien im angegebenen Verzeichnis.
        """
        print("\n=== Log File Management ===")  # Deutliche Trennung

        # Sammle alle debug_log Dateien
        log_files = list(log_dir.glob("debug_log_*.txt"))

        print(f"Gefundene Log-Dateien: {len(log_files)}")
        print("Dateien im Log-Verzeichnis:")
        for file in log_files:
            print(f"  • {file.name} - Geändert: {datetime.fromtimestamp(file.stat().st_mtime)}")

        if len(log_files) > max_files:
            print(f"\nLösche alte Logs (behalte {max_files} neueste Dateien):")
            # Sortiere Dateien nach Änderungsdatum (neueste zuerst)
            log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # Lösche überzählige Dateien
            for old_file in log_files[max_files:]:
                try:
                    print(f"  Lösche: {old_file.name}")
                    old_file.unlink()
                    print(f"  ✓ Erfolgreich gelöscht")
                except Exception as e:
                    print(f"  ✗ Fehler beim Löschen: {e}")

            print("=== Log Management Ende ===\n")