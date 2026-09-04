import streamlit as st
import time
from datetime import datetime
from agent import run_research_agent

# ============================================================================
# PAGE CONFIGURATION & STYLING
# ============================================================================

st.set_page_config(
    page_title="AIPRA — Research, considered",
    page_icon="◈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --ink: #241F1C;
            --stone: #6E6459;
            --parchment: #FAF6F0;
            --panel: #F4EEE4;
            --aubergine: #4A2A3D;
            --gilt: #A9824C;
            --hairline: #E4DDD1;
        }

        .stApp {
            background: var(--parchment);
            color: var(--ink);
        }

        [data-testid="stHeader"] {
            background: transparent;
            box-shadow: none;
        }

        .main .block-container {
            max-width: 720px;
            padding-top: 3rem;
            padding-bottom: 4rem;
        }

        /* Typography */
        h1, h2, h3, .display {
            font-family: 'Cormorant Garamond', Georgia, serif;
            color: var(--ink);
            font-weight: 500;
            letter-spacing: 0.2px;
        }

        p, span, div, label, input, textarea, select {
            font-family: 'Inter', sans-serif;
        }

        .eyebrow {
            font-family: 'Inter', sans-serif;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 2.5px;
            text-transform: uppercase;
            color: var(--gilt);
        }

        .masthead {
            text-align: center;
            padding-bottom: 2.5rem;
            border-bottom: 1px solid var(--hairline);
            margin-bottom: 2.5rem;
        }

        .masthead h1 {
            font-size: 44px;
            margin: 6px 0 4px 0;
            font-style: italic;
        }

        .masthead .sub {
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            color: var(--stone);
            letter-spacing: 0.5px;
        }

        /* Stats row — quiet, typographic, no badges */
        .stat-row {
            display: flex;
            justify-content: center;
            gap: 48px;
            margin: 1.5rem 0 2.5rem 0;
        }

        .stat {
            text-align: center;
        }

        .stat .num {
            font-family: 'Cormorant Garamond', serif;
            font-size: 30px;
            font-weight: 600;
            color: var(--aubergine);
            line-height: 1;
        }

        .stat .lbl {
            font-family: 'Inter', sans-serif;
            font-size: 10px;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            color: var(--stone);
            margin-top: 4px;
        }

        /* Section rule */
        .rule {
            height: 1px;
            background: var(--hairline);
            margin: 2.5rem 0;
            border: none;
        }

        .section-label {
            font-family: 'Inter', sans-serif;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: var(--gilt);
            margin-bottom: 0.5rem;
        }

        /* Inputs — underline style, no boxes */
        .stTextInput > div > div > input {
            background: transparent !important;
            border: none !important;
            border-bottom: 1px solid var(--hairline) !important;
            border-radius: 0 !important;
            color: var(--ink) !important;
            font-family: 'Cormorant Garamond', serif !important;
            font-size: 22px !important;
            font-style: italic;
            padding: 10px 2px !important;
        }

        .stTextInput > div > div > input:focus {
            border-bottom: 1px solid var(--aubergine) !important;
            box-shadow: none !important;
        }

        .stTextInput > div > div > input::placeholder {
            color: var(--stone);
            opacity: 0.6;
        }

        .stSelectbox > div > div {
            background: transparent !important;
            border: none !important;
            border-bottom: 1px solid var(--hairline) !important;
            border-radius: 0 !important;
        }

        .stSlider [data-baseweb="slider"] {
            padding-top: 8px;
        }

        /* Button — outlined small caps, not a pill */
        .stButton > button {
            background: transparent;
            color: var(--aubergine);
            border: 1px solid var(--aubergine);
            border-radius: 0;
            padding: 10px 22px;
            font-family: 'Inter', sans-serif;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            transition: all 0.25s ease;
            width: 100%;
        }

        .stButton > button:hover {
            background: var(--aubergine);
            color: var(--parchment);
        }

        /* Summary block */
        .summary-block {
            padding: 1.75rem 0;
            border-top: 1px solid var(--hairline);
            border-bottom: 1px solid var(--hairline);
            margin: 1.5rem 0 2rem 0;
        }

        .summary-block .query-tag {
            font-family: 'Inter', sans-serif;
            font-size: 12px;
            color: var(--stone);
            font-style: italic;
            margin-bottom: 10px;
        }

        .summary-block p {
            font-size: 17px;
            line-height: 1.75;
            color: var(--ink);
        }

        /* Findings — editorial numbered list */
        .finding {
            display: flex;
            gap: 20px;
            padding: 1.4rem 0;
            border-bottom: 1px solid var(--hairline);
        }

        .finding:last-child {
            border-bottom: none;
        }

        .finding .num {
            font-family: 'Cormorant Garamond', serif;
            font-style: italic;
            font-size: 30px;
            color: var(--gilt);
            min-width: 36px;
            line-height: 1;
        }

        .finding .txt {
            font-size: 15.5px;
            line-height: 1.7;
            color: var(--ink);
            padding-top: 3px;
        }

        /* Sources — hairline list, no cards */
        .source-row {
            padding: 1rem 0;
            border-bottom: 1px solid var(--hairline);
            text-decoration: none;
            display: block;
        }

        .source-row:last-child {
            border-bottom: none;
        }

        .source-row .idx {
            font-family: 'Cormorant Garamond', serif;
            font-style: italic;
            color: var(--gilt);
            font-size: 14px;
            margin-right: 8px;
        }

        .source-row .title {
            color: var(--ink);
            font-weight: 500;
            font-size: 14.5px;
        }

        .source-row .url {
            color: var(--stone);
            font-size: 12px;
            margin: 3px 0 6px 0;
        }

        .source-row .snip {
            color: var(--stone);
            font-size: 13px;
            line-height: 1.55;
        }

        /* Progress */
        .stProgress > div > div {
            background-color: var(--aubergine) !important;
        }

        .status-line {
            font-family: 'Inter', sans-serif;
            font-size: 12px;
            color: var(--stone);
            font-style: italic;
            text-align: center;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: var(--panel);
            border-right: 1px solid var(--hairline);
        }

        [data-testid="stSidebar"] h3 {
            font-size: 18px;
        }

        .history-item {
            padding: 0.85rem 0;
            border-bottom: 1px solid var(--hairline);
        }

        .history-item .ts {
            font-size: 10px;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: var(--gilt);
        }

        .history-item .q {
            font-size: 13px;
            color: var(--ink);
            margin: 4px 0;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE
# ============================================================================

if "research_history" not in st.session_state:
    st.session_state.research_history = []
if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0
if "milestones" not in st.session_state:
    st.session_state.milestones = []

def get_level():
    q = st.session_state.total_queries
    if q == 0: return "Novice"
    if q < 5: return "Scholar"
    if q < 10: return "Researcher"
    if q < 20: return "Expert"
    return "Master researcher"

def format_time(seconds):
    return f"{int(seconds)}s" if seconds < 60 else f"{seconds/60:.1f}m"

# ============================================================================
# MASTHEAD
# ============================================================================

st.markdown("""
    <div class="masthead">
        <div class="eyebrow">Research, considered</div>
        <h1>AIPRA</h1>
        <div class="sub">An intelligent research companion</div>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="stat-row">
        <div class="stat"><div class="num">{st.session_state.total_queries}</div><div class="lbl">Queries</div></div>
        <div class="stat"><div class="num">{get_level()}</div><div class="lbl">Standing</div></div>
        <div class="stat"><div class="num">{len(st.session_state.milestones)}</div><div class="lbl">Milestones</div></div>
    </div>
""", unsafe_allow_html=True)

# ============================================================================
# SEARCH
# ============================================================================

st.markdown('<div class="section-label">Ask a question</div>', unsafe_allow_html=True)

query = st.text_input(
    "Research question",
    placeholder="What would you like to understand today?",
    label_visibility="collapsed"
)

col1, col2, col3 = st.columns([1.3, 1, 1])
with col1:
    depth = st.selectbox("Depth", ["Quick overview", "Standard", "Deep analysis"], index=1, label_visibility="collapsed")
with col2:
    num_sources = st.slider("Sources", 3, 10, 6, label_visibility="collapsed")
with col3:
    search_button = st.button("Begin research")

st.markdown('<hr class="rule">', unsafe_allow_html=True)

# ============================================================================
# RESEARCH EXECUTION
# ============================================================================

if search_button and query:
    st.session_state.total_queries += 1

    progress_container = st.container()
    results_container = st.container()

    with progress_container:
        status = st.empty()
        bar = st.progress(0)
        start_time = time.time()

        stages = ["Drafting a research plan", "Gathering sources", "Weighing the evidence"]
        for i, stage in enumerate(stages):
            bar.progress((i + 1) * 30)
            status.markdown(f'<div class="status-line">{stage} …</div>', unsafe_allow_html=True)
            time.sleep(0.4)

        try:
            result = run_research_agent(query, depth=depth, num_sources=num_sources)
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.stop()

        elapsed = time.time() - start_time
        bar.progress(100)
        status.markdown(f'<div class="status-line">Complete in {format_time(elapsed)}</div>', unsafe_allow_html=True)
        time.sleep(0.4)

    progress_container.empty()

    with results_container:
        st.markdown(f"""
            <div class="summary-block">
                <div class="query-tag">On the question of “{query}”</div>
                <p>{result.get('summary', 'No summary available.')}</p>
            </div>
        """, unsafe_allow_html=True)

        findings = result.get('findings', [])
        if findings:
            st.markdown('<div class="section-label">Key findings</div>', unsafe_allow_html=True)
            findings_html = ""
            roman = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]
            for i, finding in enumerate(findings):
                num = roman[i] if i < len(roman) else str(i + 1)
                findings_html += f'<div class="finding"><div class="num">{num}</div><div class="txt">{finding}</div></div>'
            st.markdown(findings_html, unsafe_allow_html=True)
            st.markdown('<hr class="rule">', unsafe_allow_html=True)

        sources = result.get('sources', [])
        if sources:
            st.markdown('<div class="section-label">Sources consulted</div>', unsafe_allow_html=True)
            sources_html = ""
            for idx, source in enumerate(sources[:6], 1):
                sources_html += f"""
                    <a href="{source.get('url', '#')}" target="_blank" class="source-row">
                        <div class="title"><span class="idx">{idx:02d}</span>{source.get('title', 'Untitled')}</div>
                        <div class="url">{source.get('url', '')}</div>
                        <div class="snip">{source.get('snippet', '')[:150]}</div>
                    </a>
                """
            st.markdown(sources_html, unsafe_allow_html=True)

        # milestones — quiet, no confetti
        if st.session_state.total_queries in (1, 5, 10, 20):
            label = {1: "First research", 5: "Five questions asked", 10: "Ten questions asked", 20: "Twenty questions asked"}[st.session_state.total_queries]
            if label not in st.session_state.milestones:
                st.session_state.milestones.append(label)

        st.session_state.research_history.append({
            "query": query,
            "timestamp": datetime.now().strftime("%d %b, %H:%M"),
            "findings_count": len(findings)
        })

# ============================================================================
# SIDEBAR — HISTORY
# ============================================================================

with st.sidebar:
    st.markdown('<h3>History</h3>', unsafe_allow_html=True)

    if st.session_state.research_history:
        for entry in reversed(st.session_state.research_history[-6:]):
            st.markdown(f"""
                <div class="history-item">
                    <div class="ts">{entry['timestamp']}</div>
                    <div class="q">{entry['query'][:60]}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size:13px; color:#6E6459;">Nothing yet — ask your first question.</p>', unsafe_allow_html=True)

    if st.session_state.milestones:
        st.markdown('<hr class="rule">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Milestones</div>', unsafe_allow_html=True)
        for m in st.session_state.milestones:
            st.markdown(f'<p style="font-size:13px; font-style:italic; color:#4A2A3D;">{m}</p>', unsafe_allow_html=True)

            