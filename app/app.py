import json
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="MedGemma Agentic Clinical Assistant (Demo)", layout="wide")

st.title("MedGemma Impact Challenge — Demo")
st.caption("Prototype UI — pipeline + model wiring TBD")

EXAMPLES_PATH = Path(__file__).resolve().parent / "examples.json"

examples = []
if EXAMPLES_PATH.exists():
    examples = json.loads(EXAMPLES_PATH.read_text())

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input")
    if examples:
        pick = st.selectbox("Load example", [e["name"] for e in examples])
        initial = next(e["note"] for e in examples if e["name"] == pick)
    else:
        initial = ""

    note = st.text_area("Clinical note", value=initial, height=420)

    run = st.button("Run (stub)", type="primary")

with col2:
    st.subheader("Output")
    if run:
        st.info("Model pipeline not implemented yet. This will run MedGemma + agentic checks.")
        st.json(
            {
                "structured_summary": {
                    "problem_list": ["..."],
                    "assessment": "...",
                    "plan": {"meds": [], "follow_up": [], "tests": []},
                },
                "patient_friendly_summary": "...",
                "red_flags": ["..."],
                "citations": [
                    {"claim": "...", "evidence": "...", "span": [0, 0]},
                ],
            }
        )

st.divider()

st.markdown(
    """
**Goal**: demonstrate a privacy-focused, offline-first clinical assistant built on **MedGemma**.

**Agentic workflow** (planned):
1) Parse note → candidate facts
2) Retrieve relevant snippets (local)
3) Draft structured output
4) Verify claims against retrieved evidence
5) Generate patient-friendly version + escalation warnings
"""
)
