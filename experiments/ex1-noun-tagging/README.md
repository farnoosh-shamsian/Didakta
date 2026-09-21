# Experiment 1 — Noun tagging

Predicts Didakta case tags (`didakta_1`) for nouns in Homer.

| Path | Contents |
|---|---|
| `ML-Nouns.ipynb` | Main pipeline: TF-IDF baselines + Ancient Greek BERT fine-tune |
| `ML-sandbox.ipynb` | Scratch/exploration |
| `results/` | Metrics, predictions, error analysis (committed) |
| `models/` | Trained weights — **gitignored**, regenerate by running the notebook |

Input data lives in `../../data/` (shared across experiments). Paths are
resolved at runtime from the repo root, so the notebooks run from any
machine and from either the repo root or this folder.
