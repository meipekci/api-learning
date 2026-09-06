# Pulmonary Embolism Diagnosis with LLMs

A research project evaluating how reliably large language models (GPT-4o,
Gemini) can assist in diagnosing pulmonary embolism (PE) — a blood clot
blocking an artery in the lung — from a patient's history, symptoms, and
exam/lab findings in free-text form.

PE is difficult to diagnose and expensive to confirm (typically via CT
angiography), so clinicians must decide, based on history and symptoms alone,
whether to rule it out or pursue further imaging. This project explores
whether an LLM, given the same staged clinical information a physician would
have (triage history -> physical exam -> labs and risk scores), can produce
diagnoses and CT/mortality-risk recommendations that track the confirmed
ground-truth outcomes for a cohort of ~60 (de-identified) patients.

See [`METHODOLOGY.md`](METHODOLOGY.md) for the staged diagnostic workflow and
the clinical risk-scoring systems (WELLS, GENEVA, PERC, YEARS, PESI) used to
guide it.

## Project Structure

- **`llm_diagnosis_pipeline/`** — The pipeline used to produce this study's results:
  - `translate_patient_records.py` — parses the raw Turkish patient
    transcript and translates each patient's record into English.
  - `diagnosis_pipeline.py` — the main pipeline: queries an LLM per patient
    with progressively richer clinical context (triage -> +exam -> +labs and
    risk scores) for differential diagnosis, PE probability, and CT
    recommendation. Built around GPT-4o, but every model in the study was
    evaluated by swapping in that provider's API key.
  - `score_diagnosis_accuracy.py` / `pe_embedding_similarity.py` —
    exploratory side-analyses (top-k diagnostic accuracy scoring and
    text-embedding similarity to a "pulmonary embolism" reference concept),
    not part of the core pipeline above.
- **`gemini_scoring/`** — Scores Gemini model outputs (`gemini_flash*.csv`)
  by the same top-k PE hit-rate methodology as `score_diagnosis_accuracy.py`.
- **`tests_unit/`** — Pytest configuration and fixtures.

> **Note on data:** the raw, patient-level source files (case transcripts and
> input CSVs) are not included in this repository. Only code and
> already-aggregated model output/scoring files are checked in.

## Installation

### Prerequisites

1. Clone the repository:
   ```bash
   git clone https://github.com/meipekci/pe-diagnosis-llm.git
   ```

2. Install [`uv`](https://docs.astral.sh/uv/) (Python package/environment manager):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

### Environment Setup

1. Create and activate a virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Create a `.env` file with the API keys the scripts you're running need,
   e.g.:
   ```bash
   OPENAI_API_KEY=...
   ```

### Managing Dependencies

- Add a new dependency: `uv add <package-name>`
- Remove a dependency: `uv remove <package-name>`

## Running the Scripts

There isn't a single unified entry point — each script under
`llm_diagnosis_pipeline/` and `gemini_scoring/` is a standalone step (translation,
diagnosis querying, embedding comparison, or accuracy scoring). Run them
individually, e.g.:

```bash
python llm_diagnosis_pipeline/translate_patient_records.py
python llm_diagnosis_pipeline/diagnosis_pipeline.py
python llm_diagnosis_pipeline/score_diagnosis_accuracy.py
```

Most require the corresponding OpenAI/Gemini API key set in the environment
and the relevant input CSV present alongside the script.

## Development

### Testing
```bash
pytest
```

### Code Style
```bash
ruff check .
```

Or via [`just`](https://github.com/casey/just), see `justfile` for the full
list of recipes:
```bash
just setup   # create venv + install dependencies
just lint    # format and lint
just test    # run tests
```

## License

[MIT](LICENSE)
