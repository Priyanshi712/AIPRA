import streamlit as st
import time
from datetime import datetime
from agent import run_research_agent
from Voice_Input import get_voice_query
from Image_input import get_image_query


# ============================================================
# HTML RENDERER
# ============================================================
# Use Streamlit's native HTML renderer when available. This prevents
# HTML from being displayed as literal text/code in newer Streamlit versions.
# The fallback keeps compatibility with older Streamlit releases.
def render_html(content, **kwargs):
    if hasattr(st, "html"):
        st.html(content)
    else:
        st.markdown(content, unsafe_allow_html=True)



# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AIPRA",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SESSION STATE
# ============================================================

if "research_history" not in st.session_state:
    st.session_state.research_history = []

if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0

if "milestones" not in st.session_state:
    st.session_state.milestones = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "last_query" not in st.session_state:
    st.session_state.last_query = ""


# ============================================================
# HELPERS
# ============================================================

def get_level():
    q = st.session_state.total_queries

    if q == 0:
        return "Ready"
    elif q < 5:
        return "Scholar"
    elif q < 10:
        return "Researcher"
    elif q < 20:
        return "Expert"
    else:
        return "Master"


def format_time(seconds):
    if seconds < 60:
        return f"{int(seconds)}s"
    return f"{seconds / 60:.1f}m"


# ============================================================
# GLOBAL CSS
# ============================================================

