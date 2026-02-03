# MedGemma Impact Challenge — Project Skeleton

This repo is a working area for our Kaggle submission:
- Kaggle Writeup (<= 3 pages)
- Video demo (<= 3 minutes)
- Reproducible code + demo app

## Planned direction (draft)
**Agentic clinical documentation assistant** (offline-first):
- Turns messy clinical notes into structured care plan + patient-friendly summary
- Uses MedGemma (HAI-DEF) as the core model
- Adds an agentic workflow: retrieval, drafting, self-checking, red-flagging, and citation of source snippets.

## Repo layout
- `app/` Streamlit demo
- `src/` pipeline code
- `notebooks/` reproducible experiments
- `writeup/` Kaggle Writeup markdown + assets
- `video/` storyboard + script

## Quickstart (placeholder)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/app.py
```
