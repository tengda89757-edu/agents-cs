# Multi-Agent Intelligent Tutoring System

This directory contains the fully modular, version-locked, and tested supplementary code for the manuscript *"A Multi-Agent Intelligent Tutoring System for Data Structures and Algorithms"*.

It was created to systematically address reviewer concerns about reproducibility (prompts, orchestration, guardrails, item-generation pipeline, dataset samples, and code availability).

## Directory Overview

```
reproducibility_package/
├── prompts/                # Version-locked agent prompts (JSON)
├── orchestration/          # Modular multi-agent orchestration
├── guardrails/             # Executable input-validation and fallback rules
├── scoring/                # Reference implementation of Eqs. (7)–(9)
├── item_generation/        # Template-first question generation pipeline
├── dataset/                # De-identified data samples & dictionary
├── tests/                  # Unit and integration tests
└── scripts/                # Executable entry points and verification tools
```

## Quick Start

### 1. Install Dependencies

```bash
cd reproducibility_package
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and set your API key:

```bash
cp .env.example .env
```

Edit `.env`:

```ini
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxx
MODEL_NAME=gpt-4o-mini
```

### 3. Run Verification

```bash
python scripts/verify_reproducibility.py
```

This executes all unit tests, checks prompt version consistency, and writes `reproducibility_report.json`.

### 4. Run Interactive Demo

```bash
python scripts/run_demo.py
```

### 5. Run Batch Simulation (Reproducible Hooks)

```bash
python scripts/run_batch_simulation.py
```

## Reproducibility Highlights

### Prompts
All four agent instructions are extracted from hard-coded strings into `prompts/*.json`. The orchestration layer dynamically loads and formats them at runtime, ensuring that any textual change is traceable via Git diff.

### Guardrails & Fallbacks
`guardrails/fallback_rules.py` implements **every** edge-case policy as an executable function (not a string comment). `validators.py` composes these functions into a validation pipeline. This directly addresses the reviewer's concern that "auxiliary fallback / edge-case branches were not saved to the degree needed to reconstruct pseudocode."

### Scoring Formulas (Eqs. 7–9)
`scoring/engine.py` provides the reference implementation with explicit:
- NaN guards
- Zero-division protection (`safe_divide`)
- Interval clipping (`clip`)
- Negative-target and boundary handling

`scoring/edge_cases.py` documents each code-level edge case in tabular form, and `scoring/tests.py` covers them with unit tests.

### Item-Generation Pipeline
`item_generation/pipeline.py` selects a structured template from a fixed bank (`question_templates.json`), fills placeholders deterministically, and only delegates creative sub-parts (code snippets, distractors) to the LLM. Setting `rng_seed` guarantees an identical question skeleton for the same student state.

### Orchestration Modularity
All side effects (`time.sleep`, `print`) are injected via hooks (`transfers.py`). The default `PRODUCTION_HOOKS` provide delays and console output, while `REPRODUCIBLE_HOOKS` are no-ops, enabling deterministic batch simulation and testing.

## Dataset

- `dataset/experimental_sample.csv` — First 5 rows of the experimental group (N = 41)
- `dataset/control_sample.csv` — First 5 rows of the control group (N = 21)
- `dataset/data_dictionary.md` — Full variable definitions, formula references, and encoding tables

## Known Limitations

See `REPRODUCIBILITY_MANIFEST.md` for a complete list of:
- **What is reproduced** (core orchestration, all guardrails, scoring formulas, item-generation pipeline, dataset samples)
- **What is not reproduced** (network-timeout retry loops, experimental LLM temperature sweeps — these were not archived in the original development environment)

## Citation

If you use this code or dataset, please cite the associated manuscript.

## License

MIT License
