# src/utils/logger_setup.py
import logging
from pathlib import Path
from datetime import datetime

class LoggerSetup:
    """Sets up logging to both console and file with timestamps"""

    @staticmethod
    def setup_logger():
        # Erstelle einen Logs-Ordner im Projektverzeichnis
        project_root = Path(__file__).parent.parent.parent  # Gehe drei Ordner nach oben
        log_path = project_root / "logs"
        log_path.mkdir(exist_ok=True)

        # Erstelle einen eindeutigen Dateinamen mit Zeitstempel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_path / f"debug_log_{timestamp}.txt"

        # Informiere über den Log-Speicherort
        print(f"Logs werden gespeichert in: {log_file}")

        # Rest der Logger-Konfiguration bleibt gleich
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_file, encoding='utf-8')
            ]
        )

        return logging.getLogger('SFPO_Analyzer')