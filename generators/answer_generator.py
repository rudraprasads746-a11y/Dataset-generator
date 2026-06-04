"""
generators/answer_generator.py
Generates correct, partial, and incorrect answers for interview questions.
"""

import logging
import random
from typing import Dict

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    CORRECT_ANSWERS,
    GENERIC_CORRECT_FRAGMENTS,
    GENERIC_PARTIAL_FRAGMENTS,
    GENERIC_INCORRECT_FRAGMENTS,
)

logger = logging.getLogger(__name__)


class AnswerGenerator:
    """
    Produces correct, partial, and incorrect answers for a given question.

    Strategy
    --------
    1. Look up a curated correct answer in CORRECT_ANSWERS.
    2. If none exists, build a plausible answer from generic fragments.
    3. Derive a partial answer by truncating / removing key sentences.
    4. Derive an incorrect answer from the wrong-answer fragment pool.
    """

    def __init__(self):
        logger.debug("AnswerGenerator initialized.")

    # ──────────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────────

    def generate_all(self, domain: str, question: str, difficulty: str) -> Dict[str, str]:
        """
        Return a dict with keys 'correct', 'partial', and 'incorrect'.

        Parameters
        ----------
        domain : str
        question : str
        difficulty : str
            Used to scale answer depth.
        """
        correct = self._get_correct_answer(domain, question, difficulty)
        partial = self._derive_partial_answer(correct, domain, difficulty)
        incorrect = self._get_incorrect_answer(domain, question, difficulty)

        logger.debug("Answers generated for: '%s'", question[:60])
        return {
            "correct": correct,
            "partial": partial,
            "incorrect": incorrect,
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Answer builders
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _get_correct_answer(domain: str, question: str, difficulty: str) -> str:
        """Return a curated answer or build one generically."""
        # Check specific curated answers first
        domain_answers = CORRECT_ANSWERS.get(domain, {})
        if question in domain_answers:
            return domain_answers[question]

        # Build a generic correct answer
        fragment = random.choice(GENERIC_CORRECT_FRAGMENTS).replace("{domain}", domain)

        # Add depth hints based on difficulty
        depth_suffix = {
            "Easy": (
                f" This is a foundational concept in {domain} that every practitioner "
                "should understand before moving to more advanced topics."
            ),
            "Medium": (
                f" Mastery of this area in {domain} allows engineers to design more "
                "robust systems, avoid common pitfalls, and debug complex issues "
                "more effectively in production environments."
            ),
            "Hard": (
                f" At scale, this aspect of {domain} requires deep understanding of "
                "distributed systems principles, careful performance profiling, and "
                "often involves trade-offs between consistency, availability, and "
                "partition tolerance. Real-world implementations must also account "
                "for operational concerns such as monitoring, alerting, and graceful "
                "degradation under load."
            ),
        }
        return fragment + depth_suffix.get(difficulty, "")

    @staticmethod
    def _derive_partial_answer(correct_answer: str, domain: str, difficulty: str) -> str:
        """
        Build a partial answer by combining a fragment from the correct answer
        with a generic partial-answer fragment, giving the impression of an
        incomplete but directionally correct response.
        """
        sentences = [s.strip() for s in correct_answer.split(".") if s.strip()]
        # Take only the first 1-2 sentences from the correct answer
        take = min(2, max(1, len(sentences) // 3))
        first_part = ". ".join(sentences[:take]) + "."

        frag = random.choice(GENERIC_PARTIAL_FRAGMENTS).replace("{domain}", domain)
        return f"{first_part} {frag}"

    @staticmethod
    def _get_incorrect_answer(domain: str, question: str, difficulty: str) -> str:
        """Return a plausible-sounding but wrong answer."""
        frag = random.choice(GENERIC_INCORRECT_FRAGMENTS).replace("{domain}", domain)

        # Add a red-herring technical detail scaled to difficulty
        wrong_extras = {
            "Easy": (
                " This basic misconception often arises because the naming convention "
                "is similar to an unrelated concept from a different technology stack."
            ),
            "Medium": (
                " This incorrect interpretation conflates two distinct patterns and "
                "would lead to improper implementation, security vulnerabilities, or "
                "significant performance degradation in production."
            ),
            "Hard": (
                " Applying this flawed understanding at scale would result in cascading "
                "failures, data inconsistency, and potential data loss. The correct "
                "approach requires understanding the distributed systems guarantees "
                "and failure modes that this incorrect answer ignores entirely."
            ),
        }
        return frag + wrong_extras.get(difficulty, "")
