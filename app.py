import streamlit as st
import json
import time
from datetime import datetime
from agent import run_research_agent
import random

# ============================================================================
# PAGE CONFIGURATION & STYLING
# ============================================================================

st.set_page_config(
    page_title="AIPRA - Research Intelligence",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful gradient theme
st.markdown("""
    <style>
        /* Gradient Background */
        .stApp {
            background: linear-gradient(135deg, #0f1419 0%, #1a1f3a 50%, #2d1b4e 100%);
            color: #e8e8f0;
        }
        
        /* Remove default streamlit styling */
        [data-testid="stHeader"] {
            background: transparent;
            box-shadow: none;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        /* Typography - Headers */
        h1, h2 {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #a8e6ff 0%, #d4a5ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        
        h3 {
            color: #c8b4ff;
            font-weight: 600;
            letter-spacing: -0.3px;
        }
        
        /* Main container styling */
        .main-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        /* Research card styling */
        .research-card {
            background: linear-gradient(135deg, rgba(168, 230, 255, 0.05) 0%, rgba(212, 165, 255, 0.05) 100%);
            border: 1px solid rgba(168, 230, 255, 0.2);
            border-radius: 16px;
            padding: 24px;
            margin: 16px 0;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        }
        
        .research-card:hover {
            background: linear-gradient(135deg, rgba(168, 230, 255, 0.1) 0%, rgba(212, 165, 255, 0.1) 100%);
            border-color: rgba(168, 230, 255, 0.4);
            transform: translateY(-2px);
            box-shadow: 0 12px 48px rgba(168, 230, 255, 0.15);
        }
        
        /* Source cards */
        .source-card {
            background: rgba(45, 27, 78, 0.4);
            border-left: 4px solid #a8e6ff;
            padding: 16px;
            margin: 12px 0;
            border-radius: 8px;
            transition: all 0.2s ease;
        }
        
        .source-card:hover {
            background: rgba(45, 27, 78, 0.6);
            border-left-color: #d4a5ff;
            transform: translateX(4px);
        }
        
        /* Progress indicators */
        .progress-pill {
            display: inline-block;
            background: linear-gradient(135deg, #a8e6ff 0%, #d4a5ff 100%);
            color: #0f1419;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin: 4px 4px 4px 0;
            letter-spacing: 0.5px;
        }
        
        /* Achievement badges */
        .achievement-badge {
            display: inline-block;
            background: linear-gradient(135deg, #ffa500 0%, #ff6b6b 100%);
            color: white;
            padding: 10px 16px;
            border-radius: 12px;
            margin: 8px;
            font-weight: 600;
            text-align: center;
            box-shadow: 0 4px 16px rgba(255, 107, 107, 0.3);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        /* Input styling */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(168, 230, 255, 0.3) !important;
            border-radius: 8px !important;
            color: #e8e8f0 !important;
            font-size: 16px !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: rgba(200, 180, 255, 0.5);
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #a8e6ff 0%, #d4a5ff 100%);
            color: #0f1419;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 700;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 16px rgba(168, 230, 255, 0.3);
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(168, 230, 255, 0.4);
        }
        
        /* Spinner animation */
        .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(168, 230, 255, 0.3);
            border-top-color: #a8e6ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Stats card */
        .stats-card {
            background: rgba(45, 27, 78, 0.4);
            border: 1px solid rgba(168, 230, 255, 0.2);
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            margin: 8px;
        }
        
        .stats-number {
            font-size: 28px;
            font-weight: 700;
            background: linear-gradient(135deg, #a8e6ff 0%, #d4a5ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .stats-label {
            color: #999;
            font-size: 12px;
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Divider */
        .divider {
            height: 2px;
            background: linear-gradient(90deg, transparent, #a8e6ff, transparent);
            margin: 24px 0;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE & UTILITIES
# ============================================================================

if "research_history" not in st.session_state:
    st.session_state.research_history = []

if "achievements" not in st.session_state:
    st.session_state.achievements = []

if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0

def add_achievement(achievement_name, emoji):
    """Add achievement badge"""
    if achievement_name not in st.session_state.achievements:
        st.session_state.achievements.append(achievement_name)

def get_research_level():
    """Calculate user level based on research count"""
    queries = st.session_state.total_queries
    if queries == 0:
        return "Novice", "📚"
    elif queries < 5:
        return "Scholar", "🎓"
    elif queries < 10:
        return "Researcher", "🔬"
    elif queries < 20:
        return "Expert", "⭐"
    else:
        return "Master Researcher", "🏆"

def format_time_taken(seconds):
    """Format research time"""
    if seconds < 60:
        return f"{int(seconds)}s"
    else:
        minutes = seconds / 60
        return f"{minutes:.1f}m"

# ============================================================================
# HEADER & HERO SECTION
# ============================================================================

# Create header with gradient
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
        <h1 style='text-align: center; margin-bottom: 0.5rem;'>
            🔬 AIPRA
        </h1>
        <p style='text-align: center; color: #c8b4ff; font-size: 14px; letter-spacing: 1px;'>
            AI-Powered Research Intelligence Platform
        </p>
    """, unsafe_allow_html=True)

# User stats in header
level_name, level_emoji = get_research_level()
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class='stats-card'>
            <div class='stats-number'>{st.session_state.total_queries}</div>
            <div class='stats-label'>Queries</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class='stats-card'>
            <div class='stats-number'>{level_emoji}</div>
            <div class='stats-label'>{level_name}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class='stats-card'>
            <div class='stats-number'>{len(st.session_state.achievements)}</div>
            <div class='stats-label'>Achievements</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class='stats-card'>
            <div class='stats-number'>{'⭐' * min(5, len(st.session_state.achievements))}</div>
            <div class='stats-label'>Stars Earned</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ============================================================================
# SEARCH INTERFACE
# ============================================================================

st.markdown("""
    <h2 style='text-align: center; margin-bottom: 1.5rem;'>
        What would you like to research today?
    </h2>
""", unsafe_allow_html=True)

# Research query input
query = st.text_input(
    "Enter your research question",
    placeholder="E.g., 'What are the latest developments in quantum computing?'",
    label_visibility="collapsed"
)

# Research options
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    depth = st.selectbox(
        "Research Depth",
        ["Quick Overview", "Standard", "Deep Analysis"],
        index=1,
        label_visibility="collapsed"
    )

with col2:
    num_sources = st.slider(
        "Number of Sources",
        min_value=3,
        max_value=10,
        value=6,
        label_visibility="collapsed"
    )

with col3:
    search_button = st.button("🚀 Launch Research", use_container_width=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ============================================================================
# RESEARCH EXECUTION
# ============================================================================

if search_button and query:
    st.session_state.total_queries += 1
    
    # Create a progress container with visual feedback
    progress_container = st.container()
    results_container = st.container()
    
    with progress_container:
        st.markdown("<h3>🔍 Research in Progress...</h3>", unsafe_allow_html=True)
        
        # Progress indicators
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
                <div class='research-card'>
                    <div style='color: #a8e6ff; font-weight: 600; margin-bottom: 8px;'>
                        📋 Planning
                    </div>
                    <div style='font-size: 12px; color: #999;'>Generating search strategy</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class='research-card'>
                    <div style='color: #d4a5ff; font-weight: 600; margin-bottom: 8px;'>
                        🌐 Gathering
                    </div>
                    <div style='font-size: 12px; color: #999;'>Collecting sources</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
                <div class='research-card'>
                    <div style='color: #c8b4ff; font-weight: 600; margin-bottom: 8px;'>
                        ✨ Analyzing
                    </div>
                    <div style='font-size: 12px; color: #999;'>Synthesizing insights</div>
                </div>
            """, unsafe_allow_html=True)
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Run the research agent
        start_time = time.time()
        
        with st.spinner():
            try:
                # Simulate progress updates
                for i in range(3):
                    progress_bar.progress((i + 1) * 30)
                    if i == 0:
                        status_text.info("📋 Creating research plan...")
                    elif i == 1:
                        status_text.info("🌐 Searching for relevant sources...")
                    else:
                        status_text.info("✨ Synthesizing findings...")
                    time.sleep(0.5)
                
                # Execute research
                research_result = run_research_agent(query)
                
                elapsed_time = time.time() - start_time
                progress_bar.progress(100)
                status_text.success(f"✅ Research complete in {format_time_taken(elapsed_time)}")
                time.sleep(0.5)
                
            except Exception as e:
                st.error(f"❌ Research failed: {str(e)}")
                st.stop()
    
    # Clear progress section
    progress_container.empty()
    
    # ========================================================================
    # DISPLAY RESULTS
    # ========================================================================
    
    with results_container:
        st.markdown(f"""
            <div class='research-card'>
                <h3>📊 Research Summary</h3>
                <p style='color: #999; font-size: 12px; margin-bottom: 1rem;'>
                    Query: <em>{query}</em>
                </p>
                <p style='line-height: 1.6; color: #e8e8f0;'>
                    {research_result.get('summary', 'No summary available')}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Key findings section
        st.markdown("<h2 style='margin-top: 2rem; margin-bottom: 1.5rem;'>🎯 Key Findings</h2>", unsafe_allow_html=True)
        
        findings = research_result.get('findings', [])
        if findings:
            for i, finding in enumerate(findings, 1):
                st.markdown(f"""
                    <div class='research-card'>
                        <div style='display: flex; align-items: center; gap: 12px;'>
                            <div style='
                                width: 32px;
                                height: 32px;
                                border-radius: 50%;
                                background: linear-gradient(135deg, #a8e6ff 0%, #d4a5ff 100%);
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                color: #0f1419;
                                font-weight: 700;
                                flex-shrink: 0;
                            '>{i}</div>
                            <div>
                                <p style='color: #c8b4ff; font-weight: 600; margin: 0;'>Finding {i}</p>
                                <p style='color: #e8e8f0; margin: 8px 0 0 0; line-height: 1.6;'>
                                    {finding}
                                </p>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        # Sources section
        st.markdown("<h2 style='margin-top: 2rem; margin-bottom: 1.5rem;'>📚 Sources</h2>", unsafe_allow_html=True)
        
        sources = research_result.get('sources', [])
        if sources:
            cols = st.columns(2)
            for idx, source in enumerate(sources[:6]):
                with cols[idx % 2]:
                    st.markdown(f"""
                        <a href="{source.get('url', '#')}" target="_blank" style='text-decoration: none;'>
                            <div class='source-card'>
                                <div style='color: #a8e6ff; font-weight: 600; margin-bottom: 8px;'>
                                    📖 Source {idx + 1}
                                </div>
                                <div style='color: #e8e8f0; font-weight: 500; margin-bottom: 6px;'>
                                    {source.get('title', 'Untitled')}
                                </div>
                                <div style='color: #999; font-size: 12px; margin-bottom: 8px;'>
                                    {source.get('url', 'No URL')}
                                </div>
                                <div style='color: #c8b4ff; font-size: 13px; line-height: 1.5;'>
                                    {source.get('snippet', 'No preview available')[:150]}...
                                </div>
                            </div>
                        </a>
                    """, unsafe_allow_html=True)
        
        # Achievements section
        st.markdown(f"<h2 style='margin-top: 2rem; margin-bottom: 1.5rem;'>🏆 Achievements Unlocked</h2>", unsafe_allow_html=True)
        
        # Check for achievement milestones
        if st.session_state.total_queries == 1:
            add_achievement("🚀 First Research", "First Query")
        elif st.session_state.total_queries == 5:
            add_achievement("🎓 Scholar", "5 Queries")
        elif st.session_state.total_queries == 10:
            add_achievement("🔬 Researcher", "10 Queries")
        
        if st.session_state.achievements:
            achievement_cols = st.columns(len(st.session_state.achievements[:4]))
            for idx, achievement in enumerate(st.session_state.achievements[:4]):
                with achievement_cols[idx]:
                    st.markdown(f"""
                        <div class='achievement-badge'>
                            {achievement}
                        </div>
                    """, unsafe_allow_html=True)
        
        # Add to history
        research_entry = {
            "query": query,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "findings_count": len(findings)
        }
        st.session_state.research_history.append(research_entry)

# ============================================================================
# RESEARCH HISTORY SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("""
        <h3 style='margin-bottom: 1.5rem;'>📜 Research History</h3>
    """, unsafe_allow_html=True)
    
    if st.session_state.research_history:
        for entry in reversed(st.session_state.research_history[-5:]):
            st.markdown(f"""
                <div class='research-card' style='margin-bottom: 12px;'>
                    <div style='color: #a8e6ff; font-weight: 600; font-size: 13px; margin-bottom: 6px;'>
                        {entry['timestamp']}
                    </div>
                    <div style='color: #e8e8f0; font-size: 13px; line-height: 1.4;'>
                        {entry['query'][:50]}...
                    </div>
                    <span class='progress-pill'>
                        {entry['findings_count']} findings
                    </span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No research history yet. Start exploring!")
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Quick tips
    
    st.markdown("""
        <h4 style='color: #c8b4ff; margin-top: 1.5rem;'>💡 Quick Tips</h4>
        <div style='font-size: 13px; color: #999; line-height: 1.6;'>
            • Be specific in your questions<br>
            • Use keywords naturally<br>
            • Deep analysis takes more time<br>
            • Check multiple sources<br>
            • Unlock more achievements!
        </div>
    """, unsafe_allow_html=True)