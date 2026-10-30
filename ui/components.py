"""Reusable UI presentation components for StudyMate."""

from pathlib import Path
from typing import Any, Dict, List, Optional
import streamlit as st


def format_latex(text: str) -> str:
    """Render common LaTeX delimiters correctly in Streamlit Markdown."""
    if not isinstance(text, str):
        return ""
    text = text.replace(r"\[", "$$")
    text = text.replace(r"\]", "$$")
    text = text.replace(r"\(", "$")
    text = text.replace(r"\)", "$")
    return text


def render_brand_header(subtitle: str = "Academic Knowledge Platform"):
    """Render global StudyMate brand badge and title."""
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.2rem;">
            <div style="
                background: linear-gradient(135deg, var(--brand-primary), var(--brand-accent));
                color: #FFFFFF;
                width: 38px;
                height: 38px;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.3rem;
                box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
            ">📚</div>
            <div>
                <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.35rem; font-weight: 800; color: var(--text-primary); line-height: 1.1;">StudyMate</div>
                <div style="font-size: 0.76rem; color: var(--text-muted); font-weight: 500;">{subtitle}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_card(icon: str, label: str, value: str, subtext: str = ""):
    """Render a clean metric card."""
    st.markdown(
        f"""
        <div style="
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 1.1rem 1.25rem;
            box-shadow: var(--shadow-sm);
            height: 100%;
        ">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.4rem;">
                <span style="font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted);">{label}</span>
                <span style="font-size: 1.25rem;">{icon}</span>
            </div>
            <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.85rem; font-weight: 700; color: var(--text-primary); line-height: 1.2;">
                {value}
            </div>
            {f'<div style="font-size: 0.76rem; color: var(--text-light); margin-top: 0.3rem;">{subtext}</div>' if subtext else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_source_passages(sources: List[Any]):
    """Render expandable source cards grouped by file and page numbers."""
    if not sources:
        return

    st.markdown(
        """
        <div style="
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--text-muted);
            border-top: 1px solid var(--border-color);
            padding-top: 0.9rem;
            margin: 1.1rem 0 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        ">
            <span>📚 Verified Source Material</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    grouped_sources: Dict[str, set] = {}
    for doc in sources:
        meta = doc.get("metadata") if isinstance(doc, dict) else (doc.metadata or {})
        source_path = meta.get("source") or meta.get("file_path") or "Study Material"
        filename = Path(str(source_path).replace("\\", "/")).name
        page = meta.get("page")
        if page is not None and str(page) != "Unknown":
            try:
                page_num = int(page) + 1
                grouped_sources.setdefault(filename, set()).add(page_num)
            except Exception:
                grouped_sources.setdefault(filename, set())
        else:
            grouped_sources.setdefault(filename, set())

    for filename, pages in grouped_sources.items():
        if pages:
            sorted_pages = sorted(pages)
            if len(sorted_pages) == 1:
                page_text = f"Page {sorted_pages[0]}"
            elif len(sorted_pages) == 2:
                page_text = f"Pages {sorted_pages[0]} and {sorted_pages[1]}"
            else:
                page_text = f"Pages {', '.join(map(str, sorted_pages[:-1]))} and {sorted_pages[-1]}"
        else:
            page_text = "Page Unknown"

        with st.expander(f"📄 {filename} — {page_text}"):
            for idx, doc in enumerate(sources, start=1):
                meta = doc.get("metadata") if isinstance(doc, dict) else (doc.metadata or {})
                source_path = meta.get("source") or meta.get("file_path") or ""
                doc_filename = Path(str(source_path).replace("\\", "/")).name

                if doc_filename == filename:
                    content = (
                        doc.get("page_content", "")
                        if isinstance(doc, dict)
                        else getattr(doc, "page_content", "")
                    )
                    if content:
                        st.caption(f"Relevant textbook excerpt {idx}")
                        st.markdown(format_latex(content))


def render_empty_state(icon: str, title: str, description: str, hint: str = ""):
    """Render a modern empty state block."""
    st.markdown(
        f"""
        <div style="
            text-align: center;
            padding: 3rem 1.5rem;
            background: var(--bg-surface);
            border: 1px dashed var(--border-color);
            border-radius: 16px;
            margin: 1.5rem 0;
        ">
            <div style="font-size: 2.6rem; margin-bottom: 0.5rem;">{icon}</div>
            <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.35rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.35rem;">
                {title}
            </div>
            <div style="color: var(--text-secondary); font-size: 0.92rem; max-width: 480px; margin: 0 auto;">
                {description}
            </div>
            {f'<div style="font-size: 0.8rem; color: var(--text-light); margin-top: 1rem; font-style: italic;">{hint}</div>' if hint else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )
