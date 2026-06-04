# 🤖 Synthetic Interview Dataset Generator

A production-ready Python tool that automatically generates synthetic technical interview question-and-answer datasets for **AI interview system testing and validation**.

---

## 📌 What This Project Does

This tool generates fake (synthetic) interview questions and answers across **15 technical domains** with **3 difficulty levels** and **3 answer types** (correct, partial, incorrect).

It eliminates the need for real interview data when building and testing AI-based interview evaluation systems.

---

## 🗂️ Domains Covered

| # | Domain | # | Domain |
|---|--------|---|--------|
| 1 | Cloud Computing | 9 | DBMS |
| 2 | AWS | 10 | Networking |
| 3 | Azure | 11 | Cyber Security |
| 4 | GCP | 12 | DevOps |
| 5 | Python | 13 | Linux |
| 6 | Java | 14 | Full Stack Development |
| 7 | Machine Learning | 15 | Data Science |
| 8 | SQL | | |

---

## 🎯 Difficulty Levels

| Level | Example Question |
|-------|-----------------|
| **Easy** | What is Amazon EC2? |
| **Medium** | How does AWS Auto Scaling work? |
| **Hard** | Design a highly available multi-region AWS architecture |

---

## 📊 Answer Types Per Question

Every question gets **3 answer variants**:

| Label | Description | Example |
|-------|-------------|---------|
| `correct` | Fully accurate and complete | "Amazon EC2 is a web service that provides resizable compute capacity in the cloud..." |
| `partial` | Directionally correct but incomplete | "Amazon EC2 provides servers in the cloud. It handles some compute tasks." |
| `incorrect` | Wrong or misleading | "Amazon EC2 is a database service used to store files..." |

---

## 📁 Project Structure

```
synthetic-interview-dataset-generator/
│
├── data/
│   ├── dataset.json              ← Full generated dataset (150+ records)
│   ├── dataset.csv               ← Same data in CSV/Excel format
│   └── validation_samples.json   ← 15 hand-checked samples with notes
│
├── generators/
│   ├── question_generator.py     ← QuestionGenerator class
│   ├── answer_generator.py       ← AnswerGenerator class
│   └── label_generator.py        ← LabelGenerator class
│
├── validators/
│   └── dataset_validator.py      ← DatasetValidator class
│
├── exports/
│   └── exporter.py               ← DatasetExporter class
│
├── config.py                     ← All domain/question/answer templates
├── main.py                       ← Entry point + DatasetGenerator class
├── requirements.txt              ← Python dependencies
└── README.md                     ← This file
```

---

## ⚙️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/rudraprasads746-a11y/Dataset-generator.git
cd Dataset-generator

# 2. Install dependencies
pip install -r requirements.txt

# Python 3.10+ required
```

---

## 🚀 How to Run

```bash
# Default — generates 150 samples across all domains
python main.py

# Generate 500 samples
python main.py --samples 500

# Specific domain only
python main.py --domain AWS
python main.py --domain Python
python main.py --domain "Machine Learning"

# Specific difficulty only
python main.py --difficulty Easy
python main.py --difficulty Medium
python main.py --difficulty Hard

# Combine filters
python main.py --domain AWS --difficulty Hard --samples 60

# View statistics without exporting
python main.py --stats-only
```

---

## 📤 Sample Output

Each record in `dataset.json` follows this format:

```json
{
  "domain": "AWS",
  "difficulty": "Easy",
  "question": "What is Amazon EC2?",
  "answer": "Amazon EC2 (Elastic Compute Cloud) is a web service that provides resizable compute capacity in the cloud. It allows users to rent virtual servers with various CPU, memory, and storage configurations.",
  "label": "correct"
}
```

```json
{
  "domain": "Python",
  "difficulty": "Medium",
  "question": "What are Python decorators?",
  "answer": "Python decorators use the @ symbol and wrap functions. They can modify function behavior.",
  "label": "partial"
}
```

```json
{
  "domain": "Machine Learning",
  "difficulty": "Easy",
  "question": "What is overfitting in machine learning?",
  "answer": "Overfitting means the model is too simple and cannot learn patterns, resulting in high bias.",
  "label": "incorrect"
}
```

---

## ✅ Validation Report (Auto-generated)

After every run the tool prints a validation report:

```
============================================================
  DATASET VALIDATION REPORT
============================================================
  Total Samples     : 150
  Duplicates Found  : 0
  Domains Covered   : 15 / 15

  Label Distribution:
    correct     :    50  ( 33.3%)
    incorrect   :    50  ( 33.3%)
    partial     :    50  ( 33.3%)

  Difficulty Distribution:
    Easy        :    50  ( 33.3%)
    Hard        :    50  ( 33.3%)
    Medium      :    50  ( 33.3%)

  Status: PASSED ✓
============================================================
```

---

## 🛡️ How Key Problems Are Handled

### 1. Avoiding Repetitive Questions
The `QuestionGenerator` class maintains a `_used_questions` set that tracks every question already added to the dataset. Before adding a new question it checks this set — if the question was already used it is skipped. When a domain/difficulty pool is fully exhausted the set is cleared for that pool and recycling begins with a warning log.

### 2. Keeping Label Distribution Balanced
The `LabelGenerator` uses Python's `itertools.cycle` over `['correct', 'partial', 'incorrect']`. This means labels are assigned in a strict round-robin pattern: correct → partial → incorrect → correct → partial → incorrect... guaranteeing exactly equal distribution regardless of total sample count.

### 3. Maintaining Domain Relevance
All questions are sourced from curated domain-specific template pools defined in `config.py`. Each domain has 10–15 questions per difficulty level written specifically for that technology. The `AnswerGenerator` looks up curated correct answers keyed by domain and question text, ensuring answers are relevant to the domain.

---

## 🧪 Validation Samples

The file `data/validation_samples.json` contains **15 hand-checked samples** across 7 domains. Each entry includes a `hand_checked: true` flag and a `notes` field explaining why the label is correct. These samples can be used to manually verify that the labelling logic works as expected.

---

## 🏗️ Architecture

```
DatasetGenerator (main.py)
       │
       ├── QuestionGenerator   → pulls from 300+ curated questions per domain/difficulty
       ├── AnswerGenerator     → correct (curated) / partial (truncated) / incorrect (wrong fragments)
       ├── LabelGenerator      → round-robin cycle for perfect balance
       ├── DatasetValidator    → checks duplicates, empty fields, balance, coverage
       └── DatasetExporter     → writes JSON + CSV to data/ folder
```

---

## 📦 Dependencies

```
pandas>=2.0.0
```

All other modules (`json`, `csv`, `random`, `logging`, `itertools`, `argparse`) are part of Python's standard library — no additional installation needed.

---

## 👤 Author

**Rudraprasad**  
GitHub: [@rudraprasads746-a11y](https://github.com/rudraprasads746-a11y)
