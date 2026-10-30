"""Modern design tokens and CSS theme engine for StudyMate.

Supports:
- Real dynamic Light / Dark mode switching
- Production SaaS-grade typography (Plus Jakarta Sans, Inter)
- Responsive glassmorphism cards and borders
- Polish for chat bubbles, inputs, source expanders, and tables
"""

LIGHT_THEME_CSS = """
:root {
    --bg-page: #F8FAFC;
    --bg-surface: #FFFFFF;
    --bg-subtle: #F1F5F9;
    --bg-sidebar: #F8FAFC;
    --border-color: #E2E8F0;
    --border-subtle: #EDF2F7;
    
    --brand-primary: #1E3A8A;
    --brand-accent: #2563EB;
    --brand-hover: #1D4ED8;
    --brand-tint: #EFF6FF;
    
    --text-primary: #0F172A;
    --text-secondary: #475569;
    --text-muted: #64748B;
    --text-light: #94A3B8;
    
    --user-bubble: #EFF6FF;
    --user-border: #BFDBFE;
    --user-text: #1E3A8A;
    
    --badge-bg: #E0F2FE;
    --badge-text: #0369A1;
    --danger: #DC2626;
    --danger-tint: #FEF2F2;
    --success: #16A34A;
    --success-tint: #F0FDF4;
    
    --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 14px rgba(15, 23, 42, 0.06);
    --shadow-lg: 0 10px 30px rgba(15, 23, 42, 0.08);
}
"""

DARK_THEME_CSS = """
:root {
    --bg-page: #0B0F17;
    --bg-surface: #131A26;
    --bg-subtle: #1A2333;
    --bg-sidebar: #0D131F;
    --border-color: #222D3F;
    --border-subtle: #1B2433;
    
    --brand-primary: #38BDF8;
    --brand-accent: #0284C7;
    --brand-hover: #0EA5E9;
    --brand-tint: #082F49;
    
    --text-primary: #F8FAFC;
    --text-secondary: #CBD5E1;
    --text-muted: #94A3B8;
    --text-light: #64748B;
    
    --user-bubble: #162438;
    --user-border: #1E3A5F;
    --user-text: #7DD3FC;
    
    --badge-bg: #0C4A6E;
    --badge-text: #BAE6FD;
    --danger: #EF4444;
    --danger-tint: #450A0A;
    --success: #22C55E;
    --success-tint: #052E16;
    
    --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3);
    --shadow-md: 0 4px 14px rgba(0, 0, 0, 0.4);
    --shadow-lg: 0 10px 30px rgba(0, 0, 0, 0.5);
}
"""

CORE_STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* Base Reset & Application Canvas */
.stApp {
    background-color: var(--bg-page) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    transition: background-color 0.2s ease, color 0.2s ease;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

#MainMenu, footer {
    visibility: hidden !important;
}

.block-container {
    max-width: 1200px !important;
    padding-top: 1.4rem !important;
    padding-bottom: 3.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* Typography Hierarchy */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.02em !important;
    font-weight: 700 !important;
}

p, li, span, label, div {
    color: var(--text-primary);
    line-height: 1.6;
}

code, pre {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Sidebar Customization */
[data-testid="stSidebar"] {
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-color) !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.2rem;
    padding-left: 1.1rem;
    padding-right: 1.1rem;
}

/* Primary and Secondary Buttons */
button[kind="primary"],
button[kind="primaryFormSubmit"],
button[data-testid="stBaseButton-primary"],
button[data-testid="stBaseButton-primaryFormSubmit"] {
    background: var(--brand-primary) !important;
    color: #FFFFFF !important;
    border: 1px solid var(--brand-primary) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    padding: 0.5rem 1.2rem !important;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2) !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

button[kind="primary"] p,
button[kind="primaryFormSubmit"] p,
button[data-testid="stBaseButton-primary"] p,
button[data-testid="stBaseButton-primaryFormSubmit"] p {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

button[kind="primary"]:hover,
button[kind="primaryFormSubmit"]:hover,
button[data-testid="stBaseButton-primary"]:hover,
button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
    background: var(--brand-hover) !important;
    border-color: var(--brand-hover) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3) !important;
}

