"""
generators/label_generator.py
Manages label assignment for dataset records.
"""

import logging
import itertools
from typing import List

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import LABELS

logger = logging.getLogger(__name__)


class LabelGenerator:
    """
    Assigns labels ('correct', 'partial', 'incorrect') to dataset records.

    The generator produces labels in a balanced round-robin pattern so that
    the final dataset has an approximately equal distribution of all three
    labels regardless of sample count.
    """

    def __init__(self):
        # Cycling iterator ensures balanced distribution
        self._cycle = itertools.cycle(LABELS)
        self._counts = {label: 0 for label in LABELS}
        logger.debug("LabelGenerator initialized with balanced cycling.")

    # ──────────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────────

    def next_label(self) -> str:
        """Return the next label in the balanced cycle."""
        label = next(self._cycle)
        self._counts[label] += 1
        logger.debug("Assigned label: %s", label)
        return label

    def get_distribution(self) -> dict:
        """Return current label counts."""
        return dict(self._counts)

    def reset(self) -> None:
        """Reset the label cycle and counts."""
        self._cycle = itertools.cycle(LABELS)
        self._counts = {label: 0 for label in LABELS}
        logger.debug("LabelGenerator reset.")

    @staticmethod
    def get_valid_labels() -> List[str]:
        return list(LABELS)