render_html(
    """
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * {
        box-sizing: border-box;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 75% 10%,
                rgba(55, 100, 180, 0.10),
                transparent 30%
            ),
            radial-gradient(
                circle at 15% 80%,
                rgba(70, 100, 180, 0.06),
                transparent 28%
            ),
            #05070b !important;

        color: #f4f7fb;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    [data-testid="stToolbar"] {
        display: none;
    }

    .main {
        background: transparent !important;
    }

    .main .block-container {
        max-width: 1450px;
        padding: 1.5rem 3rem 5rem 3rem;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                rgba(7, 10, 16, 0.98),
                rgba(5, 7, 11, 0.98)
            ) !important;

        border-right: 1px solid rgba(255,255,255,0.06);
    }

    [data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }

    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 8px 28px 8px;
    }

    .sidebar-logo-icon {
        width: 38px;
        height: 38px;
        border-radius: 12px;

        display: flex;
        align-items: center;
        justify-content: center;

        background:
            linear-gradient(
                145deg,
                #477dff,
                #264b9b
            );

        box-shadow:
            0 0 30px rgba(71,125,255,0.28);

        font-size: 17px;
        font-weight: 700;
    }

    .sidebar-logo-text {
        font-size: 26px !important;
        font-weight: 800 !important;
        letter-spacing: -0.4px !important;
    }

    .sidebar-section {
        margin-top: 25px;
        margin-bottom: 10px;

        font-size: 9px;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;

        color: #929daf;
    }

    .sidebar-item {
        padding: 11px 12px;
        margin: 4px 0;

        border-radius: 12px;

        color: #8c96a5;
        font-size: 12px;

        transition: 0.2s ease;
    }

    .sidebar-item:hover {
        background: rgba(255,255,255,0.04);
        color: #f5f7fa;
    }

    .sidebar-item.active {
        background:
            linear-gradient(
                90deg,
                rgba(71,125,255,0.16),
                rgba(71,125,255,0.04)
            );

        color: #dfe8ff;

        border: 1px solid rgba(71,125,255,0.16);
    }

    .history-card {
        padding: 12px;

        margin: 7px 0;

        border-radius: 12px;

        background: rgba(255,255,255,0.025);

        border: 1px solid rgba(255,255,255,0.05);

        transition: 0.2s ease;
    }

    .history-card:hover {
        background: rgba(255,255,255,0.045);
        border-color: rgba(71,125,255,0.2);
    }

    .history-time {
        color: #4f8cff;
        font-size: 9px;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 5px;
    }

    .history-query {
        color: #b9c1cc;
        font-size: 11px;
        line-height: 1.45;
    }


    /* ========================================================
       TOP NAV
       ======================================================== */

    .topbar {
        height: 58px;

        display: flex;
        align-items: center;
        justify-content: space-between;

        margin-bottom: 28px;

        border-bottom: 1px solid rgba(255,255,255,0.05);
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .brand-symbol {
        width: 28px;
        height: 28px;

        border-radius: 9px;

        display: flex;
        align-items: center;
        justify-content: center;

        background: linear-gradient(
            145deg,
            #5b8dff,
            #284b9c
        );

        box-shadow: 0 0 20px rgba(91,141,255,0.25);

        font-size: 12px;
        font-weight: 700;
    }

    .brand-name {
        font-size: 26px !important;
        font-weight: 800 !important;
        letter-spacing: -0.3px !important;
    }

    .brand-status {
        margin-left: 8px;

        padding: 5px 9px;

        border-radius: 20px;

        background: rgba(53,211,151,0.08);
        border: 1px solid rgba(53,211,151,0.15);

        color: #54dca7;

        font-size: 9px;
    }

    .top-actions {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .top-pill {
        padding: 10px 16px;

        border-radius: 22px;

        background: rgba(255,255,255,0.035);

        border: 1px solid rgba(255,255,255,0.07);

        color: #a9b1bd;

        font-size: 11px;
    }


    /* ========================================================
       HERO
       ======================================================== */

    .hero {
        margin-bottom: 24px;
    }

    .hero-eyebrow {
        color: #628eff;

        font-size: 10px;
        font-weight: 600;

        letter-spacing: 2.5px;
        text-transform: uppercase;

        margin-bottom: 13px;
    }

    .hero-title {
        font-size: 38px;
        line-height: 1.1;

        font-weight: 500;

        letter-spacing: -2px;

        color: #f3f6fb;

        margin: 0;
    }

    .hero-title span {
        background:
            linear-gradient(
                100deg,
                #ffffff,
                #7ea6ff
            );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        color: #aeb9c8;

        font-size: 13px;

        margin-top: 13px;

        line-height: 1.7;
    }


    /* ========================================================
       WORKSPACE
       ======================================================== */

    .workspace {
        position: relative;

        padding: 25px;

        border-radius: 28px;

        background:
            linear-gradient(
                145deg,
                rgba(18,25,36,0.80),
                rgba(7,10,16,0.82)
            );

        border: 1px solid rgba(255,255,255,0.075);

        box-shadow:
            0 30px 100px rgba(0,0,0,0.35),
            inset 0 1px 0 rgba(255,255,255,0.035);

        backdrop-filter: blur(25px);
    }


    /* ========================================================
       AGENT CARD
       ======================================================== */

    .agent-card {
        min-height: 300px;

        padding: 28px;

        border-radius: 25px;

        background:
            radial-gradient(
                circle at 80% 20%,
                rgba(72,130,255,0.28),
                transparent 35%
            ),
            linear-gradient(
                145deg,
                #152b52,
                #101c36 55%,
                #0b1324
            );

        border: 1px solid rgba(109,157,255,0.25);

        box-shadow:
            0 25px 70px rgba(30,75,160,0.18),
            inset 0 1px 1px rgba(255,255,255,0.08);

        position: relative;
        overflow: hidden;
    }

    .agent-card::after {
        content: "";

        position: absolute;

        width: 180px;
        height: 180px;

        right: -60px;
        bottom: -80px;

        background: rgba(77,130,255,0.18);

        border-radius: 50%;

        filter: blur(45px);
    }

    .agent-header {
        display: flex;
        justify-content: space-between;
        align-items: center;

        margin-bottom: 30px;
    }

    .agent-icon {
        width: 43px;
        height: 43px;

        border-radius: 14px;

        display: flex;
        align-items: center;
        justify-content: center;

        background: rgba(255,255,255,0.09);

        border: 1px solid rgba(255,255,255,0.1);

        font-size: 18px;
    }

    .agent-status {
        display: flex;
        align-items: center;
        gap: 7px;

        padding: 8px 12px;

        border-radius: 20px;

        background: rgba(255,255,255,0.08);

        color: #dce6fa;

        font-size: 10px;
    }

    .green-dot {
        width: 7px;
        height: 7px;

        border-radius: 50%;

        background: #4de0a4;

        box-shadow: 0 0 12px rgba(77,224,164,0.8);
    }

    .agent-title {
        font-size: 25px;

        font-weight: 500;

        letter-spacing: -1px;

        color: #f5f8ff;

        margin-bottom: 6px;
    }

    .agent-subtitle {
        color: #a2b1c8;

        font-size: 12px;

        margin-bottom: 24px;
    }

    .agent-tasks {
        display: flex;
        flex-wrap: wrap;
        gap: 7px;
        padding-right: 5px;
    }

    .agent-task {
        display: inline-block;

        padding: 9px 13px;

        margin: 0;

        border-radius: 20px;

        background: rgba(255,255,255,0.07);

        border: 1px solid rgba(255,255,255,0.06);

        color: #bdcae1;

        font-size: 10px;
    }

    .agent-metrics {
        position: absolute;

        left: 28px;
        right: 28px;
        bottom: 25px;

        display: flex;
        gap: 30px;

        padding-top: 17px;

        border-top: 1px solid rgba(255,255,255,0.09);
    }

    .metric {
        flex: 1;
    }

    .metric-label {
        color: #95a2b5;

        font-size: 9px;

        text-transform: uppercase;

        letter-spacing: 1.2px;

        margin-bottom: 5px;
    }

    .metric-value {
        color: #edf3ff;

        font-size: 15px;

        font-weight: 500;
    }


    /* ========================================================
       QUERY CARD
       ======================================================== */

    .query-card {
        min-height: 220px;

        padding: 28px;

        border-radius: 25px;

        background:
            linear-gradient(
                145deg,
                rgba(22,28,38,0.94),
                rgba(10,14,21,0.96)
            );

        border: 1px solid rgba(255,255,255,0.07);

        box-shadow:
            0 25px 70px rgba(0,0,0,0.25),
            inset 0 1px 0 rgba(255,255,255,0.035);
    }

    .card-label {
        font-size: 9px;

        color: #a2adbd;

        text-transform: uppercase;

        letter-spacing: 2px;

        margin-bottom: 18px;
    }

    .query-title {
        color: #eef2f8;

        font-size: 18px;

        font-weight: 500;

        line-height: 1.45;

        margin-bottom: 0;
    }

    .query-hint {
        color: #9aa6b7;

        font-size: 11px;

        line-height: 1.6;

        padding-top: 20px;

        border-top: 1px solid rgba(255,255,255,0.05);
    }


    /* ========================================================
       INPUTS
       ======================================================== */

    .stTextInput > div > div > input {
        background: rgba(7,11,17,0.9) !important;

        border: 1px solid rgba(255,255,255,0.09) !important;

        border-radius: 16px !important;

        color: #edf2f8 !important;

        font-size: 14px !important;

        padding: 17px 18px !important;

        min-height: 58px !important;
        margin-top: 10px !important;

        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.025);

        transition: 0.25s ease !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: rgba(79,140,255,0.55) !important;

        box-shadow:
            0 0 0 3px rgba(79,140,255,0.08),
            0 0 35px rgba(79,140,255,0.08) !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #8e9bad !important;
    }


    /* ========================================================
       SELECTBOX
       ======================================================== */

    .stSelectbox > div > div {
        background: rgba(7,11,17,0.9) !important;

        border: 1px solid rgba(255,255,255,0.08) !important;

        border-radius: 14px !important;

        color: #cbd3df !important;
    }


    /* ========================================================
       SLIDER
       ======================================================== */

    .stSlider {
        padding: 0 5px;
    }

    .stSlider [data-baseweb="slider"] {
        margin-top: 5px;
    }


    /* ========================================================
       BUTTON
       ======================================================== */

    .stButton > button {
        min-height: 50px !important;

        border-radius: 15px !important;

        border: 1px solid rgba(117,159,255,0.25) !important;

        background:
            linear-gradient(
                135deg,
                #568cff,
                #315dc0
            ) !important;

        color: white !important;

        font-size: 11px !important;

        font-weight: 600 !important;

        letter-spacing: 1px !important;

        text-transform: uppercase !important;

        box-shadow:
            0 10px 35px rgba(55,105,220,0.25) !important;

        transition: 0.25s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px);

        box-shadow:
            0 15px 45px rgba(55,105,220,0.35) !important;

        border-color: rgba(130,170,255,0.45) !important;
    }


    /* ========================================================
       RESEARCH CONTROLS
       ======================================================== */

    .controls {
        margin-top: 26px;

        padding: 20px;

        border-radius: 20px;

        background: rgba(255,255,255,0.025);

        border: 1px solid rgba(255,255,255,0.055);
    }

    .control-label {
        font-size: 9px;

        color: #a2adbd;

        letter-spacing: 1.5px;

        text-transform: uppercase;

        margin-bottom: 8px;
    }


    /* ========================================================
       PROGRESS / THINKING
       ======================================================== */

    .thinking-card {
        margin-top: 25px;

        padding: 22px 25px;

        border-radius: 20px;

        background:
            linear-gradient(
                145deg,
                rgba(18,25,35,0.95),
                rgba(9,13,19,0.95)
            );

        border: 1px solid rgba(255,255,255,0.07);

        box-shadow:
            0 20px 60px rgba(0,0,0,0.3);
    }

    .thinking-header {
        display: flex;
        align-items: center;
        gap: 10px;

        color: #aeb9c9;

        font-size: 11px;

        margin-bottom: 15px;
    }

    .thinking-text {
        color: #a0adbd;

        font-size: 11px;
    }

    .progress-wrap {
        height: 4px;

        border-radius: 10px;

        background: rgba(255,255,255,0.06);

        overflow: hidden;

        margin-top: 18px;
    }

    .progress-fill {
        height: 100%;

        border-radius: 10px;

        background:
            linear-gradient(
                90deg,
                #467cff,
                #82aaff
            );

        box-shadow:
            0 0 15px rgba(70,124,255,0.6);

        transition: width 0.5s ease;
    }


    /* ========================================================
       RESULTS
       ======================================================== */

    .results-header {
        display: flex;

        align-items: center;

        justify-content: space-between;

        margin-top: 55px;

        margin-bottom: 20px;
    }

    .results-title {
        font-size: 22px;

        font-weight: 500;

        letter-spacing: -0.7px;

        color: #edf1f7;
    }

    .results-count {
        color: #9aa6b7;

        font-size: 10px;

        text-transform: uppercase;

        letter-spacing: 1.5px;
    }


    /* ========================================================
       SUMMARY
       ======================================================== */

    .summary-card {
        padding: 28px;

        border-radius: 23px;

        background:
            radial-gradient(
                circle at 100% 0%,
                rgba(73,124,255,0.13),
                transparent 35%
            ),
            linear-gradient(
                145deg,
                rgba(19,27,39,0.95),
                rgba(10,14,21,0.96)
            );

        border: 1px solid rgba(255,255,255,0.075);

        box-shadow:
            0 25px 70px rgba(0,0,0,0.28);

        margin-bottom: 25px;
    }

    .summary-query {
        color: #5f8fff;

        font-size: 9px;

        letter-spacing: 1.8px;

        text-transform: uppercase;

        margin-bottom: 13px;
    }

    .summary-text {
        color: #cbd2dc;

        font-size: 14px;

        line-height: 1.85;
    }


    /* ========================================================
       FINDINGS
       ======================================================== */

    .finding-grid {
        display: grid;

        grid-template-columns: repeat(2, 1fr);

        gap: 15px;

        margin-bottom: 30px;
    }

    .finding {
        position: relative;

        min-height: 150px;

        padding: 22px;

        border-radius: 20px;

        background:
            linear-gradient(
                145deg,
                rgba(19,26,37,0.9),
                rgba(9,13,19,0.95)
            );

        border: 1px solid rgba(255,255,255,0.065);

        box-shadow:
            0 15px 45px rgba(0,0,0,0.22);

        transition: 0.25s ease;
    }

    .finding:hover {
        transform: translateY(-3px);

        border-color: rgba(76,132,255,0.25);

        box-shadow:
            0 20px 55px rgba(0,0,0,0.35),
            0 0 30px rgba(76,132,255,0.06);
    }

    .finding-number {
        display: inline-flex;

        align-items: center;
        justify-content: center;

        width: 30px;
        height: 30px;

        border-radius: 10px;

        background: rgba(75,130,255,0.1);

        border: 1px solid rgba(75,130,255,0.15);

        color: #73a0ff;

        font-size: 10px;

        font-weight: 600;

        margin-bottom: 18px;
    }

    .finding-text {
        color: #b9c2cf;

        font-size: 12px;

        line-height: 1.7;
    }


    /* ========================================================
       SOURCES
       ======================================================== */

    .source-card {
        display: block;

        padding: 20px 22px;

        margin: 10px 0;

        border-radius: 17px;

        background:
            rgba(13,18,26,0.85);

        border: 1px solid rgba(255,255,255,0.06);

        text-decoration: none !important;

        transition: 0.25s ease;
    }

    .source-card:hover {
        transform: translateX(4px);

        border-color: rgba(72,130,255,0.28);

        background: rgba(18,25,36,0.95);

        box-shadow:
            0 12px 35px rgba(0,0,0,0.25);
    }

    .source-top {
        display: flex;

        justify-content: space-between;

        gap: 20px;
    }

    .source-number {
        color: #5e8fff;

        font-size: 9px;

        font-weight: 600;

        letter-spacing: 1.5px;

        text-transform: uppercase;
    }

    .source-title {
        color: #dce2eb;

        font-size: 13px;

        font-weight: 500;

        margin: 6px 0;
    }

    .source-url {
        color: #8b97a8;

        font-size: 10px;

        word-break: break-all;
    }

    .source-snippet {
        color: #818b9a;

        font-size: 11px;

        line-height: 1.6;

        margin-top: 12px;

        padding-top: 12px;

        border-top: 1px solid rgba(255,255,255,0.045);
    }


    /* ========================================================
       EMPTY STATE
       ======================================================== */

    .empty-state {
        padding: 80px 30px;

        text-align: center;

        border-radius: 25px;

        background:
            radial-gradient(
                circle at 50% 0%,
                rgba(73,124,255,0.08),
                transparent 40%
            ),
            rgba(10,14,21,0.75);

        border: 1px solid rgba(255,255,255,0.06);
    }

    .empty-icon {
        width: 55px;
        height: 55px;

        margin: 0 auto 20px;

        border-radius: 17px;

        display: flex;
        align-items: center;
        justify-content: center;

        background: rgba(75,130,255,0.08);

        border: 1px solid rgba(75,130,255,0.13);

        color: #6190ff;

        font-size: 20px;
    }

    .empty-title {
        color: #d8dee8;

        font-size: 16px;

        margin-bottom: 8px;
    }

    .empty-subtitle {
        color: #596372;

        font-size: 11px;
    }


    /* ========================================================
       METRIC ROW
       ======================================================== */

    .stats-row {
        display: grid;

        grid-template-columns: repeat(4, 1fr);

        gap: 12px;

        margin-top: 20px;
    }

    .stat-card {
        padding: 18px;

        border-radius: 17px;

        background: rgba(255,255,255,0.025);

        border: 1px solid rgba(255,255,255,0.055);
    }

    .stat-value {
        color: #e9eef7;

        font-size: 20px;

        font-weight: 500;

        margin-bottom: 5px;
    }

    .stat-label {
        color: #9aa6b7;

        font-size: 8px;

        letter-spacing: 1.5px;

        text-transform: uppercase;
    }


    /* ========================================================
       STREAMLIT CLEANUP
       ======================================================== */

    .stMarkdown {
        color: inherit;
    }

    div[data-testid="stVerticalBlock"] {
        gap: 0.8rem;
    }

    footer {
        visibility: hidden;
    }

    #MainMenu {
        visibility: hidden;
    }


    /* ========================================================
       RESPONSIVE
       ======================================================== */

    @media (max-width: 900px) {

        .main .block-container {
            padding: 1rem 1.2rem 4rem 1.2rem;
        }

        .hero-title {
            font-size: 32px;
        }

        .finding-grid {
            grid-template-columns: 1fr;
        }

        .stats-row {
            grid-template-columns: repeat(2, 1fr);
        }
    }


    /* ========================================================
       AIPRA UX POLISH
       ======================================================== */

    .query-card-open {
        padding-bottom: 16px;
        border-bottom-left-radius: 10px;
        border-bottom-right-radius: 10px;
        border-bottom-color: rgba(91,141,255,0.16);
    }

    .query-topline {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
    }

    .query-badge {
        color: #b5caff;
        background: rgba(79,140,255,0.10);
        border: 1px solid rgba(79,140,255,0.20);
        border-radius: 999px;
        padding: 5px 9px;
        font-size: 8px;
        font-weight: 700;
        letter-spacing: 1.2px;
        white-space: nowrap;
    }

    .controls-attached {
        margin-top: -1px;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        border-bottom: 0;
        background: rgba(17,23,33,0.92);
        padding: 17px 20px 7px;
    }

    .query-footer-note {
        margin-top: 12px;
        color: #8794a6;
        font-size: 10px;
        line-height: 1.55;
        text-align: right;
    }

    .stSelectbox label,
    .stSlider label {
        color: #aeb9c8 !important;
        font-size: 10px !important;
        font-weight: 600 !important;
        letter-spacing: .7px !important;
        text-transform: uppercase !important;
        margin-bottom: 6px !important;
    }

    .stTextInput {
        margin-top: -8px;
        margin-bottom: 0;
    }

    .stTextInput > div > div > input {
        min-height: 62px !important;
        border-radius: 14px !important;
        border-color: rgba(121,151,201,0.22) !important;
        background: rgba(5,9,15,0.96) !important;
    }

    .stTextInput > div > div > input:hover {
        border-color: rgba(121,151,201,0.38) !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #8e9bad !important;
        opacity: 1 !important;
    }

    /* Brand-aligned neutral blue slider instead of red/coral. */
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background: #79a2ff !important;
        border-color: #79a2ff !important;
        box-shadow: 0 0 0 3px rgba(121,162,255,0.12) !important;
    }

    .stSlider [data-baseweb="slider"] > div > div {
        background: linear-gradient(90deg, #477dff, #82aaff) !important;
    }

    .stSlider [data-baseweb="slider"] > div > div > div {
        background: #27354f !important;
    }

    .stSelectbox [data-baseweb="select"] > div {
        min-height: 44px !important;
    }

    .stButton > button {
        min-height: 48px !important;
        border-radius: 13px !important;
    }

    .stButton > button:focus-visible,
    .stSelectbox [data-baseweb="select"]:focus-within,
    .stTextInput input:focus-visible {
        outline: 2px solid rgba(121,162,255,0.7) !important;
        outline-offset: 2px;
    }

    .agent-card {
        min-height: 370px;
    }

    .agent-subtitle {
        max-width: 290px;
    }

    .agent-tasks {
        max-width: 330px;
    }

    .workspace {
        box-shadow:
            0 35px 110px rgba(0,0,0,0.42),
            inset 0 1px 0 rgba(255,255,255,0.045);
    }

    .hero-subtitle {
        max-width: 690px;
    }

    @media (max-width: 900px) {
        .agent-card {
            min-height: 310px;
        }

        .query-footer-note {
            text-align: left;
        }

        .query-topline {
            align-items: flex-start;
        }
    }

    /* Force AIPRA wordmark size — overrides any earlier rule */
    .brand-name, .sidebar-logo-text {
        font-size: 48px !important;
        font-weight: 800 !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    if st.session_state.research_history:
        st.markdown("### 📈 Quick Stats")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Queries", st.session_state.total_queries)
        with col2:
            st.metric("Level", get_level())
        
        total_findings = sum(r.get('findings', 0) for r in st.session_state.research_history)
        st.metric("Total Findings", total_findings)
        
        if st.button("🗑️ Clear History"):
            st.session_state.research_history = []
            st.session_state.total_queries = 0
            st.rerun()
        
        st.markdown("---")

    render_html(
        """
        <div class="sidebar-logo">
            <div class="sidebar-logo-icon">◆</div>
            <div class="sidebar-logo-text">AIPRA</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    render_html(
        '<div class="sidebar-section">Workspace</div>',
        unsafe_allow_html=True
    )

    render_html(
        '<div class="sidebar-item active">◈ &nbsp; Research</div>',
        unsafe_allow_html=True
    )

    render_html(
        '<div class="sidebar-item">⌕ &nbsp; Explore</div>',
        unsafe_allow_html=True
    )

    render_html(
        '<div class="sidebar-item">◇ &nbsp; Sources</div>',
        unsafe_allow_html=True
    )

    render_html(
        '<div class="sidebar-item">▥ &nbsp; Analytics</div>',
        unsafe_allow_html=True
    )

    render_html(
        '<div class="sidebar-section">Recent Research</div>',
        unsafe_allow_html=True
    )

    if st.session_state.research_history:

        for entry in reversed(
            st.session_state.research_history[-6:]
        ):

            render_html(
                f"""
                <div class="history-card">
                    <div class="history-time">
                        {entry['timestamp']}
                    </div>

                    <div class="history-query">
                        {entry['query'][:65]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        render_html(
            """
            <div style="
                color:#8995a6;
                font-size:11px;
                padding:10px 5px;
            ">
                No research yet.
            </div>
            """,
            unsafe_allow_html=True
        )

    render_html(
        '<div class="sidebar-section">Progress</div>',
        unsafe_allow_html=True
    )

    render_html(
        f"""
        <div class="history-card">
            <div class="history-time">Research Level</div>
            <div style="
                color:#d9e2f1;
                font-size:13px;
                margin-top:5px;
            ">
                {get_level()}
            </div>

            <div style="
                color:#5f6b7a;
                font-size:10px;
                margin-top:7px;
            ">
                {st.session_state.total_queries} total queries
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# TOP BAR
# ============================================================

render_html(
    """
    <div class="topbar">

        <div class="brand">

            <div class="brand-symbol">◆</div>

            <div class="brand-name">
                AIPRA
            </div>

            <div class="brand-status">
                ● AI ONLINE
            </div>

        </div>

        <div class="top-actions">

            <div class="top-pill">
                v2.0 · Research workspace
            </div>

        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HERO
# ============================================================

render_html(
    """
    <div class="hero">

        <div class="hero-eyebrow">
            Autonomous Intelligence Platform
        </div>

        <div class="hero-title">
            Research, <span>without the noise.</span>
        </div>

        <div class="hero-subtitle">
            A PERSONAL SEARCH ENGINE FOR DEEP, EVIDENCE-BASED INSIGHTS.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# MAIN WORKSPACE
# ============================================================

# NOTE:
# Streamlit widgets are rendered as separate DOM elements. Do not open an
# HTML <div> in one st.markdown() call and close it after st.columns() or
# st.text_input(). Each HTML block below is intentionally self-contained.

left, right = st.columns(
    [1, 1],
    gap="large"
)


# ============================================================
# AGENT CARD
# ============================================================

with left:
    render_html(
        f"""
        <div class="agent-card">

            <div class="agent-header">

                <div class="agent-icon">
                    ◇
                </div>

                <div class="agent-status">
                    <span class="green-dot"></span>
                    Ready
                </div>

            </div>

            <div class="agent-title">
                AIPRA Engine
            </div>

            <div class="agent-subtitle">
                Autonomous Research &amp; Intelligence
            </div>

            <div class="agent-tasks">
                <span class="agent-task">Planning</span>
                <span class="agent-task">Web Search</span>
                <span class="agent-task">Analysis</span>
                <span class="agent-task">Synthesis</span>
            </div>

            <div class="agent-metrics">

                <div class="metric">
                    <div class="metric-label">Queries</div>
                    <div class="metric-value">{st.session_state.total_queries}</div>
                </div>

                <div class="metric">
                    <div class="metric-label">Level</div>
                    <div class="metric-value">{get_level()}</div>
                </div>

                <div class="metric">
                    <div class="metric-label">Milestones</div>
                    <div class="metric-value">{len(st.session_state.milestones)}</div>
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# QUERY AREA
# ============================================================

with right:
    render_html(
        """
        <div class="query-card query-card-open">
            <div class="query-topline">
                <div class="card-label">NEW RESEARCH</div>
                <div class="query-badge">READY TO ANALYZE</div>
            </div>

            <div class="query-title">
                What would you like to understand?
            </div>

            <div class="query-hint">
                Define the question, choose the research depth, and set the evidence target.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    input_mode = st.radio(
        "Input method",
        ["✍️ Type", "🎤 Voice", "📷 Image"],
        horizontal=True,
        label_visibility="collapsed",
        key="aipra_input_mode"
    )

    query = ""

    if input_mode == "✍️ Type":

        query = st.text_input(
            "Research question",
            placeholder="e.g. What are the most promising approaches to…",
            label_visibility="collapsed",
            key="research_question"
        )

    elif input_mode == "🎤 Voice":

        voice_text = get_voice_query()

        query = st.text_input(
            "Research question",
            value=voice_text or "",
            placeholder="Your transcribed question will appear here — feel free to edit.",
            label_visibility="collapsed",
            key="research_question_voice"
        )

    else:  # 📷 Image

        image_text = get_image_query()

        query = st.text_input(
            "Research question",
            value=image_text or "",
            placeholder="Text extracted from your image will appear here — feel free to edit.",
            label_visibility="collapsed",
            key="research_question_image"
        )

    render_html(
        """
        <div class="controls controls-attached">
            <div class="control-label">RESEARCH CONFIGURATION</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns([1.15, 1.15, 0.8], gap="medium")

    with c1:
        depth = st.selectbox(
            "Depth",
            ["Quick", "Standard", "Deep"],
            index=1,
            label_visibility="visible"
        )

    with c2:
        num_sources = st.slider(
            "Evidence sources",
            min_value=3,
            max_value=10,
            value=6,
            label_visibility="visible"
        )

    with c3:
        search_button = st.button(
            "ANALYZE  →",
            use_container_width=True
        )

    render_html(
        """
        <div class="query-footer-note">
            AIPRA will plan the research, gather evidence, and synthesize the strongest findings.
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# EMPTY STATE
# ============================================================

if not query and st.session_state.last_result is None:

    render_html(
        """
        <div class="empty-state">

            <div class="empty-icon">
                ◇
            </div>

            <div class="empty-title">
                Your research workspace is ready
            </div>

            <div class="empty-subtitle">
                Enter a research question above to activate the agent.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# RESEARCH EXECUTION
# ============================================================

if search_button:

    if not query.strip():

        st.warning("Please enter a research question first.")

    else:

        st.session_state.total_queries += 1
        st.session_state.last_query = query

        progress_placeholder = st.empty()

        start_time = time.time()

        stages = [
            (
                "Planning",
                "Building research strategy",
                25
            ),
            (
                "Gathering",
                "Collecting relevant sources",
                55
            ),
            (
                "Analyzing",
                "Synthesizing evidence",
                80
            )
        ]

        for stage, description, progress in stages:

            render_html(
                f"""
                <div class="thinking-card">

                    <div class="thinking-header">

                        <span class="green-dot"></span>

                        <strong>
                            AIPRA Engine
                        </strong>

                        <span style="color:#9aa6b7;">
                            {stage}
                        </span>

                    </div>

                    <div class="thinking-text">
                        {description}...
                    </div>

                    <div class="progress-wrap">

                        <div
                            class="progress-fill"
                            style="width:{progress}%"
                        ></div>

                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

            time.sleep(0.35)

        try:

            result = run_research_agent(
                query,
                depth=depth,
                num_sources=num_sources
            )

        except Exception as e:

            progress_placeholder.empty()

            st.error(f"Research failed: {e}")

            st.stop()

        elapsed = time.time() - start_time

        render_html(
            f"""
            <div class="thinking-card">

                <div class="thinking-header">

                    <span class="green-dot"></span>

                    <strong>
                        Research complete
                    </strong>

                    <span style="color:#9aa6b7;">
                        {format_time(elapsed)}
                    </span>

                </div>

                <div class="thinking-text">
                    Evidence synthesized successfully.
                </div>

                <div class="progress-wrap">

                    <div
                        class="progress-fill"
                        style="width:100%"
                    ></div>

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        time.sleep(0.4)

        progress_placeholder.empty()

        st.session_state.last_result = result

        findings = result.get("findings", [])
        sources = result.get("sources", [])

        # ----------------------------------------------------
        # MILESTONES
        # ----------------------------------------------------

        milestone_labels = {
            1: "First research",
            5: "Five queries",
            10: "Ten queries",
            20: "Twenty queries"
        }

        if st.session_state.total_queries in milestone_labels:

            label = milestone_labels[
                st.session_state.total_queries
            ]

            if label not in st.session_state.milestones:

                st.session_state.milestones.append(label)

        # ----------------------------------------------------
        # HISTORY
        # ----------------------------------------------------

        st.session_state.research_history.append(
            {
                "query": query,
                "timestamp": datetime.now().strftime(
                    "%d %b, %H:%M"
                ),
                "findings": len(findings)
            }
        )


# ============================================================
# DISPLAY RESULTS
# ============================================================

if st.session_state.last_result is not None:

    result = st.session_state.last_result

    findings = result.get("findings", [])
    sources = result.get("sources", [])

    summary = result.get(
        "summary",
        "No summary was generated."
    )

    # --------------------------------------------------------
    # RESULT HEADER
    # --------------------------------------------------------

    render_html(
        f"""
        <div class="results-header">

            <div class="results-title">
                Research Output
            </div>

            <div class="results-count">
                {len(findings)} findings ·
                {len(sources)} sources
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    render_html(
        f"""
        <div class="summary-card">

            <div class="summary-query">
                Research Question
            </div>

            <div style="
                color:#e8edf5;
                font-size:15px;
                margin-bottom:18px;
                line-height:1.5;
            ">
                {st.session_state.last_query}
            </div>

            <div class="summary-query">
                AI Synthesis
            </div>

            <div class="summary-text">
                {summary}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    render_html(
        f"""
        <div class="stats-row">

            <div class="stat-card">
                <div class="stat-value">
                    {len(findings)}
                </div>

                <div class="stat-label">
                    Key Findings
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-value">
                    {len(sources)}
                </div>

                <div class="stat-label">
                    Sources
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-value">
                    {depth}
                </div>

                <div class="stat-label">
                    Research Depth
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-value">
                    {num_sources}
                </div>

                <div class="stat-label">
                    Source Target
                </div>
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # FINDINGS
    # --------------------------------------------------------

    if findings:

        render_html(
            """
            <div class="results-header">

                <div class="results-title">
                    Key Findings
                </div>

                <div class="results-count">
                    Synthesized Insights
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        render_html(
            '<div class="finding-grid">',
            unsafe_allow_html=True
        )

        for i, finding in enumerate(findings, 1):

            render_html(
                f"""
                <div class="finding">

                    <div class="finding-number">
                        {i:02d}
                    </div>

                    <div class="finding-text">
                        {finding}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

        render_html(
            "</div>",
            unsafe_allow_html=True
        )

        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📋 Copy Results", use_container_width=True):
                results_text = f"Query: {query}\n\n"
                results_text += f"Summary: {result.get('summary', '')}\n\n"
                results_text += "Key Findings:\n"
                for i, finding in enumerate(findings, 1):
                    results_text += f"{i}. {finding}\n"
                st.code(results_text)
                st.success("✅ Copy the text above!")
        
        with col2:
            if st.button("📊 Export as Text"):
                st.info("Export feature coming soon!")
        
        with col3:
            if st.button("⭐ Save to Favorites"):
                st.success("Saved!")


    # --------------------------------------------------------
    # SOURCES
    # --------------------------------------------------------

    if sources:

        render_html(
            """
            <div class="results-header">

                <div class="results-title">
                    Evidence
                </div>

                <div class="results-count">
                    Research Sources
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        for idx, source in enumerate(
            sources[:10],
            1
        ):

            url = source.get(
                "url",
                "#"
            )

            title = source.get(
                "title",
                "Untitled Source"
            )

            snippet = source.get(
                "snippet",
                ""
            )

            render_html(
                f"""
                <a
                    href="{url}"
                    target="_blank"
                    class="source-card"
                >

                    <div class="source-top">

                        <div>

                            <div class="source-number">
                                SOURCE {idx:02d}
                            </div>

                            <div class="source-title">
                                {title}
                            </div>

                            <div class="source-url">
                                {url}
                            </div>

                        </div>

                        <div style="
                            color:#8c99aa;
                            font-size:16px;
                        ">
                            ↗
                        </div>

                    </div>

                    <div class="source-snippet">
                        {snippet[:220]}
                    </div>

                </a>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# FOOTER
# ============================================================

render_html(
    """
    <div style="
        text-align:center;
        margin-top:48px;
        padding-top:20px;
        border-top:1px solid rgba(255,255,255,0.045);
        color:#778396;
        font-size:9px;
        letter-spacing:1.5px;
        text-transform:uppercase;
    ">
        AIPRA · Autonomous Intelligence Platform · Research powered by AI
    </div>
    """,
    unsafe_allow_html=True
)