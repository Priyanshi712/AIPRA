
import streamlit as st

from agent import research, format_sources_for_display


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AIPRA - AI Personal Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
    .main-header {
        text-align: center;
        color: #1f77b4;
    }

    .source-card {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
        background-color: #f9f9f9;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown("# 🔬 AIPRA - AI Personal Research Agent")

st.markdown(
    """
    **AIPRA** searches, analyzes, and synthesizes information from
    multiple web sources.

    This agent creates a research plan, performs web searches,
    and generates a citation-backed report.
    """
)

st.divider()


# ============================================================
# SIDEBAR CONFIGURATION
# ============================================================

with st.sidebar:

    st.header("⚙️ Settings")

    # User selects research depth
    search_depth = st.selectbox(
        "Research Depth",
        options=["Quick", "Standard", "Deep"],
        index=1,
        help="Controls how many web sources are retrieved for each query."
    )

    # Number of sources based on selected depth
    depth_map = {
        "Quick": 3,
        "Standard": 5,
        "Deep": 10
    }

    max_results = depth_map[search_depth]

    st.info(
        f"📊 Will retrieve up to **{max_results} sources per query**"
    )


# ============================================================
# MAIN INPUT AREA
# ============================================================

st.subheader("📝 Your Research Question")

question = st.text_area(
    "What would you like to research?",
    placeholder=(
        "Example: What are the latest developments in "
        "retrieval augmented generation (RAG) for LLMs?"
    ),
    height=100,
    label_visibility="collapsed"
)


# ============================================================
# RESEARCH CONTROLS
# ============================================================

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    research_button = st.button(
        "🚀 Start Research",
        type="primary",
        use_container_width=True
    )

with col2:
    clear_button = st.button(
        "🔄 Clear",
        use_container_width=True
    )


# ============================================================
# CLEAR RESULTS
# ============================================================

if clear_button:
    st.rerun()


# ============================================================
# EXECUTE RESEARCH
# ============================================================

if research_button:

    if not question.strip():

        st.warning("⚠️ Please enter a research question.")

    else:

        # ----------------------------------------------------
        # Progress tracking
        # ----------------------------------------------------

        progress_bar = st.progress(
            0,
            text="Starting research..."
        )

        status_container = st.container()

        with status_container:

            progress_bar.progress(
                10,
                text="📋 Creating research plan..."
            )

            progress_bar.progress(
                40,
                text="🔍 Searching the web..."
            )

            progress_bar.progress(
                70,
                text="📊 Analyzing sources..."
            )

            # ------------------------------------------------
            # Execute research
            # ------------------------------------------------

            with st.spinner(
                "⏳ AIPRA is researching... This may take a minute."
            ):

                try:

                    # IMPORTANT:
                    # Pass the selected search depth to the agent.
                    result = research(
                        question,
                        max_results=max_results
                    )

                    progress_bar.progress(
                        100,
                        text="✅ Research completed!"
                    )

                except Exception as e:

                    st.error(
                        f"❌ Error during research: {str(e)}"
                    )

                    st.stop()


        st.success("✅ Research completed successfully!")

        st.divider()


        # ====================================================
        # DISPLAY RESEARCH PLAN
        # ====================================================

        with st.expander(
            "📋 Research Queries",
            expanded=True
        ):

            st.write(
                "AIPRA generated these search queries:"
            )

            for i, query in enumerate(
                result["queries"],
                1
            ):

                st.write(
                    f"{i}. **{query}**"
                )


        # ====================================================
        # DISPLAY RESEARCH REPORT
        # ====================================================

        st.subheader("📑 Research Report")

        st.markdown(
            result["report"]
        )

        st.divider()


        # ====================================================
        # DISPLAY SOURCES
        # ====================================================

        with st.expander(
            "📚 Sources",
            expanded=False
        ):

            st.write(
                f"**Total sources found: "
                f"{len(result['sources'])}**"
            )

            if result["sources"]:

                for i, source in enumerate(
                    result["sources"],
                    1
                ):

                    with st.container(
                        border=True
                    ):

                        col1, col2 = st.columns(
                            [3, 1]
                        )

                        with col1:

                            st.markdown(
                                f"**[{i}] "
                                f"{source.get('title', 'Untitled')}**"
                            )

                            st.markdown(
                                f"🔗 "
                                f"{source.get('url', 'N/A')}"
                            )

                        with col2:

                            if source.get("score"):

                                st.metric(
                                    "Score",
                                    f"{source.get('score'):.2f}"
                                )

            else:

                st.info(
                    "No sources found for this research query."
                )


        # ====================================================
        # EXPORT OPTIONS
        # ====================================================

        st.divider()

        st.subheader("💾 Export Options")

        col1, col2 = st.columns(2)


        # ----------------------------------------------------
        # Markdown export
        # ----------------------------------------------------

        with col1:

            markdown_text = result["report"]

            st.download_button(
                label="📄 Download Report (Markdown)",
                data=markdown_text,
                file_name="AIPRA_research_report.md",
                mime="text/markdown"
            )


        # ----------------------------------------------------
        # Text export
        # ----------------------------------------------------

        with col2:

            full_text = (
                f"{result['report']}\n\n"
                "---\n\n"
                "## Queries Used:\n"
            )

            for q in result["queries"]:

                full_text += f"- {q}\n"

            st.download_button(
                label="📋 Download Full Report (Text)",
                data=full_text,
                file_name="AIPRA_research_report.txt",
                mime="text/plain"
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    ---

    **AIPRA - AI Personal Research Agent** | Phase 1 MVP

    - 🔍 Multi-query web research
    - 🤖 LLM-powered analysis
    - 📚 Citation-backed reports
    - 🚀 Agentic workflow

    [GitHub](https://github.com/Priyanshi712/AIPRA)
    """
)
