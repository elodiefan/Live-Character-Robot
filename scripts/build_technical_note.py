"""Build the two-page submission technical note as a verified PDF."""

from __future__ import annotations

from pathlib import Path

from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "live-character-robot-technical-note.pdf"

NAVY = colors.HexColor("#18324A")
BLUE = colors.HexColor("#2D6A8A")
PALE_BLUE = colors.HexColor("#EAF3F7")
WARM = colors.HexColor("#F3C969")
INK = colors.HexColor("#20262B")
MUTED = colors.HexColor("#5B6870")


def box(drawing: Drawing, x: float, y: float, width: float, label: str) -> None:
    """Draw one architecture node."""
    drawing.add(Rect(x, y, width, 27, rx=5, ry=5, fillColor=PALE_BLUE, strokeColor=BLUE))
    drawing.add(
        String(
            x + width / 2,
            y + 9,
            label,
            fontName="Helvetica-Bold",
            fontSize=7.2,
            fillColor=NAVY,
            textAnchor="middle",
        )
    )


def arrow(drawing: Drawing, x1: float, y1: float, x2: float, y2: float) -> None:
    """Draw a directed connection."""
    drawing.add(Line(x1, y1, x2, y2, strokeColor=MUTED, strokeWidth=1.2))
    drawing.add(
        Polygon(
            [x2, y2, x2 - 5, y2 + 3, x2 - 5, y2 - 3],
            fillColor=MUTED,
            strokeColor=MUTED,
        )
    )


def architecture_diagram() -> Drawing:
    """Create the required architecture and data-flow diagram."""
    drawing = Drawing(530, 112)
    box(drawing, 0, 70, 72, "Camera")
    box(drawing, 0, 16, 72, "Microphone")
    box(drawing, 102, 70, 94, "Vision")
    box(drawing, 102, 16, 94, "Local speech")
    box(drawing, 228, 43, 92, "Controller")
    box(drawing, 228, 86, 92, "Scene memory")
    box(drawing, 352, 43, 82, "Safe actions")
    box(drawing, 466, 70, 64, "MuJoCo")
    box(drawing, 466, 16, 64, "Audio")
    arrow(drawing, 72, 83, 102, 83)
    arrow(drawing, 72, 29, 102, 29)
    arrow(drawing, 196, 83, 228, 61)
    arrow(drawing, 196, 29, 228, 52)
    arrow(drawing, 320, 56, 352, 56)
    arrow(drawing, 434, 56, 466, 79)
    arrow(drawing, 434, 56, 466, 29)
    drawing.add(Line(274, 70, 274, 86, strokeColor=MUTED, strokeWidth=1.2))
    drawing.add(
        String(
            265,
            74,
            "<> ",
            fontName="Helvetica-Bold",
            fontSize=7,
            fillColor=MUTED,
        )
    )
    return drawing


def footer(canvas, doc) -> None:
    """Draw restrained page furniture."""
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D8E0E5"))
    canvas.line(36, 30, letter[0] - 36, 30)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(36, 18, "Live Character Robot - Software Challenge")
    canvas.drawRightString(letter[0] - 36, 18, f"Page {doc.page} of 2")
    canvas.restoreState()


