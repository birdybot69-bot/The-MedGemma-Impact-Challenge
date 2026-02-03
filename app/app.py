import json
from pathlib import Path

import streamlit as st

from medgemma_impact.pipeline import MedGemmaAgenticPipeline

st.set_page_config(page_title="ED Documentation Assistant (MedGemma)", layout="wide")

st.title("ED Documentation Assistant (Offline-first) — MedGemma Impact Challenge")
st.caption("Documentation assistant demo (not medical advice).")

EXAMPLES_PATH = Path(__file__).resolve().parent / "examples.json"

examples = []
if EXAMPLES_PATH.exists():
    examples = json.loads(EXAMPLES_PATH.read_text())

with st.sidebar:
    st.header("Settings")
    model_id = st.text_input("Model id", value="google/medgemma-4b-it")
    st.caption("Tip: keep a smaller model for fast demos.")

    show_raw = st.checkbox("Show raw model output", value=False)

pipeline = MedGemmaAgenticPipeline(model_id=model_id)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input")
    if examples:
        pick = st.selectbox("Load example", [e["name"] for e in examples])
        initial = next(e["note"] for e in examples if e["name"] == pick)
    else:
        initial = ""

    note = st.text_area("ED note", value=initial, height=420)

    run = st.button("Run", type="primary")

with col2:
    st.subheader("Output")
    if run:
        with st.spinner("Running pipeline..."):
            res = pipeline.run(note)

        st.markdown("### Structured summary")
        st.json(res.structured_summary)

        st.markdown("### Patient-friendly summary")
        st.write(res.patient_friendly_summary or "(empty)")

        st.markdown("### Red flags (from note)")
        if res.red_flags:
            for f in res.red_flags:
                st.warning(f)
        else:
            st.write("None detected.")

        st.markdown("### Evidence citations")
        if res.citations:
            for c in res.citations:
                st.write(f"**Claim:** {c['claim']}")
                st.code(c["evidence"], language="text")
                st.caption(f"Span: {c['span']}")
                st.divider()
        else:
            st.write("No citations produced.")

        if show_raw:
            st.markdown("### Raw model output")
            st.code(res.raw_model_output or "(none)")

st.divider()

st.markdown(
    """
**What this is:** a documentation assistant for ED chest pain notes.

**What this is not:** medical advice, diagnosis, or autonomous decision-making.

**Agentic workflow:**
1) Draft a structured summary
2) Produce key claims with copied evidence snippets
3) Validate citation spans and surface red flags
"""
)
