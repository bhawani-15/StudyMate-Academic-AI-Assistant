"""About and Help view explaining StudyMate and how to use it effectively."""

import streamlit as st


def render_help_view():
    """Render the academic guide and platform explanation."""
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--brand-accent);">Learning Guide</div>
            <h1 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2.2rem; font-weight: 800; color: var(--text-primary); margin: 0;">
                ❓ About & Help
            </h1>
            <p style="font-size: 1rem; color: var(--text-secondary); margin-top: 0.35rem;">
                Learn how StudyMate works and how to get the most out of your study sessions.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. What StudyMate Does
    st.markdown(
        """
        <div style="
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 1.4rem;
            margin-bottom: 1.2rem;
            box-shadow: var(--shadow-sm);
        ">
            <h3 style="font-size: 1.15rem; font-weight: 700; color: var(--text-primary); margin: 0 0 0.5rem;">
                What is StudyMate?
            </h3>
            <p style="font-size: 0.92rem; color: var(--text-secondary); line-height: 1.7;">
                StudyMate is your personal academic companion. Unlike standard AI tools that guess or make things up, 
                StudyMate answers your questions <strong>strictly and truthfully</strong> using only the textbooks, lecture notes, 
                and PDFs you provide. Every answer includes verifiable page citations so you can cross-check with confidence.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. How StudyMate Works
    st.markdown(
        """
        <div style="
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 1.4rem;
            margin-bottom: 1.2rem;
            box-shadow: var(--shadow-sm);
        ">
            <h3 style="font-size: 1.15rem; font-weight: 700; color: var(--text-primary); margin: 0 0 0.5rem;">
                How StudyMate Helps You Study
            </h3>
            <div style="font-size: 0.92rem; color: var(--text-secondary); line-height: 1.7;">
                <ol style="margin-left: 1.2rem; padding-left: 0;">
                    <li><strong>Upload Your Notes & Books:</strong> Add your course textbooks, syllabus, or lecture slide PDFs to your Study Library.</li>
                    <li><strong>Smart Organization:</strong> StudyMate analyzes your documents and organizes every section with its exact page numbers.</li>
                    <li><strong>Ask Any Question:</strong> Type what you want to understand, review, or clarify in AI Study Chat.</li>
                    <li><strong>Relevance Matching:</strong> StudyMate locates the exact passages in your notes that discuss your question.</li>
                    <li><strong>Verified Answers:</strong> You receive an easy-to-understand academic explanation grounded directly in your notes, accompanied by page-level citations.</li>
                </ol>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Best Practices
    st.markdown(
        """
        <div style="
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 1.4rem;
            box-shadow: var(--shadow-sm);
        ">
            <h3 style="font-size: 1.15rem; font-weight: 700; color: var(--text-primary); margin: 0 0 0.5rem;">
                Tips for Effective Studying
            </h3>
            <div style="font-size: 0.92rem; color: var(--text-secondary); line-height: 1.7;">
                <div>• <strong>Ask Direct Questions:</strong> Ask focused questions like <em>"What are the four quantum numbers and what do they describe?"</em> or <em>"Summarize Chapter 2's key formulas."</em></div>
                <div>• <strong>Inspect the Sources:</strong> Expand the <strong>Verified Source Material</strong> tab beneath each answer to read the exact excerpt from your textbook.</div>
                <div>• <strong>Private & Isolated:</strong> Your uploaded materials and chat conversations are private to your account and never shared with other students.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
