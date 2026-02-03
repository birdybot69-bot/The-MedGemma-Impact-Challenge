### Project name
**ED Note Copilot: Offline Chest-Pain Documentation Assistant (MedGemma)**

### Your team
- **Birdy Bot** — implementation, prompt design, demo app, writeup, video script
- **Stanley Young** — project direction, review, submission

### Problem statement (Problem domain + Impact potential)
Emergency departments (EDs) run on time-critical, high-stakes documentation. Clinicians must rapidly turn noisy notes (triage + HPI + vitals + ECG + labs) into a coherent assessment and plan. In many clinical environments, **large closed models are not viable** due to privacy constraints, connectivity issues, or infrastructure limitations.

This project targets ED chest-pain notes because:
- It’s common and high impact (throughput + patient safety).
- Documentation quality matters: missing key details (risk factors, ECG/lab findings, escalation triggers) can cause delays.

**Impact estimate (illustrative):** if the assistant saves even **60–120 seconds per chest-pain chart** for a clinician and reduces rework, this can compound across a shift and improve timeliness of escalation for concerning features.

### Overall solution (Effective use of HAI‑DEF models)
We built an **offline-first documentation assistant** powered by **MedGemma (HAI‑DEF)**.

Given a raw ED note, the system produces:
1) A **structured ED summary** (CC/HPI/PMH/vitals/exam/ECG/labs/assessment/plan)
2) A **patient-friendly summary** (plain language; no new facts)
3) **Red flags** extracted from the note (transparent heuristics)
4) **Claim-to-evidence citations**: for each key claim, the assistant must point to an **exact substring** from the source note.

This is intentionally *documentation assistance*, not autonomous diagnosis.

### Technical details (Product feasibility)
**Model:** `google/medgemma-4b-it` (instruction-tuned; suitable for controllable structured outputs)

**Agentic workflow (verification loop):**
- **Draft step:** model returns strict JSON + `key_claims` with copied evidence snippets.
- **Verify step:** we validate that each evidence snippet exists in the note and record character spans.
- **Surface step:** the UI presents citations and red flags so a clinician can audit quickly.

**Demo app:** Streamlit UI to paste an ED note, run the pipeline, and view outputs + citations.

**Deployment story:** Designed for **offline** or restricted-network settings. Can run on a workstation GPU; can be adapted for smaller/quantized models.

**Safety + scope:** The assistant is framed as documentation support, avoids autonomous recommendations, and does not introduce facts not present in the input note.

### Links
- Source code: (to be provided)
- Demo video (<= 3 minutes): (to be provided)
- Reproducible notebook(s): (to be provided)
