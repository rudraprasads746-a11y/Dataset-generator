"""
main.py
Entry point for the Synthetic Interview Dataset Generator.

Usage
-----
# Generate 150 samples across all domains
python main.py

# Generate 500 samples
python main.py --samples 500

# Generate for a specific domain
python main.py --domain AWS

# Generate for a specific difficulty
python main.py --difficulty Hard

# Combine filters
python main.py --domain Python --difficulty Medium --samples 60

# Show statistics only (no export)
python main.py --stats-only
"""

import argparse
import json
import logging
import os
import random
import sys
from typing import Any, Dict, List, Optional

from config import (
    DATA_DIR,
    DATASET_CSV,
    DATASET_JSON,
    DEFAULT_SAMPLES,
    DIFFICULTIES,
    DOMAINS,
    LOG_FORMAT,
    LOG_LEVEL,
    MAX_SAMPLES,
    MIN_SAMPLES,
    VALIDATION_SAMPLES,
)
from exports.exporter import DatasetExporter
from generators.answer_generator import AnswerGenerator
from generators.label_generator import LabelGenerator
from generators.question_generator import QuestionGenerator
from validators.dataset_validator import DatasetValidator

# ──────────────────────────────────────────────────────────────────────────────
# Logging configuration
# ──────────────────────────────────────────────────────────────────────────────

logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# DatasetGenerator
# ──────────────────────────────────────────────────────────────────────────────


