"""Render PDF pages and extract faithful Markdown through a vision-capable Ollama API."""

from __future__ import annotations

import base64
from io import BytesIO
import re
import unicodedata
import uuid
from collections import Counter
from pathlib import Path

import pypdfium2 as pdfium
import requests

from config import settings


def _tokens(text: str) -> Counter[str]:
    normalized = unicodedata.normalize("NFKC", text or "").casefold()
    return Counter(re.findall(r"[^\W_]+", normalized, flags=re.UNICODE))


def _coverage(source_text: str, extracted_text: str) -> dict:
    source = _tokens(source_text)
    extracted = _tokens(extracted_text)
    source_count = sum(source.values())
    matched = sum((source & extracted).values())
    return {
        "source_tokens": source_count,
        "matched_tokens": matched,
        "recall_percent": round(100 * matched / source_count, 1) if source_count else None,
    }


def _require_vision_model(model: str) -> None:
    try:
        response = requests.post(
            f"{settings.OLLAMA_URL}/api/show", json={"model": model}, timeout=(10, 45)
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"Cannot reach the Ollama API for PDF extraction: {exc}") from exc
    if response.status_code != 200:
        try:
            detail = response.json().get("error", "")
        except ValueError:
            detail = response.text
        detail = " ".join(str(detail).split())[:300]
        suffix = f" {detail}" if detail else ""
        raise RuntimeError(f"Ollama could not load PDF extraction model {model!r}.{suffix}")
    try:
        capabilities = response.json().get("capabilities") or []
    except ValueError as exc:
        raise RuntimeError("Ollama returned an invalid model description for PDF extraction.") from exc
    if capabilities and "vision" not in capabilities:
        raise RuntimeError(
            f"Ollama model {model!r} does not support vision. Set PDF_EXTRACTION_OLLAMA_MODEL "
            "to a vision-capable model; the PDF is not sent to a local AI model."
        )


def _extract_page_markdown(model: str, page_number: int, image: bytes) -> str:
    prompt = f"""Transcribe page {page_number} of a scientific paper into Markdown.
This is OCR and faithful document conversion, not summarization or analysis.
Rules:
- Preserve all readable words, numbers, units, punctuation, equations, headings, footnotes, captions, and references in reading order.
- Reproduce tables as Markdown tables when their rows and columns are legible; preserve every cell and value.
- Keep the original wording. Never paraphrase, infer, correct, or add facts.
- If a small region cannot be read, mark only that region as [illegible]. Do not omit surrounding readable content.
- Include figure/table labels and captions. Do not describe visual details that contain no readable text.
- Return only the page's Markdown, with no preface, summary, or code fence."""
    try:
        response = requests.post(
            f"{settings.OLLAMA_URL}/api/chat",
            json={
                "model": model,
                "messages": [{
                    "role": "user",
                    "content": prompt,
                    "images": [base64.b64encode(image).decode("ascii")],
                }],
                "stream": False,
                "options": {"temperature": 0},
            },
            timeout=(15, 600),
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"Ollama API failed while extracting PDF page {page_number}: {exc}") from exc
    if response.status_code != 200:
        try:
            detail = response.json().get("error", "")
        except ValueError:
            detail = response.text
        detail = " ".join(str(detail).split())[:300]
        suffix = f": {detail}" if detail else ""
        raise RuntimeError(f"Ollama API returned HTTP {response.status_code} on PDF page {page_number}{suffix}.")
    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError(f"Ollama returned an invalid response for PDF page {page_number}.") from exc
    content = ((payload.get("message") or {}).get("content") or "").strip()
    content = re.sub(r"^```(?:markdown|md)?\s*|\s*```$", "", content, flags=re.IGNORECASE).strip()
    if not content:
        raise RuntimeError(f"Ollama returned no Markdown for PDF page {page_number}.")
    return content


def extract_pdf_to_markdown(pdf_path: Path, native_pdf_pages: tuple | list = ()) -> dict:
    """Convert a PDF page-by-page using the configured remote Ollama vision model."""
    pdf_path = Path(pdf_path)
    model = settings.PDF_EXTRACTION_OLLAMA_MODEL
    if not model:
        raise RuntimeError("PDF_EXTRACTION_OLLAMA_MODEL is empty; configure a vision model in the app environment.")
    try:
        pdf = pdfium.PdfDocument(str(pdf_path))
    except Exception as exc:
        raise RuntimeError(f"Could not open PDF for page rendering: {exc}") from exc
    page_count = len(pdf)
    if page_count < 1:
        pdf.close()
        raise RuntimeError("The PDF has no pages to extract.")

    _require_vision_model(model)
    source_pages = {int(number): text or "" for number, text in native_pdf_pages}
    page_markdown = []
    page_reports = []
    try:
        for page_index in range(page_count):
            page_number = page_index + 1
            page = pdf[page_index]
            bitmap = page.render(scale=1.8)
            rendered = bitmap.to_pil()
            image_buffer = BytesIO()
            rendered.save(image_buffer, format="JPEG", quality=84)
            image = image_buffer.getvalue()
            rendered.close()
            image_buffer.close()
            bitmap.close()
            page.close()
            extracted_text = _extract_page_markdown(model, page_number, image)
            del image
            page_markdown.append(f"<!-- PDF_PAGE:{page_number} -->\n\n{extracted_text}")

            coverage = _coverage(source_pages.get(page_number, ""), extracted_text)
            coverage.update({
                "page": page_number,
                "status": "no_native_text" if not coverage["source_tokens"] else
                          "low_coverage" if coverage["recall_percent"] < 60 else "covered",
            })
            page_reports.append(coverage)
    finally:
        pdf.close()

    markdown = "\n\n".join(page_markdown).strip() + "\n"
    low_pages = [item["page"] for item in page_reports if item["status"] == "low_coverage"]
    no_text_pages = [item["page"] for item in page_reports if item["status"] == "no_native_text"]
    native_text = "\n".join(source_pages.values())
    overall = _coverage(native_text, re.sub(r"<!-- PDF_PAGE:\d+ -->", "", markdown))

    markdown_path = pdf_path.with_suffix(".ollama.md")
    temporary = markdown_path.with_name(f".{markdown_path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(markdown, encoding="utf-8", newline="")
        temporary.replace(markdown_path)
    finally:
        if temporary.exists():
            temporary.unlink()

    warning = None
    if low_pages:
        warning = "Low text-layer overlap on pages " + ", ".join(map(str, low_pages)) + "; review these pages against the source PDF."
    if no_text_pages:
        ocr_warning = "Pages " + ", ".join(map(str, no_text_pages)) + " have no native text layer and rely on vision OCR; review them against the PDF."
        warning = f"{warning} {ocr_warning}" if warning else ocr_warning
    return {
        "markdown": markdown,
        "markdown_path": markdown_path,
        "coverage": {
            "method": "normalized_token_overlap_against_pdf_text_layer",
            "engine": "ollama_vision_api",
            "model": model,
            "page_count": len(page_reports),
            "low_coverage_pages": low_pages,
            "pages_without_native_text": no_text_pages,
            "pages": page_reports,
            "warning": warning,
            **overall,
        },
    }
