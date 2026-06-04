# Synthetic Interview Dataset Generator

A production-ready Python tool for generating synthetic technical interview question-answer datasets across 15 domains — designed for AI interview system testing and validation.

---

## Features

- **15 technical domains**: Cloud Computing, AWS, Azure, GCP, Python, Java, Machine Learning, Data Science, SQL, DBMS, Networking, Cyber Security, DevOps, Linux, Full Stack Development
- **3 difficulty levels**: Easy, Medium, Hard
- **3 answer types per question**: correct, partial, incorrect — with balanced distribution
- **Duplicate prevention** via a used-question tracking cache
- **Validation module** with full report (distribution, coverage, errors)
- **JSON + CSV export** ready for downstream ML pipeline consumption
- **CLI interface** with `--samples`, `--domain`, `--difficulty`, `--stats-only` flags

---

## Project Structure

```
synthetic-interview-dataset-generator/
│
├── data/
│   ├── dataset.json           ← Primary export
│   ├── dataset.csv            ← CSV export
│   └── validation_samples.json← Sample preview
│
├── generators/
│   ├── question_generator.py  ← QuestionGenerator class
│   ├── answer_generator.py    ← AnswerGenerator class
│   └── label_generator.py     ← LabelGenerator class
│
├── validators/
│   └── dataset_validator.py   ← DatasetValidator class
│
├── exports/
│   └── exporter.py            ← DatasetExporter class
│
├── config.py                  ← All domain/question/answer templates
├── main.py                    ← CLI entry point + DatasetGenerator class
├── requirements.txt
└── README.md
```

---

## Installation

```bash
# Clone or download the project
cd synthetic-interview-dataset-generator

# Install dependencies (only pandas and faker are external)
pip install -r requirements.txt
```

Python 3.10+ required.

---

## Quick Start

```bash
# Generate 150 samples (default) across all domains
python main.py

# Generate 500 samples
python main.py --samples 500

# Generate only AWS questions
python main.py --domain AWS

# Generate only Hard questions
python main.py --difficulty Hard

# Filter both domain and difficulty
python main.py --domain Python --difficulty Medium --samples 60

# Print stats without exporting files
python main.py --stats-only

# Skip validation
python main.py --samples 200 --no-validate
```

---

## Output

### dataset.json

```json
[
  {
    "domain": "AWS",
    "difficulty": "Easy",
    "question": "What is Amazon EC2?",
    "answer": "Amazon EC2 (Elastic Compute Cloud) is a web service that provides resizable compute capacity in the cloud...",
    "label": "correct"
  },
  {
    "domain": "Python",
    "difficulty": "Medium",
    "question": "How does Python's asyncio event loop work?",
    "answer": "This is related to Python and involves managing some aspects...",
    "label": "partial"
  }
]
```

### Validation Report Example

```
============================================================
  DATASET VALIDATION REPORT
============================================================

── Statistics ──────────────────────────────────────────
  Total Samples     : 500
  Duplicates Found  : 0
  Domains Covered   : 15 / 15

  Label Distribution:
    correct     :   167  ( 33.4%)
    incorrect   :   167  ( 33.4%)
    partial     :   166  ( 33.2%)

  Difficulty Distribution:
    Easy        :   167  ( 33.4%)
    Hard        :   166  ( 33.2%)
    Medium      :   167  ( 33.4%)

  Status: PASSED ✓
============================================================
```

---

## Architecture

### DatasetGenerator (main.py)

Orchestrates the full pipeline:
1. Build balanced `(domain, difficulty)` task pairs
2. For each task: generate a question → generate answers → assign label → create record
3. Validate the complete dataset
4. Export to JSON + CSV

### QuestionGenerator

- Pulls from curated template pools in `config.py`
- Tracks used questions to prevent duplicates
- Falls back to synthesised questions when template pool is exhausted

### AnswerGenerator

- Looks up curated correct answers from `config.py`
- Builds partial answers by truncating correct answers + adding incompleteness fragments
- Generates incorrect answers from a pool of plausible-but-wrong fragments

### LabelGenerator

- Uses `itertools.cycle` over `['correct', 'partial', 'incorrect']`
- Guarantees balanced distribution regardless of sample count

### DatasetValidator

Checks for: missing fields, invalid values, empty answers, duplicate questions, label imbalance, domain coverage gaps.

---

## Extending

**Add a new domain**: Add its name to `DOMAINS` in `config.py`, then add question templates to `QUESTION_TEMPLATES[new_domain]` and optionally curated answers to `CORRECT_ANSWERS[new_domain]`.

**Add curated answers**: Add entries to `CORRECT_ANSWERS[domain][question_text]` in `config.py`.

**Increase sample cap**: Adjust `MAX_SAMPLES` in `config.py`.

---

## License

MIT License — free to use for research, education, and commercial AI system development.