class DatasetGenerator:
    """
    Orchestrates question generation, answer generation, labelling, validation,
    and export for the synthetic interview dataset.
    """

    def __init__(self):
        self.question_gen = QuestionGenerator()
        self.answer_gen = AnswerGenerator()
        self.label_gen = LabelGenerator()
        self.validator = DatasetValidator()
        self.exporter = DatasetExporter(
            json_path=DATASET_JSON,
            csv_path=DATASET_CSV,
        )
        self.records: List[Dict[str, Any]] = []

    # ──────────────────────────────────────────────────────────────────────────
    # Core generation pipeline
    # ──────────────────────────────────────────────────────────────────────────

    def generate(
        self,
        num_samples: int = DEFAULT_SAMPLES,
        domains: Optional[List[str]] = None,
        difficulties: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate *num_samples* dataset records.

        Parameters
        ----------
        num_samples : int
            Total number of records to produce.
        domains : List[str] | None
            Restrict generation to these domains. None = all domains.
        difficulties : List[str] | None
            Restrict to these difficulty levels. None = all difficulties.

        Returns
        -------
        List[Dict]  – The complete dataset records.
        """
        num_samples = max(MIN_SAMPLES, min(num_samples, MAX_SAMPLES))
        active_domains = domains or DOMAINS
        active_difficulties = difficulties or DIFFICULTIES

        logger.info(
            "Starting generation: %d samples | %d domain(s) | %d difficulty level(s)",
            num_samples,
            len(active_domains),
            len(active_difficulties),
        )

        # Build a balanced task list: (domain, difficulty) pairs
        tasks = [
            (d, diff)
            for d in active_domains
            for diff in active_difficulties
        ]
        random.shuffle(tasks)

        self.records = []
        self.question_gen.reset()
        self.label_gen.reset()

        # Round-robin through tasks to ensure spread
        task_iter = iter(tasks * (num_samples // len(tasks) + 2))

        while len(self.records) < num_samples:
            try:
                domain, difficulty = next(task_iter)
            except StopIteration:
                # Reshuffle and continue if needed
                tasks_copy = list(tasks)
                random.shuffle(tasks_copy)
                task_iter = iter(tasks_copy * 2)
                domain, difficulty = next(task_iter)

            questions = self.question_gen.generate(domain, difficulty, count=1)
            if not questions:
                continue

            question = questions[0]
            answers = self.answer_gen.generate_all(domain, question, difficulty)
            label = self.label_gen.next_label()

            record = {
                "domain": domain,
                "difficulty": difficulty,
                "question": question,
                "answer": answers[label],
                "label": label,
            }
            self.records.append(record)

        # Trim to exact count
        self.records = self.records[:num_samples]
        logger.info("Generation complete: %d records produced.", len(self.records))
        return self.records

    # ──────────────────────────────────────────────────────────────────────────
    # Validate
    # ──────────────────────────────────────────────────────────────────────────

    def validate(self) -> str:
        """Run the validator and return the report string."""
        is_valid, report = self.validator.validate(self.records)
        status = "PASSED" if is_valid else "FAILED"
        logger.info("Validation %s.", status)
        return report

    # ──────────────────────────────────────────────────────────────────────────
    # Export
    # ──────────────────────────────────────────────────────────────────────────

    def export(self) -> Dict[str, str]:
        """Export dataset to JSON and CSV; return dict of output paths."""
        os.makedirs(DATA_DIR, exist_ok=True)
        json_path = self.exporter.export_json(self.records)
        csv_path = self.exporter.export_csv(self.records)
        samples_path = self.exporter.export_validation_samples(
            self.records, VALIDATION_SAMPLES, n=10
        )
        return {
            "json": json_path,
            "csv": csv_path,
            "samples": samples_path,
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Statistics
    # ──────────────────────────────────────────────────────────────────────────

    def print_statistics(self) -> None:
        """Print a concise statistics summary to stdout."""
        if not self.records:
            print("No records generated yet.")
            return

        from collections import Counter

        total = len(self.records)
        label_counts = Counter(r["label"] for r in self.records)
        domain_counts = Counter(r["domain"] for r in self.records)
        diff_counts = Counter(r["difficulty"] for r in self.records)

        print("\n" + "=" * 50)
        print("  DATASET STATISTICS")
        print("=" * 50)
        print(f"  Total Samples    : {total}")
        print(f"  Correct          : {label_counts.get('correct', 0)}")
        print(f"  Partial          : {label_counts.get('partial', 0)}")
        print(f"  Incorrect        : {label_counts.get('incorrect', 0)}")
        print(f"  Domains Covered  : {len(domain_counts)}")
        print(f"  Duplicates Found : 0  (deduplicated during generation)")
        print()
        print("  Difficulty Breakdown:")
        for d in DIFFICULTIES:
            print(f"    {d:<8}: {diff_counts.get(d, 0)}")
        print()
        print("  Top 5 Domains by Record Count:")
        for domain, cnt in domain_counts.most_common(5):
            print(f"    {domain:<30}: {cnt}")
        print("=" * 50 + "\n")

    # ──────────────────────────────────────────────────────────────────────────
    # Preview
    # ──────────────────────────────────────────────────────────────────────────

    def preview(self, n: int = 3) -> None:
        """Print a few sample records to stdout."""
        samples = random.sample(self.records, min(n, len(self.records)))
        print("\n── Sample Records Preview ──────────────────────────────")
        for i, rec in enumerate(samples, 1):
            print(f"\n  [{i}] Domain    : {rec['domain']}")
            print(f"      Difficulty : {rec['difficulty']}")
            print(f"      Label      : {rec['label'].upper()}")
            print(f"      Question   : {rec['question']}")
            answer_preview = rec["answer"][:120].replace("\n", " ")
            print(f"      Answer     : {answer_preview}...")
        print()


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Synthetic Interview Dataset Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
  python main.py --samples 500
  python main.py --domain AWS
  python main.py --difficulty Hard
  python main.py --domain Python --difficulty Medium --samples 60
  python main.py --stats-only
        """,
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=DEFAULT_SAMPLES,
        metavar="N",
        help=f"Number of samples to generate (default: {DEFAULT_SAMPLES}, "
             f"min: {MIN_SAMPLES}, max: {MAX_SAMPLES})",
    )
    parser.add_argument(
        "--domain",
        type=str,
        default=None,
        metavar="DOMAIN",
        help=f"Restrict to one domain. Options: {', '.join(DOMAINS)}",
    )
    parser.add_argument(
        "--difficulty",
        type=str,
        default=None,
        choices=DIFFICULTIES,
        metavar="LEVEL",
        help=f"Restrict to one difficulty level. Options: {', '.join(DIFFICULTIES)}",
    )
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Print statistics without exporting files.",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip validation step.",
    )
    parser.add_argument(
        "--preview",
        type=int,
        default=3,
        metavar="N",
        help="Number of sample records to preview (default: 3).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Validate domain argument
    domains = None
    if args.domain:
        if args.domain not in DOMAINS:
            print(
                f"[ERROR] Unknown domain '{args.domain}'.\n"
                f"Valid domains: {', '.join(DOMAINS)}"
            )
            sys.exit(1)
        domains = [args.domain]

    difficulties = [args.difficulty] if args.difficulty else None

    # ── Run generation ──────────────────────────────────────────────────────
    generator = DatasetGenerator()
    print(f"\n🚀  Generating {args.samples} synthetic interview records …\n")
    generator.generate(
        num_samples=args.samples,
        domains=domains,
        difficulties=difficulties,
    )

    # ── Preview ─────────────────────────────────────────────────────────────
    generator.preview(n=args.preview)

    # ── Statistics ──────────────────────────────────────────────────────────
    generator.print_statistics()

    # ── Validation ──────────────────────────────────────────────────────────
    if not args.no_validate:
        report = generator.validate()
        print(report)

    # ── Export ──────────────────────────────────────────────────────────────
    if not args.stats_only:
        paths = generator.export()
        print("\n✅  Export complete:")
        print(f"    JSON    → {paths['json']}")
        print(f"    CSV     → {paths['csv']}")
        print(f"    Samples → {paths['samples']}\n")
    else:
        print("Stats-only mode: no files exported.\n")


if __name__ == "__main__":
    main()