button[kind="secondary"],
button[data-testid="stBaseButton-secondary"] {
    background: var(--bg-surface) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    transition: all 0.18s ease !important;
}

button[kind="secondary"]:hover,
button[data-testid="stBaseButton-secondary"]:hover {
    background: var(--bg-subtle) !important;
    border-color: var(--brand-accent) !important;
    color: var(--brand-accent) !important;
    transform: translateY(-1px) !important;
}

/* Inputs & Form Controls */
[data-testid="stTextInput"] input {
    background: var(--bg-surface) !important;
    color: var(--text-primary) !important;
    border: 1.5px solid var(--border-color) !important;
    border-radius: 10px !important;
    padding: 0.6rem 0.9rem !important;
    font-size: 0.95rem !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}

[data-testid="stTextInput"] input:focus {
    border-color: var(--brand-accent) !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
}

/* Expanders / Accordions (Sources) */
[data-testid="stExpander"] {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    margin-bottom: 0.6rem !important;
    box-shadow: var(--shadow-sm) !important;
    overflow: hidden !important;
}

[data-testid="stExpander"] details {
    border: none !important;
}

[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    padding: 0.8rem 1.1rem !important;
    font-size: 0.92rem !important;
    transition: background 0.15s ease;
}

[data-testid="stExpander"] summary:hover {
    background: var(--bg-subtle) !important;
    color: var(--brand-accent) !important;
}

[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    padding: 0.2rem 1.1rem 1rem !important;
    border-top: 1px solid var(--border-subtle) !important;
    background: var(--bg-surface) !important;
}

/* Chat Message Rendering */
div[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.4rem 0 !important;
    gap: 0 !important;
}

[data-testid^="stChatMessageAvatar"] {
    display: none !important;
}

/* Custom User Message Flag Hook */
.sm-user-flag { display: none; }

div[data-testid="stChatMessage"]:has(.sm-user-flag) {
    background: var(--user-bubble) !important;
    border: 1px solid var(--user-border) !important;
    border-radius: 16px 16px 4px 16px !important;
    padding: 1rem 1.25rem !important;
    margin: 1.2rem 0 0.8rem !important;
    box-shadow: var(--shadow-sm) !important;
}

div[data-testid="stChatMessage"]:has(.sm-user-flag) p {
    color: var(--user-text) !important;
    font-weight: 500 !important;
    font-size: 1rem !important;
}

/* Custom Assistant Bubble */
.sm-assistant-bubble {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 1.25rem 1.4rem;
    margin-bottom: 0.8rem;
    box-shadow: var(--shadow-sm);
}

.sm-ans-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: var(--badge-bg);
    color: var(--badge-text);
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 0.25rem 0.65rem;
    border-radius: 6px;
    margin-bottom: 0.8rem;
}

/* File Uploader Dropzone */
[data-testid="stFileUploaderDropzone"] {
    background: var(--bg-surface) !important;
    border: 1.5px dashed var(--border-color) !important;
    border-radius: 12px !important;
    transition: border-color 0.2s ease, background 0.2s ease !important;
}

[data-testid="stFileUploaderDropzone"]:hover {
    border-color: var(--brand-accent) !important;
    background: var(--brand-tint) !important;
}

/* Clean Form Containers */
[data-testid="stForm"] {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 14px !important;
    padding: 0.9rem 1.1rem !important;
    box-shadow: var(--shadow-md) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border-color) !important;
    gap: 1.5rem !important;
}

.stTabs [data-baseweb="tab"] {
    color: var(--text-muted) !important;
    font-weight: 600 !important;
    padding: 0.6rem 0.2rem !important;
}

.stTabs [aria-selected="true"] {
    color: var(--brand-primary) !important;
    border-bottom: 2px solid var(--brand-primary) !important;
}

/* Custom Scrollbars */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: var(--text-muted);
}
</style>
"""


def apply_theme(theme: str = "light") -> str:
    """Return full CSS styles injecting current theme variables."""
    palette_css = DARK_THEME_CSS if theme == "dark" else LIGHT_THEME_CSS
    return f"<style>\n{palette_css}\n</style>\n{CORE_STYLES}"
