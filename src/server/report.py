import json
import os
from typing import Any, Dict, Optional

from PIL import Image


def generate_pdf(analysis_json: Dict[str, Any], overlay_path: Optional[str], out_path: str) -> str:
    """
    Generate a single-page PDF report for an analysis result.

    Attempts backends in order: reportlab -> fpdf -> Pillow (image->PDF fallback).

    Args:
        analysis_json: API response JSON (e.g., from /analyze)
        overlay_path: Path to overlay PNG (can be None). If None, will try to render nothing.
        out_path: Output PDF file path to write.

    Returns:
        The path to the written PDF file.

    Example:
        >>> from src.server.report import generate_pdf
        >>> analysis = {"mode": "mock", "prediction": {"objects": [{"label":"plant","confidence":0.87,"box":[10,10,100,100]}]}}
        >>> pdf_path = generate_pdf(analysis, overlay_path="static/overlays/example.png", out_path="reports/report.pdf")
        >>> print(pdf_path)

    Route suggestion (server):
        - Store analysis results and overlay path under a request_id when /analyze is called
        - Expose GET /report?request_id=<uuid> that:
            * Loads stored analysis and overlay path
            * Calls generate_pdf(analysis, overlay_path, out_path)
            * Sends the generated file with send_file
    """
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    # Try reportlab
    try:
        return _gen_with_reportlab(analysis_json, overlay_path, out_path)
    except Exception:
        pass

    # Try FPDF
    try:
        return _gen_with_fpdf(analysis_json, overlay_path, out_path)
    except Exception:
        pass

    # Fallback: Pillow image -> PDF (image-only with JSON as metadata comment)
    return _gen_with_pillow(analysis_json, overlay_path, out_path)


def _summary_lines(analysis_json: Dict[str, Any]) -> Dict[str, Any]:
    mode = analysis_json.get("mode", "n/a")
    pred = analysis_json.get("prediction", {}) or {}
    objects = pred.get("objects", []) or []
    return {
        "mode": mode,
        "num_objects": len(objects),
        "objects": objects,
    }


def _gen_with_reportlab(analysis_json: Dict[str, Any], overlay_path: Optional[str], out_path: str) -> str:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas

    c = canvas.Canvas(out_path, pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawString(20 * mm, height - 25 * mm, "AgriVision Analysis Report")

    # Summary
    s = _summary_lines(analysis_json)
    c.setFont("Helvetica", 11)
    y = height - 35 * mm
    c.drawString(20 * mm, y, f"Mode: {s['mode']}")
    y -= 6 * mm
    c.drawString(20 * mm, y, f"Objects: {s['num_objects']}")

    # JSON snippet
    snippet = json.dumps(analysis_json, ensure_ascii=False, indent=2)[:2000]
    text = c.beginText(20 * mm, y - 8 * mm)
    text.setFont("Helvetica", 8)
    for line in snippet.splitlines():
        text.textLine(line)
    c.drawText(text)

    # Overlay image
    if overlay_path and os.path.isfile(overlay_path):
        try:
            img = Image.open(overlay_path)
            iw, ih = img.size
            max_w = width - 40 * mm
            max_h = 120 * mm
            scale = min(max_w / iw, max_h / ih)
            dw, dh = iw * scale, ih * scale
            x = (width - dw) / 2
            y_img = 40 * mm
            c.drawImage(ImageReader(img), x, y_img, dw, dh, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    c.showPage()
    c.save()
    return out_path


def _gen_with_fpdf(analysis_json: Dict[str, Any], overlay_path: Optional[str], out_path: str) -> str:
    from fpdf import FPDF

    pdf = FPDF(unit="mm", format="A4")
    pdf.add_page()

    # Header
    pdf.set_font("Helvetica", style="B", size=18)
    pdf.cell(0, 10, "AgriVision Analysis Report", ln=1)

    # Summary
    s = _summary_lines(analysis_json)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 6, f"Mode: {s['mode']}", ln=1)
    pdf.cell(0, 6, f"Objects: {s['num_objects']}", ln=1)

    # JSON snippet block
    pdf.set_font("Courier", size=8)
    snippet = json.dumps(analysis_json, ensure_ascii=False, indent=2)[:2000]
    for line in snippet.splitlines():
        pdf.multi_cell(0, 4, line)

    # Overlay image
    if overlay_path and os.path.isfile(overlay_path):
        try:
            # Fit image to width with max height
            x = 10
            y = pdf.get_y() + 4
            max_w = 190
            pdf.image(overlay_path, x=x, y=y, w=max_w)
        except Exception:
            pass

    pdf.output(out_path)
    return out_path


def _gen_with_pillow(analysis_json: Dict[str, Any], overlay_path: Optional[str], out_path: str) -> str:
    # If overlay image exists, save it directly as single-page PDF
    if overlay_path and os.path.isfile(overlay_path):
        img = Image.open(overlay_path)
        img.convert("RGB").save(out_path, "PDF")
        return out_path

    # Else create a simple text image and export to PDF
    img = Image.new("RGB", (800, 600), (250, 250, 250))
    try:
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), "AgriVision Analysis Report", fill=(0, 0, 0))
        snippet = json.dumps(analysis_json, ensure_ascii=False, indent=2)[:2000]
        y = 60
        for line in snippet.splitlines():
            draw.text((20, y), line, fill=(0, 0, 0))
            y += 16
    except Exception:
        pass
    img.save(out_path, "PDF")
    return out_path
