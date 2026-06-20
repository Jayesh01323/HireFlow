"""
Resume Parser Page

Streamlit page for uploading resumes and parsing them using Gemini.
Extracts structured information such as skills, experience, and education.
"""

from __future__ import annotations

import streamlit as st

from src.database import get_all_resumes, init_db, save_resume
from src.parser import PDFExtractionError, ResumeParseError, extract_text_from_pdf, parse_resume
from src.schemas import Resume
from src.utils import get_env, load_env

load_env()
init_db()

st.set_page_config(page_title="Resume Parser", page_icon="📄", layout="wide")

st.title("📄 Resume Parser")
st.markdown(
    "Upload one or more PDF resumes to extract structured career data with Gemini."
)

if not get_env("GEMINI_API_KEY"):
    st.warning(
        "GEMINI_API_KEY is not set. Add your key to `.env` before parsing resumes.",
        icon="⚠️",
    )


def _render_list_section(title: str, items: list[str]) -> None:
    st.markdown(f"**{title}**")
    if items:
        for item in items:
            st.markdown(f"- {item}")
    else:
        st.caption("Not found")


def _render_resume(resume: Resume) -> None:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Name:** {resume.name or 'Not found'}")
        st.markdown(f"**Email:** {resume.email or 'Not found'}")
        st.markdown(f"**Phone:** {resume.phone or 'Not found'}")

    with col2:
        st.markdown("**Skills**")
        if resume.skills:
            skill_labels = [
                f"{skill.name} ({skill.level})" if skill.level else skill.name
                for skill in resume.skills
            ]
            st.markdown(", ".join(skill_labels))
        else:
            st.caption("Not found")

    _render_list_section("Education", resume.education)
    _render_list_section("Projects", resume.projects)
    _render_list_section("Experience", resume.experience)


uploaded_files = st.file_uploader(
    "Upload Resume(s) (PDF)",
    type=["pdf"],
    accept_multiple_files=True,
    help="Select one or more PDF resume files to parse.",
)

if st.button("Parse Resume(s)", type="primary", disabled=not uploaded_files):
    if not uploaded_files:
        st.info("Upload at least one PDF resume to continue.")
    else:
        progress = st.progress(0.0, text="Starting resume parsing...")
        success_count = 0

        for index, uploaded_file in enumerate(uploaded_files):
            filename = uploaded_file.name or f"resume_{index + 1}.pdf"
            progress.progress(
                index / len(uploaded_files),
                text=f"Processing {filename} ({index + 1}/{len(uploaded_files)})...",
            )

            with st.expander(f"Results: {filename}", expanded=True):
                try:
                    uploaded_file.seek(0)
                    raw_text = extract_text_from_pdf(uploaded_file)
                    parsed = parse_resume(raw_text)
                    resume_id = save_resume(filename, raw_text, parsed)

                    st.success(f"Parsed and saved successfully (ID: {resume_id}).")
                    _render_resume(parsed)

                    with st.expander("Raw extracted text"):
                        st.text_area(
                            "PDF text",
                            value=raw_text,
                            height=200,
                            disabled=True,
                            label_visibility="collapsed",
                        )

                    success_count += 1

                except PDFExtractionError as exc:
                    st.error(f"Could not read PDF `{filename}`: {exc}")
                except ResumeParseError as exc:
                    st.error(f"Could not parse `{filename}`: {exc}")
                except Exception as exc:
                    st.error(f"Unexpected error while processing `{filename}`: {exc}")

        progress.progress(1.0, text="Parsing complete.")
        if success_count:
            st.success(f"Successfully parsed {success_count} of {len(uploaded_files)} resume(s).")
        else:
            st.warning("No resumes were parsed successfully.")

st.divider()
st.subheader("Saved Resumes")

saved_resumes = get_all_resumes()

if not saved_resumes:
    st.info("No resumes saved yet. Upload and parse PDFs above.")
else:
    for record in saved_resumes:
        parsed = Resume.model_validate(record["parsed"])
        header = parsed.name or record["filename"]
        label = f"{header} — {record['filename']} (#{record['id']})"

        with st.expander(label):
            st.caption(f"Saved at {record['created_at']}")
            _render_resume(parsed)

            with st.expander("Raw extracted text"):
                st.text_area(
                    "PDF text",
                    value=record["raw_text"],
                    height=200,
                    disabled=True,
                    label_visibility="collapsed",
                    key=f"raw_text_{record['id']}",
                )
