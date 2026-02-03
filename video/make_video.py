import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
BG = (10, 14, 20)
FG = (240, 245, 250)
ACCENT = (99, 179, 237)
MUTED = (160, 170, 180)

HERE = Path(__file__).resolve().parent
OUTDIR = HERE / "build"
OUTDIR.mkdir(parents=True, exist_ok=True)

# Try to find a decent font
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]

def load_font(size=48, bold=False):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            return ImageFont.truetype(p, size=size)
    return ImageFont.load_default()

font_title = load_font(78)
font_h = load_font(52)
font_b = load_font(42)
font_s = load_font(34)


def wrap(draw, text, font, max_w):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        tw = draw.textlength(trial, font=font)
        if tw <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def slide(title, bullets=None, footer=None, filename="slide.png"):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)

    # header bar
    d.rectangle([0, 0, W, 16], fill=ACCENT)

    x0, y0 = 120, 120
    d.text((x0, y0), title, font=font_title, fill=FG)

    y = y0 + 140
    if bullets:
        for b in bullets:
            lines = wrap(d, b, font_b, W - 2*x0 - 80)
            # bullet dot
            d.ellipse([x0, y + 12, x0 + 16, y + 28], fill=ACCENT)
            tx = x0 + 36
            for i, ln in enumerate(lines):
                d.text((tx, y), ln, font=font_b, fill=FG)
                y += 56
            y += 18

    if footer:
        d.text((120, H - 90), footer, font=font_s, fill=MUTED)

    out = OUTDIR / filename
    im.save(out)
    return out


slides = []
slides.append(slide(
    "ED Note Copilot",
    [
        "Offline-first clinical documentation assistant for ED chest pain notes",
        "Built with MedGemma (HAI-DEF)",
        "Outputs: structured ED summary + patient-friendly summary + red flags",
    ],
    footer="MedGemma Impact Challenge — Main Track + Agentic Workflow Prize",
    filename="01_title.png",
))

slides.append(slide(
    "Why this matters",
    [
        "ED documentation is time-critical and noisy (triage, HPI, vitals, ECG, labs)",
        "Privacy / connectivity constraints often block cloud LLMs",
        "Goal: reduce rework and improve clarity without acting as clinical decision support",
    ],
    footer="Scope: documentation assistance (no autonomous diagnosis)",
    filename="02_problem.png",
))

slides.append(slide(
    "Agentic draft → verify",
    [
        "Draft step: MedGemma returns strict JSON + key claims",
        "Each claim must include a copied evidence snippet from the source note",
        "Verify step: check snippets exist and store character spans",
    ],
    footer="Verification makes the output auditable",
    filename="03_agentic.png",
))

slides.append(slide(
    "What the clinician sees",
    [
        "Structured summary (CC/HPI/PMH/vitals/exam/ECG/labs/A&P)",
        "Patient-friendly explanation (plain language; no new facts)",
        "Red flags + clickable citations back to the note",
    ],
    footer="Fast review: trust, but verify",
    filename="04_ui.png",
))

slides.append(slide(
    "Feasibility",
    [
        "Runs locally; designed for offline / edge environments",
        "Graceful fallback to deterministic baseline when model unavailable",
        "Streamlit demo + reproducible code in repo",
    ],
    footer="Thanks — GitHub link is in the writeup",
    filename="05_feasibility.png",
))

print("Wrote slides:")
for s in slides:
    print(s)
