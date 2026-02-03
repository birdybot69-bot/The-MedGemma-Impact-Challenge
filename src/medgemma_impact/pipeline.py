"""Agentic documentation assistant pipeline (ED chest pain).

The competition is a hackathon judged on writeup + video + reproducible code.
This pipeline focuses on:
- *Documentation assistance* (not clinical decision automation)
- Offline-first / edge-friendly deployment
- Agentic verification: every key claim should be backed by evidence spans

We keep this module dependency-light; if `transformers` is available, it will run
MedGemma (or any HAI-DEF model). If not, we fall back to a deterministic
baseline so the demo still runs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class PipelineResult:
    structured_summary: Dict[str, Any]
    patient_friendly_summary: str
    red_flags: List[str]
    citations: List[Dict[str, Any]]
    raw_model_output: Optional[str] = None


def _find_span(text: str, snippet: str) -> Optional[Tuple[int, int]]:
    """Return (start,end) span of snippet in text (case-insensitive), if found."""
    if not snippet:
        return None
    lt, ls = text.lower(), snippet.lower()
    i = lt.find(ls)
    if i == -1:
        return None
    return i, i + len(snippet)


def _simple_red_flags(note: str) -> List[str]:
    n = note.lower()
    flags = []
    if "st depression" in n or "st depressions" in n:
        flags.append("ECG shows ST depression — consider ischemia; escalate per protocol.")
    if "troponin" in n and ("elevated" in n or "0." in n):
        flags.append("Troponin appears elevated — treat as possible ACS; consider serial troponins.")
    if "diaphoretic" in n or "diaphoresis" in n:
        flags.append("Diaphoresis with chest pain is concerning — monitor closely.")
    if "radiating" in n and "arm" in n:
        flags.append("Radiation to arm is concerning for ACS — prioritize evaluation.")
    return flags


class MedGemmaAgenticPipeline:
    """Two-stage agentic pipeline:

    1) Draft: produce structured JSON + brief summaries
    2) Verify: ensure every major claim is grounded in evidence spans

    For the hackathon demo, we keep verification simple and transparent.
    """

    def __init__(
        self,
        model_id: str = "google/medgemma-4b-it",  # default: small enough for demos
        device: str = "auto",
        max_new_tokens: int = 512,
    ):
        self.model_id = model_id
        self.device = device
        self.max_new_tokens = max_new_tokens

        self._generator = None
        self._transformers_error: Optional[str] = None

    def _lazy_init(self) -> None:
        if self._generator is not None or self._transformers_error is not None:
            return
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

            tok = AutoTokenizer.from_pretrained(self.model_id)
            model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                device_map=self.device,
                torch_dtype="auto",
            )
            self._generator = pipeline(
                "text-generation",
                model=model,
                tokenizer=tok,
            )
        except Exception as e:  # pragma: no cover
            self._transformers_error = f"transformers unavailable or model load failed: {e}"

    def _draft_with_model(self, note: str) -> Tuple[Dict[str, Any], str]:
        """Ask the model to produce a strict JSON draft."""
        self._lazy_init()
        if self._generator is None:
            structured, patient = self._draft_baseline(note)
            # Keep return signature consistent: ((structured, patient), raw_text)
            return (structured, patient), self._transformers_error

        system = (
            "You are an ED documentation assistant. You do NOT provide medical advice. "
            "You only restructure the clinician's note and draft documentation. "
            "Return STRICT JSON only."
        )

        prompt = f"""{system}

Input ED note:
{note}

Return JSON with keys:
- structured_summary: {{ chief_complaint, hpi, pmh, vitals, exam, ekg, labs, assessment, plan }}
- patient_friendly_summary: string (plain language, no new facts)
- key_claims: [{{claim, evidence_snippet}}] (each claim must cite a snippet copied verbatim from the note)

Rules:
- Do not invent facts.
- Keep plan generic and based only on what's already in the note.
- Evidence snippets must be exact substrings of the input note.
"""

        out = self._generator(
            prompt,
            max_new_tokens=self.max_new_tokens,
            do_sample=False,
            temperature=0.0,
            return_full_text=False,
        )
        text = out[0]["generated_text"] if out else ""
        # Try to parse JSON; if fail, fall back.
        import json

        try:
            data = json.loads(text)
            structured = data.get("structured_summary") or {}
            patient = data.get("patient_friendly_summary") or ""
            claims = data.get("key_claims") or []
        except Exception:
            structured, patient = self._draft_baseline(note)
            claims = []

        # Build citations from evidence snippets
        citations = []
        for c in claims:
            claim = (c.get("claim") or "").strip()
            ev = (c.get("evidence_snippet") or "").strip()
            span = _find_span(note, ev)
            if claim and ev and span:
                citations.append({"claim": claim, "evidence": ev, "span": list(span)})

        return (
            {
                **structured,
                "_citations": citations,
            },
            patient,
        ), text

    def _draft_baseline(self, note: str) -> Tuple[Dict[str, Any], str]:
        """Deterministic baseline that extracts a few fields via heuristics."""
        lines = [l.strip() for l in note.splitlines() if l.strip()]
        cc = next((l.split(":", 1)[1].strip() for l in lines if l.lower().startswith("cc:")), "Chest pain")
        vitals = next((l for l in lines if l.lower().startswith("vitals:")), "")
        ekg = next((l for l in lines if l.lower().startswith("ecg:")), "")
        labs = next((l for l in lines if l.lower().startswith("labs:")), "")
        assessment = next((l.split(":", 1)[1].strip() for l in lines if l.lower().startswith("assessment:")), "")
        plan = next((l.split(":", 1)[1].strip() for l in lines if l.lower().startswith("plan:")), "")

        structured = {
            "chief_complaint": cc,
            "hpi": " ".join([l for l in lines if l.lower().startswith("hpi:")]) or "",
            "pmh": " ".join([l for l in lines if "with" in l.lower() and "presents" in l.lower()]) or "",
            "vitals": vitals,
            "exam": " ".join([l for l in lines if l.lower().startswith("exam:")]) or "",
            "ekg": ekg,
            "labs": labs,
            "assessment": assessment,
            "plan": plan,
        }

        patient = (
            "This note describes a visit to the emergency department for chest pain. "
            "The clinician documented the symptoms, vital signs, ECG and lab results, and a plan for next steps."
        )

        # Citations from obvious lines
        citations: List[Dict[str, Any]] = []
        for claim, snippet in [
            ("Chief complaint is chest pain", next((l for l in lines if l.lower().startswith("cc:")), "")),
            ("ECG findings were documented", ekg),
            ("Troponin result was documented", labs),
        ]:
            span = _find_span(note, snippet)
            if snippet and span:
                citations.append({"claim": claim, "evidence": snippet, "span": list(span)})

        structured["_citations"] = citations
        return structured, patient

    def run(self, note: str) -> PipelineResult:
        # Draft
        (structured, patient), raw = self._draft_with_model(note)

        citations = structured.pop("_citations", [])
        red_flags = _simple_red_flags(note)

        # Minimal "verification": ensure citations point into the note
        verified = []
        for c in citations:
            span = c.get("span")
            if (
                isinstance(span, list)
                and len(span) == 2
                and isinstance(span[0], int)
                and isinstance(span[1], int)
                and 0 <= span[0] < span[1] <= len(note)
            ):
                verified.append(c)

        return PipelineResult(
            structured_summary=structured,
            patient_friendly_summary=patient,
            red_flags=red_flags,
            citations=verified,
            raw_model_output=raw,
        )
