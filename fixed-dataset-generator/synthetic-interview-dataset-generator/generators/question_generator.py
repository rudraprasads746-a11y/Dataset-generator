"""
generators/question_generator.py
Generates interview questions for given domains and difficulty levels.
"""

import logging
import random
from typing import List, Optional

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DOMAINS, DIFFICULTIES, QUESTION_TEMPLATES

logger = logging.getLogger(__name__)


class QuestionGenerator:
    """
    Generates interview questions for specified domains and difficulty levels.
    Tracks previously used questions to prevent duplicates.
    """

    def __init__(self):
        self._used_questions: set = set()
        logger.debug("QuestionGenerator initialized.")

    # ──────────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────────

    def generate(
        self,
        domain: str,
        difficulty: str,
        count: int = 1,
    ) -> List[str]:
        """
        Return *count* unique questions for the given domain and difficulty.

        Parameters
        ----------
        domain : str
            One of the domains defined in config.DOMAINS.
        difficulty : str
            One of 'Easy', 'Medium', or 'Hard'.
        count : int
            Number of questions to generate (default 1).

        Returns
        -------
        List[str]
            List of question strings.
        """
        if domain not in DOMAINS:
            raise ValueError(f"Unknown domain '{domain}'. Valid: {DOMAINS}")
        if difficulty not in DIFFICULTIES:
            raise ValueError(f"Unknown difficulty '{difficulty}'. Valid: {DIFFICULTIES}")

        pool = self._get_pool(domain, difficulty)
        available = [q for q in pool if q not in self._used_questions]

        if not available:
            # Reset used set for this domain/difficulty to allow recycling
            logger.warning(
                "Question pool exhausted for %s / %s — recycling questions.", domain, difficulty
            )
            self._used_questions = {
                q for q in self._used_questions if not (q in pool)
            }
            available = list(pool)

        selected = random.sample(available, min(count, len(available)))
        self._used_questions.update(selected)

        logger.debug("Generated %d question(s) for %s / %s.", len(selected), domain, difficulty)
        return selected

    def reset(self) -> None:
        """Clear the used-question cache."""
        self._used_questions.clear()
        logger.debug("QuestionGenerator cache reset.")

    @staticmethod
    def list_domains() -> List[str]:
        return list(DOMAINS)

    @staticmethod
    def list_difficulties() -> List[str]:
        return list(DIFFICULTIES)

    # ──────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _get_pool(domain: str, difficulty: str) -> List[str]:
        """Return the template question list for a domain + difficulty."""
        domain_templates = QUESTION_TEMPLATES.get(domain, {})
        pool = domain_templates.get(difficulty, [])

        if not pool:
            # Fallback: synthesise generic questions
            pool = QuestionGenerator._synthesise_questions(domain, difficulty)

        return pool

    @staticmethod
    def _synthesise_questions(domain: str, difficulty: str) -> List[str]:
        """
        Synthesise plausible questions when no template exists for a
        domain / difficulty combination.
        """
        level_hints = {
            "Easy": [
                "What is {domain}?",
                "Why is {domain} important?",
                "What are the main components of {domain}?",
                "What are common use cases for {domain}?",
                "What tools are typically used with {domain}?",
            ],
            "Medium": [
                "How does {domain} handle scalability challenges?",
                "What are the best practices for implementing {domain}?",
                "Explain the difference between X and Y in {domain}.",
                "How would you troubleshoot a common issue in {domain}?",
                "What are the security considerations in {domain}?",
            ],
            "Hard": [
                "Design a production-grade {domain} system for 10 million users.",
                "How would you optimize {domain} for high-throughput workloads?",
                "What are the architectural trade-offs in a {domain} implementation?",
                "How would you implement disaster recovery for a {domain} system?",
                "Explain the internals of {domain} and how to extend them.",
            ],
        }
        templates = level_hints.get(difficulty, level_hints["Medium"])
        return [t.replace("{domain}", domain) for t in templates]
