"""
validators/dataset_validator.py
Validates the generated dataset for quality and consistency.
"""

import logging
from collections import Counter
from typing import List, Dict, Any, Tuple

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DOMAINS, DIFFICULTIES, LABELS

logger = logging.getLogger(__name__)


class DatasetValidator:
    """
    Validates a generated dataset and produces a human-readable report.

    Checks
    ------
    1. Duplicate questions
    2. Missing or empty fields (domain, difficulty, question, answer, label)
    3. Invalid field values (unknown domain, difficulty, or label)
    4. Empty answer strings
    5. Label distribution balance
    6. Domain coverage
    """

    REQUIRED_FIELDS = {"domain", "difficulty", "question", "answer", "label"}

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.stats: Dict[str, Any] = {}

    # ──────────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────────

    def validate(self, records: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Validate the dataset.

        Parameters
        ----------
        records : List[Dict]
            Dataset records to validate.

        Returns
        -------
        (is_valid, report_string)
        """
        self.errors = []
        self.warnings = []
        self.stats = {}

        if not records:
            self.errors.append("Dataset is empty — no records to validate.")
            return False, self._build_report()

        self._check_fields(records)
        duplicates = self._check_duplicates(records)
        self._check_empty_answers(records)
        self._collect_stats(records, duplicates)
        self._check_distribution_balance(records)
        self._check_domain_coverage(records)

        is_valid = len(self.errors) == 0
        return is_valid, self._build_report()

    # ──────────────────────────────────────────────────────────────────────────
    # Validation steps
    # ──────────────────────────────────────────────────────────────────────────

    def _check_fields(self, records: List[Dict]) -> None:
        for i, rec in enumerate(records):
            missing = self.REQUIRED_FIELDS - rec.keys()
            if missing:
                self.errors.append(f"Record {i}: Missing fields: {missing}")
                continue

            if rec["domain"] not in DOMAINS:
                self.errors.append(
                    f"Record {i}: Invalid domain '{rec['domain']}'."
                )
            if rec["difficulty"] not in DIFFICULTIES:
                self.errors.append(
                    f"Record {i}: Invalid difficulty '{rec['difficulty']}'."
                )
            if rec["label"] not in LABELS:
                self.errors.append(
                    f"Record {i}: Invalid label '{rec['label']}'."
                )

    def _check_duplicates(self, records: List[Dict]) -> int:
        questions = [r.get("question", "") for r in records]
        counts = Counter(questions)
        dups = {q: c for q, c in counts.items() if c > 1}
        dup_count = sum(c - 1 for c in dups.values())

        if dups:
            self.warnings.append(
                f"Found {len(dups)} duplicate question(s) ({dup_count} extra occurrences)."
            )
            for q, c in list(dups.items())[:5]:
                self.warnings.append(f"  '{q[:80]}...' appears {c}x")

        return dup_count

    def _check_empty_answers(self, records: List[Dict]) -> None:
        empty = [i for i, r in enumerate(records) if not r.get("answer", "").strip()]
        if empty:
            self.errors.append(
                f"Empty answers at record indices: {empty[:10]}"
                + ("..." if len(empty) > 10 else "")
            )

    def _collect_stats(self, records: List[Dict], duplicate_count: int) -> None:
        label_dist = Counter(r.get("label") for r in records)
        domain_dist = Counter(r.get("domain") for r in records)
        diff_dist = Counter(r.get("difficulty") for r in records)

        self.stats = {
            "total": len(records),
            "duplicates": duplicate_count,
            "label_distribution": dict(label_dist),
            "domain_distribution": dict(domain_dist),
            "difficulty_distribution": dict(diff_dist),
            "domains_covered": len(domain_dist),
            "errors": len(self.errors),
            "warnings": len(self.warnings),
        }

    def _check_distribution_balance(self, records: List[Dict]) -> None:
        total = len(records)
        label_counts = Counter(r.get("label") for r in records)
        expected = total / len(LABELS)

        for label in LABELS:
            count = label_counts.get(label, 0)
            pct = (count / total * 100) if total else 0
            deviation = abs(count - expected) / expected * 100 if expected else 0
            if deviation > 20:
                self.warnings.append(
                    f"Label '{label}' has imbalanced distribution: "
                    f"{count} records ({pct:.1f}%), expected ~{expected:.0f} ({100/len(LABELS):.1f}%)."
                )

    def _check_domain_coverage(self, records: List[Dict]) -> None:
        covered = {r.get("domain") for r in records}
        missing = set(DOMAINS) - covered
        if missing:
            self.warnings.append(
                f"The following domains have no records: {sorted(missing)}"
            )

    # ──────────────────────────────────────────────────────────────────────────
    # Report builder
    # ──────────────────────────────────────────────────────────────────────────

    def _build_report(self) -> str:
        lines = [
            "=" * 60,
            "  DATASET VALIDATION REPORT",
            "=" * 60,
        ]

        if self.stats:
            lines += [
                "",
                "── Statistics ──────────────────────────────────────────",
                f"  Total Samples     : {self.stats.get('total', 0)}",
                f"  Duplicates Found  : {self.stats.get('duplicates', 0)}",
                f"  Domains Covered   : {self.stats.get('domains_covered', 0)} / {len(DOMAINS)}",
                "",
                "  Label Distribution:",
            ]
            for label, count in sorted(
                self.stats.get("label_distribution", {}).items()
            ):
                pct = count / self.stats["total"] * 100 if self.stats["total"] else 0
                lines.append(f"    {label:<12}: {count:>5}  ({pct:5.1f}%)")

            lines += [
                "",
                "  Difficulty Distribution:",
            ]
            for diff, count in sorted(
                self.stats.get("difficulty_distribution", {}).items()
            ):
                pct = count / self.stats["total"] * 100 if self.stats["total"] else 0
                lines.append(f"    {diff:<12}: {count:>5}  ({pct:5.1f}%)")

        if self.errors:
            lines += ["", "── Errors ──────────────────────────────────────────────"]
            for e in self.errors:
                lines.append(f"  [ERROR] {e}")

        if self.warnings:
            lines += ["", "── Warnings ────────────────────────────────────────────"]
            for w in self.warnings:
                lines.append(f"  [WARN]  {w}")

        status = "PASSED ✓" if not self.errors else "FAILED ✗"
        lines += [
            "",
            f"  Status: {status}",
            "=" * 60,
        ]
        return "\n".join(lines)
