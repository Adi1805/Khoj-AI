"""Khoj AI — Multi-Agent Autonomous Research System.

A stunning Streamlit frontend for the multi-agent research pipeline.
Run with: streamlit run app.py
"""

import streamlit as st
import time
import os
from dotenv import load_dotenv

# Page configuration — must be first Streamlit command
st.set_page_config(
    page_title="Khoj AI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS — Premium Dark Mode UI
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* === Global Dark Theme === */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #0d0d1a 50%, #0a0f1a 100%);
        font-family: 'Inter', sans-serif;
        color: #e0e0e0;
    }

    /* Hide Streamlit defaults */
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}

    /* === Input Styling === */
    .stTextInput > div > div > input {
        background: #1a1a2e !important;
        border: 1px solid rgba(102,126,234,0.3) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        padding: 14px 18px !important;
        font-size: 16px !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        caret-color: #667eea !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: #6a6a8a !important;
        opacity: 1 !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(102,126,234,0.6) !important;
        box-shadow: 0 0 20px rgba(102,126,234,0.15) !important;
        background: #1e1e36 !important;
    }
    /* Force dark theme on Streamlit input container */
    .stTextInput > div > div {
        background: #1a1a2e !important;
        border-radius: 12px !important;
    }
    .stTextInput > div {
        background: transparent !important;
    }
    .stTextInput label {
        color: #a0a0b0 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* === Button Styling === */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 32px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        letter-spacing: 0.5px;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102,126,234,0.35) !important;
    }

    /* === Tab Styling === */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #a0a0b0 !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(102,126,234,0.2) !important;
        color: #ffffff !important;
    }

    /* === Expander Styling === */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.03) !important;
        border-radius: 8px !important;
        color: #e0e0e0 !important;
    }

    /* === Sidebar Styling === */
    section[data-testid="stSidebar"] {
        background: rgba(10,10,20,0.95) !important;
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: #c0c0d0;
    }

    /* === Download Button === */
    .stDownloadButton > button {
        background: rgba(255,255,255,0.05) !important;
        color: #e0e0e0 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stDownloadButton > button:hover {
        background: rgba(255,255,255,0.1) !important;
        border-color: rgba(102,126,234,0.4) !important;
    }

    /* === Cards & Containers === */
    .glass-card {
        background: rgba(255,255,255,0.03);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 24px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        border-color: rgba(102,126,234,0.3);
        box-shadow: 0 4px 20px rgba(102,126,234,0.1);
    }

    /* === Gradient Text === */
    .gradient-text {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
    }

    /* === Badge Styles === */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .badge-high { background: rgba(0,210,100,0.15); color: #00d264; border: 1px solid rgba(0,210,100,0.3); }
    .badge-medium { background: rgba(255,193,7,0.15); color: #ffc107; border: 1px solid rgba(255,193,7,0.3); }
    .badge-low { background: rgba(255,82,82,0.15); color: #ff5252; border: 1px solid rgba(255,82,82,0.3); }
    .badge-web { background: rgba(33,150,243,0.15); color: #2196f3; border: 1px solid rgba(33,150,243,0.3); }
    .badge-paper { background: rgba(76,175,80,0.15); color: #4caf50; border: 1px solid rgba(76,175,80,0.3); }
    .badge-wiki { background: rgba(156,39,176,0.15); color: #ce93d8; border: 1px solid rgba(156,39,176,0.3); }

    /* === Agent Status Cards === */
    .agent-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .agent-card .agent-emoji { font-size: 28px; }
    .agent-card .agent-name { font-size: 13px; font-weight: 600; color: #e0e0e0; margin-top: 8px; }
    .agent-card .agent-stat { font-size: 11px; color: #a0a0b0; margin-top: 4px; }

    /* === Feature badges === */
    .feature-row {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        justify-content: center;
        margin: 16px 0;
    }
    .feature-badge {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px;
        padding: 8px 16px;
        font-size: 13px;
        color: #c0c0d0;
    }

    /* === Animations === */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .fade-in { animation: fadeIn 0.5s ease-out; }

    /* === Source Card === */
    .source-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 10px;
        padding: 14px 18px;
        margin: 6px 0;
        transition: all 0.2s ease;
    }
    .source-card:hover {
        background: rgba(255,255,255,0.06);
        border-color: rgba(102,126,234,0.3);
    }

    /* === Metrics override === */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stMetricLabel"] {
        color: #a0a0b0 !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
if "research_history" not in st.session_state:
    st.session_state.research_history = []
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "is_researching" not in st.session_state:
    st.session_state.is_researching = False


# ============================================================
# MAIN CONTENT — HEADER
# ============================================================
st.markdown("""
<div style="text-align: center; padding: 30px 0 10px 0;" class="fade-in">
    <h1 style="font-size: 48px; margin-bottom: 8px;">
        🔬 <span class="gradient-text">Khoj AI</span>
    </h1>
    <p style="font-size: 18px; color: #808090; margin-bottom: 20px;">
        Multi-Agent Autonomous Research System
    </p>
    <div class="feature-row">
        <span class="feature-badge">🧠 5 AI Agents</span>
        <span class="feature-badge">🔍 Web + Academic</span>
        <span class="feature-badge">✅ Fact-Checked</span>
        <span class="feature-badge">📋 Cited Reports</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# SEARCH SECTION
# ============================================================
col_search, col_btn = st.columns([5, 1])

with col_search:
    query = st.text_input(
        "Research Query",
        placeholder="What would you like to research? (e.g., 'Latest breakthroughs in fusion energy')",
        label_visibility="collapsed",
    )

with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    research_clicked = st.button("🚀 Research", use_container_width=True)


# RESEARCH EXECUTION
# ============================================================
if research_clicked and query:
    st.session_state.is_researching = True

    # Check for API key
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_google_api_key_here":
        st.error("""
        **⚠️ Google API Key not configured!**

        1. Get your FREE API key from [Google AI Studio](https://aistudio.google.com/apikey)
        2. Create a `.env` file in the project root
        3. Add: `GOOGLE_API_KEY=your_key_here`
        4. Restart the app
        """)
        st.stop()

    with st.status("🔬 **Research in Progress...**", expanded=True) as status:
        st.write("🧠 **Manager Agent**: Analyzing and decomposing your query...")
        time.sleep(0.5)

        try:
            from src.graph.research_graph import run_research

            result = run_research(query)
            st.session_state.current_result = result
            st.session_state.research_history.append({
                "query": query,
                "result": result,
            })

            status.update(label="✅ **Research Complete!**", state="complete", expanded=False)

        except Exception as e:
            status.update(label="❌ **Research Failed**", state="error")
            st.error(f"An error occurred: {str(e)}")
            st.session_state.current_result = None
            st.stop()

    st.session_state.is_researching = False


# ============================================================
# DISPLAY RESULTS
# ============================================================
result = st.session_state.current_result

if result:
    # Agent Summary Cards
    st.markdown("<br>", unsafe_allow_html=True)
    agent_cols = st.columns(5)

    agents_info = [
        ("🧠", "Manager", f"{len(result.get('sub_questions', []))} questions", "#7c3aed"),
        ("🔍", "Web Searcher", f"{len(result.get('web_results', []))} findings", "#2563eb"),
        ("📄", "Paper Reader", f"{len(result.get('paper_results', []))} papers", "#059669"),
        ("✅", "Fact Checker", f"{len(result.get('verified_facts', []))} verified", "#d97706"),
        ("✍️", "Writer", "Report ready", "#dc2626"),
    ]

    for col, (emoji, name, stat, color) in zip(agent_cols, agents_info):
        with col:
            st.markdown(f"""
            <div class="agent-card" style="border-top: 2px solid {color};">
                <div class="agent-emoji">{emoji}</div>
                <div class="agent-name">{name}</div>
                <div class="agent-stat">{stat}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabbed Results
    tab_report, tab_facts, tab_sources, tab_activity = st.tabs([
        "📋 Report", "✅ Verified Facts", "📚 Sources", "🤖 Agent Activity"
    ])

    # === REPORT TAB ===
    with tab_report:
        report = result.get("final_report", "No report generated.")
        st.markdown(f"""<div class="glass-card fade-in">{""}</div>""", unsafe_allow_html=True)
        st.markdown(report)

        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label="📥 Export Report as Markdown",
            data=report,
            file_name=f"research_report_{result.get('query', 'report')[:30].replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    # === VERIFIED FACTS TAB ===
    with tab_facts:
        facts = result.get("verified_facts", [])
        if not facts:
            st.info("No verified facts available.")
        else:
            for fact in facts:
                confidence = fact.get("confidence", "MEDIUM").upper()
                badge_class = {
                    "HIGH": "badge-high",
                    "MEDIUM": "badge-medium",
                    "LOW": "badge-low",
                }.get(confidence, "badge-medium")

                confidence_emoji = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🔴"}.get(confidence, "🟡")
                sources_list = fact.get("supporting_sources", [])
                sources_text = ", ".join(str(s) for s in sources_list) if sources_list else "N/A"
                contradictions = fact.get("contradictions", [])

                st.markdown(f"""
                <div class="source-card">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                        <span>{confidence_emoji}</span>
                        <span class="badge {badge_class}">{confidence}</span>
                    </div>
                    <p style="color: #e0e0e0; font-size: 14px; margin: 8px 0;">{fact.get("claim", "N/A")}</p>
                    <p style="color: #808090; font-size: 12px; margin: 4px 0;">📎 Sources: {sources_text}</p>
                    {"<p style='color: #ff5252; font-size: 12px;'>⚠️ Contradictions: " + ", ".join(str(c) for c in contradictions if c) + "</p>" if contradictions and any(c for c in contradictions if c) else ""}
                </div>
                """, unsafe_allow_html=True)

    # === SOURCES TAB ===
    with tab_sources:
        sources = result.get("sources", [])
        if not sources:
            st.info("No sources collected.")
        else:
            # Group by source type
            web_sources = [s for s in sources if s.get("source_type") == "web"]
            paper_sources = [s for s in sources if s.get("source_type") == "paper"]
            wiki_sources = [s for s in sources if s.get("source_type") == "wiki"]

            if web_sources:
                st.markdown("#### 🌐 Web Sources")
                for s in web_sources:
                    url = s.get("url", "")
                    name = s.get("source", "Web Source")
                    st.markdown(f"""
                    <div class="source-card">
                        <span class="badge badge-web">WEB</span>
                        <span style="color: #e0e0e0; margin-left: 10px;">{name}</span>
                        {"<br><a href='" + url + "' target='_blank' style='color: #667eea; font-size: 12px;'>" + url[:80] + "</a>" if url else ""}
                    </div>
                    """, unsafe_allow_html=True)

            if paper_sources:
                st.markdown("#### 📄 Academic Papers")
                for s in paper_sources:
                    url = s.get("url", "")
                    name = s.get("source", "ArXiv Paper")
                    st.markdown(f"""
                    <div class="source-card">
                        <span class="badge badge-paper">PAPER</span>
                        <span style="color: #e0e0e0; margin-left: 10px;">{name[:80]}</span>
                        {"<br><a href='" + url + "' target='_blank' style='color: #4caf50; font-size: 12px;'>" + url[:80] + "</a>" if url else ""}
                    </div>
                    """, unsafe_allow_html=True)

            if wiki_sources:
                st.markdown("#### 📖 Wikipedia")
                for s in wiki_sources:
                    url = s.get("url", "")
                    name = s.get("source", "Wikipedia")
                    st.markdown(f"""
                    <div class="source-card">
                        <span class="badge badge-wiki">WIKI</span>
                        <span style="color: #e0e0e0; margin-left: 10px;">{name}</span>
                        {"<br><a href='" + url + "' target='_blank' style='color: #ce93d8; font-size: 12px;'>" + url[:80] + "</a>" if url else ""}
                    </div>
                    """, unsafe_allow_html=True)

            if not web_sources and not paper_sources and not wiki_sources:
                for s in sources:
                    url = s.get("url", "")
                    name = s.get("source", "Source")
                    st.markdown(f"""
                    <div class="source-card">
                        <span class="badge badge-web">SOURCE</span>
                        <span style="color: #e0e0e0; margin-left: 10px;">{name[:80]}</span>
                        {"<br><a href='" + url + "' target='_blank' style='color: #667eea; font-size: 12px;'>" + url[:80] + "</a>" if url else ""}
                    </div>
                    """, unsafe_allow_html=True)

    # === AGENT ACTIVITY TAB ===
    with tab_activity:
        st.markdown("#### 📝 Sub-Questions Generated")
        for i, q in enumerate(result.get("sub_questions", []), 1):
            st.markdown(f"""
            <div class="source-card">
                <span style="color: #667eea; font-weight: 600;">Q{i}.</span>
                <span style="color: #e0e0e0; margin-left: 8px;">{q}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📊 Agent Status Log")
        for update in result.get("status_updates", []):
            st.markdown(f"""
            <div class="source-card" style="padding: 10px 14px;">
                <span style="color: #c0c0d0; font-size: 13px;">{update}</span>
            </div>
            """, unsafe_allow_html=True)

        # Quick stats
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📈 Research Statistics")
        stat_cols = st.columns(4)
        with stat_cols[0]:
            st.metric("Sub-Questions", len(result.get("sub_questions", [])))
        with stat_cols[1]:
            st.metric("Web Findings", len(result.get("web_results", [])))
        with stat_cols[2]:
            st.metric("Papers Found", len(result.get("paper_results", [])))
        with stat_cols[3]:
            st.metric("Verified Facts", len(result.get("verified_facts", [])))


# ============================================================
# EMPTY STATE (no results yet)
# ============================================================
elif not st.session_state.is_researching:
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px;" class="fade-in">
        <div style="font-size: 64px; margin-bottom: 16px;">🔬</div>
        <h3 style="color: #808090; font-weight: 400; margin-bottom: 8px;">
            Enter a research topic above to get started
        </h3>
        <p style="color: #505060; font-size: 14px;">
            Khoj AI will deploy 5 specialized agents to research your topic,<br>
            cross-verify facts, and generate a comprehensive cited report.
        </p>
    </div>
    """, unsafe_allow_html=True)