def build() -> None:
    """Generate the stable two-page PDF."""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=19,
        leading=22,
        textColor=NAVY,
        spaceAfter=3,
    )
    subtitle = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=10,
        textColor=MUTED,
        spaceAfter=9,
    )
    heading = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=13,
        textColor=BLUE,
        spaceBefore=6,
        spaceAfter=3,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=INK,
        spaceAfter=5,
    )
    small = ParagraphStyle(
        "Small",
        parent=body,
        fontSize=7.8,
        leading=9.7,
        spaceAfter=3,
    )
    callout = ParagraphStyle(
        "Callout",
        parent=body,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        textColor=NAVY,
        backColor=colors.HexColor("#FFF5D8"),
        borderColor=WARM,
        borderWidth=0.6,
        borderPadding=5,
        spaceBefore=4,
        spaceAfter=7,
    )

    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.42 * inch,
        bottomMargin=0.48 * inch,
        title="Live Character Robot - Technical Note",
        author="Elodie Fan",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="note", frames=[frame], onPage=footer)])

    story = [
        Paragraph("Live Character Robot", title),
        Paragraph("Technical note | End-to-end local character prototype", subtitle),
        Paragraph("Architecture and data flow", heading),
        architecture_diagram(),
        Spacer(1, 3),
        Paragraph(
            "Camera frames feed frontal-face engagement and HSV colored-object observation. "
            "Bounded microphone clips feed the CPU <b>faster-whisper base.en</b> model. "
            "Normalized text becomes a fixed motion command, scene-memory operation, or "
            "structured color goal. Only the deterministic controller writes joint state.",
            body,
        ),
        Paragraph("Protocol and model-to-action boundary", heading),
        Paragraph(
            "The internal protocol is a typed vocabulary: scene observations contain color, "
            "confidence, and horizontal position; goals contain a target color; actions are "
            "named primitives (<b>look-left, look-right, nod, shake, look-up, sleep</b>). "
            "Language never produces arbitrary joint values. The planner selects named "
            "actions, the motion layer converts named poses to ordered vectors, and every "
            "target is clamped to imported URDF limits before smoothstep interpolation.",
            body,
        ),
        Paragraph(
            "For <i>inspect the blue object</i>, vision first searches for the requested "
            "color and estimates left/center/right position. The planner chooses a bounded "
            "orientation-and-nod sequence. The camera observes again after execution; the "
            "character reports completion only if the requested target remains visible.",
            body,
        ),
        Paragraph("Simulation, character, and deployment choices", heading),
        Paragraph(
            "MuJoCo provides quick URDF import, joint-limit inspection, and an interactive "
            "CPU-capable simulation. Speech recognition is local to avoid API cost and data "
            "transfer. macOS say or Ubuntu espeak-ng provides offline voice. Sound effects "
            "and music are synthesized at runtime; a warm shade-color pulse represents lamp "
            "light. The target is Ubuntu 24.04, Python 3.12, four CPU cores, and 8 GB RAM.",
            body,
        ),
        Paragraph(
            "Data boundary: camera frames are processed in memory and discarded; recordings "
            "and raw measurement JSON remain local and Git-ignored; no cloud API is used.",
            callout,
        ),
        PageBreak(),
        Paragraph("Measured evidence", title),
        Paragraph("Development machine: Apple Silicon Mac, macOS 14.4.1", subtitle),
        Table(
            [
                ["Metric", "Result", "Method"],
                ["Speech-to-intent latency", "0.6683 s mean", "3 runs: 1.1560 / 0.4312 / 0.4177 s"],
                ["Warm speech-to-intent", "about 0.42 s", "Runs after initial local model load"],
                ["Peak resident memory", "529.9 MiB", "Process ru_maxrss"],
                ["CPU use", "241.3% of one core", "4.8379 CPU s; about 2.4 cores average"],
                ["Engagement accuracy", "100.0%", "360 frames across 3 guided trials"],
            ],
            colWidths=[1.55 * inch, 1.42 * inch, 3.95 * inch],
            repeatRows=1,
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 7.7),
                    ("LEADING", (0, 0), (-1, -1), 9.5),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE_BLUE]),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B7C5CD")),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            ),
        ),
        Spacer(1, 6),
        Paragraph(
            "The transcript and resolved intent were correct in all runtime runs. Engagement "
            "trials used clear glasses and direct gaze followed by three disengagement "
            "variants: turning away, leaving frame, and looking down/elsewhere. Visible, "
            "absent, and overall frame accuracy were each 100%. This is a small controlled "
            "test, not a population-level reliability claim.",
            small,
        ),
        Paragraph("Reliability and physical reasoning", heading),
        Paragraph(
            "Engagement dwell times suppress detection flicker. Silence skips one turn; "
            "camera failure yields no invented observation; missing voice/audio preserves "
            "visual motion; microphone failure ends cleanly. The five-DOF action vocabulary "
            "is bounded and all targets respect imported joint limits. A physical robot would "
            "also require actuator feedback, velocity and acceleration enforcement, collision "
            "limits, an emergency stop, watchdogs, and a hardware-specific controller.",
            body,
        ),
        Paragraph("Known limitations", heading),
        Paragraph(
            "<b>Perception:</b> color segmentation depends on lighting and supports six "
            "colors; frontal-face detection may degrade with glare, occlusion, or dim light. "
            "<b>Interaction:</b> fixed English phrases, five-second turns, one nonpersistent "
            "memory item, and no calibrated transform between camera and simulated lamp. "
            "<b>Simulation:</b> shade pulse is visual rather than photometric; no hardware "
            "dynamics or collision validation. <b>Deployment:</b> developed and measured on "
            "macOS; camera indexing, PipeWire audio, espeak-ng, OpenGL, and performance still "
            "require validation on the final Ubuntu laptop.",
            body,
        ),
        Paragraph("Ownership and scope", heading),
        Paragraph(
            "The prototype intentionally favors a smaller coherent local system over broad "
            "open-ended perception. AI-assisted development was used, while architecture, "
            "behavior, measurements, review, and final submission responsibility remain with "
            "the candidate.",
            body,
        ),
    ]
    doc.build(story)


if __name__ == "__main__":
    build()
