"""
Resume Parser Module

Extracts text from PDF resumes using PyMuPDF and structures
the content into Pydantic models via the Gemini API.
"""

from __future__ import annotations

import json
import logging
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Union

import fitz  # PyMuPDF
import google.generativeai as genai
from pydantic import ValidationError

from src.schemas import Resume as ResumeSchema
from src.utils import get_env, load_env

load_env()

logger = logging.getLogger(__name__)

PDFSource = Union[Path, bytes, BinaryIO]

GEMINI_MODEL = "gemini-3.1-flash-lite"
MAX_RESUME_CHARS = 30_000


class PDFExtractionError(Exception):
    """Raised when a PDF cannot be read or contains no extractable text."""


class ResumeParseError(Exception):
    """Raised when Gemini parsing or Pydantic validation fails."""


def extract_text_from_pdf(source: PDFSource) -> str:
    """Extract raw text from a PDF resume."""
    doc: fitz.Document | None = None

    try:
        if isinstance(source, Path):
            if not source.exists():
                raise PDFExtractionError(f"PDF file not found: {source}")
            doc = fitz.open(source)
        elif isinstance(source, bytes):
            doc = fitz.open(stream=source, filetype="pdf")
        else:
            data = source.read()
            if not data:
                raise PDFExtractionError("Uploaded PDF file is empty.")
            doc = fitz.open(stream=data, filetype="pdf")

        if doc.page_count == 0:
            raise PDFExtractionError("PDF has no pages.")

        pages = [page.get_text("text") for page in doc]
        text = "\n".join(pages).strip()

        if not text:
            raise PDFExtractionError(
                "No text could be extracted from the PDF. "
                "The file may be scanned images without OCR text."
            )

        return text

    except PDFExtractionError:
        raise
    except fitz.FileDataError as exc:
        raise PDFExtractionError(f"Invalid or corrupted PDF file: {exc}") from exc
    except Exception as exc:
        raise PDFExtractionError(f"Failed to read PDF: {exc}") from exc
    finally:
        if doc is not None:
            doc.close()


def _get_gemini_model() -> genai.GenerativeModel:
    api_key = get_env("GEMINI_API_KEY")
    if not api_key:
        raise ResumeParseError(
            "GEMINI_API_KEY is not configured. Add it to your .env file."
        )

    genai.configure(api_key=api_key)
    return genai.GenerativeModel(GEMINI_MODEL)


def parse_resume(text: str) -> ResumeSchema:
    """Parse resume text into structured data using Gemini JSON mode."""
    cleaned = text.strip()
    if not cleaned:
        raise ResumeParseError("Resume text is empty; nothing to parse.")

    truncated = cleaned[:MAX_RESUME_CHARS]
    prompt = (
        "Extract structured resume information from the text below.\n"
        "Return valid JSON only with this shape:\n"
        "{\n"
        '  "name": string or null,\n'
        '  "email": string or null,\n'
        '  "phone": string or null,\n'
        '  "skills": [{"name": string, "level": string or null}],\n'
        '  "education": [string],\n'
        '  "projects": [string],\n'
        '  "experience": [string]\n'
        "}\n"
        "Rules:\n"
        "- Return only information explicitly present in the resume.\n"
        "- Use null for missing scalar fields and empty lists for missing sections.\n"
        "- Do not invent or guess contact details.\n"
        "- For skills, include technical and soft skills when listed.\n"
        "- For education, projects, and experience, use concise bullet-style strings.\n\n"
        f"Resume text:\n{truncated}"
    )

    model = _get_gemini_model()

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
            ),
        )
    except Exception as exc:
        logger.exception("Gemini API request failed")
        raise ResumeParseError(f"Gemini API request failed: {exc}") from exc

    if not response.text:
        block_reason = getattr(response, "prompt_feedback", None)
        detail = f" ({block_reason})" if block_reason else ""
        raise ResumeParseError(f"Gemini returned an empty response{detail}.")

    try:
        parsed_data = json.loads(response.text)
    except json.JSONDecodeError as exc:
        logger.exception("Gemini response was not valid JSON")
        raise ResumeParseError(f"Gemini returned invalid JSON: {exc}") from exc

    try:
        return ResumeSchema.model_validate(parsed_data)
    except ValidationError as exc:
        logger.exception("Parsed resume failed Pydantic validation")
        raise ResumeParseError(f"Parsed resume failed validation: {exc}") from exc


def parse_pdf(source: PDFSource) -> tuple[str, ResumeSchema]:
    """Extract text from a PDF and parse it into a validated Resume model."""
    raw_text = extract_text_from_pdf(source)
    parsed = parse_resume(raw_text)
    return raw_text, parsed
