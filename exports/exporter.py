"""
exports/exporter.py
Handles exporting dataset records to JSON and CSV formats.
"""

import csv
import json
import logging
import os
from typing import List, Dict, Any

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DATA_DIR, DATASET_CSV, DATASET_JSON

logger = logging.getLogger(__name__)


class DatasetExporter:
    """
    Exports dataset records to JSON and CSV files.

    Usage
    -----
    exporter = DatasetExporter()
    exporter.export_json(records)
    exporter.export_csv(records)
    """

    def __init__(
        self,
        json_path: str = DATASET_JSON,
        csv_path: str = DATASET_CSV,
    ):
        self.json_path = json_path
        self.csv_path = csv_path
        self._ensure_data_dir()

    # ──────────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────────

    def export_json(self, records: List[Dict[str, Any]]) -> str:
        """
        Write records to a JSON file.

        Returns
        -------
        str
            Absolute path of the written file.
        """
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

        logger.info("Exported %d records to JSON: %s", len(records), self.json_path)
        return os.path.abspath(self.json_path)

    def export_csv(self, records: List[Dict[str, Any]]) -> str:
        """
        Write records to a CSV file.

        Returns
        -------
        str
            Absolute path of the written file.
        """
        if not records:
            logger.warning("No records to export to CSV.")
            return ""

        fieldnames = ["domain", "difficulty", "question", "answer", "label"]
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=fieldnames, extrasaction="ignore"
            )
            writer.writeheader()
            writer.writerows(records)

        logger.info("Exported %d records to CSV: %s", len(records), self.csv_path)
        return os.path.abspath(self.csv_path)

    def export_validation_samples(
        self,
        records: List[Dict[str, Any]],
        path: str,
        n: int = 10,
    ) -> str:
        """
        Save the first *n* records as a human-readable validation sample file.
        """
        samples = records[:n]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(samples, f, indent=2, ensure_ascii=False)

        logger.info("Saved %d validation samples to: %s", len(samples), path)
        return os.path.abspath(path)

    # ──────────────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _ensure_data_dir(self) -> None:
        os.makedirs(os.path.dirname(self.json_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
