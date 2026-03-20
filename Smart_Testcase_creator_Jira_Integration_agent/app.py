"""
Smart Test Case Creator Agent - JIRA & LLM Integration
Main Streamlit Application (Light Theme, Two-Tab Layout)
"""

import streamlit as st
import pandas as pd
from tools.handshake import (
    test_jira_connection,
    test_groq_connection,
    test_ollama_connection,
    fetch_groq_models,
)
from tools.jira_client import fetch_ticket, validate_ticket_id
from tools.llm_engine import (
    generate_via_groq, generate_via_ollama,
    generate_via_groq_stream, generate_via_ollama_stream,
    _parse_llm_response,
)


# ─── Page Config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Smart Test Case Creator",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─── Custom CSS (Light Theme) ────────────────────────────────────────────────

st.markdown("""
<style>
    /* ── Import Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ── Root Variables ── */
    :root {
        --primary: #2563eb;
        --primary-light: #3b82f6;
        --primary-dark: #1d4ed8;
        --primary-bg: #eff6ff;
        --success: #16a34a;
        --success-bg: #f0fdf4;
        --success-border: #bbf7d0;
        --danger: #dc2626;
        --danger-bg: #fef2f2;
        --danger-border: #fecaca;
        --warning: #d97706;
        --warning-bg: #fffbeb;
        --warning-border: #fde68a;
        --bg-main: #f8fafc;
        --bg-white: #ffffff;
        --bg-sidebar: #1e293b;
        --text-dark: #0f172a;
        --text-mid: #475569;
        --text-light: #94a3b8;
        --border: #e2e8f0;
        --border-focus: #93c5fd;
        --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
        --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
        --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -4px rgba(0,0,0,0.05);
        --radius: 12px;
        --radius-sm: 8px;
    }

    /* ── Global ── */
    .stApp {
        background: var(--bg-main) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* ── Sidebar (Dark Contrast) ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        border-right: none;
        box-shadow: 4px 0 24px rgba(0,0,0,0.12);
    }

    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    section[data-testid="stSidebar"] .stMarkdown p {
        color: #94a3b8 !important;
    }

    /* ── Sidebar Nav Buttons ── */
    .nav-btn {
        display: flex;
        align-items: center;
        gap: 12px;
        width: 100%;
        padding: 14px 18px;
        border-radius: 10px;
        font-size: 0.88rem;
        font-weight: 600;
        letter-spacing: 0.01em;
        cursor: pointer;
        transition: all 0.2s ease;
        border: 1px solid transparent;
        text-decoration: none;
        margin-bottom: 6px;
    }

    .nav-btn-active {
        background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
        color: white !important;
        box-shadow: 0 4px 16px rgba(37,99,235,0.35);
        border-color: rgba(255,255,255,0.1);
    }

    .nav-btn-inactive {
        background: rgba(255,255,255,0.05);
        color: #94a3b8 !important;
        border-color: rgba(255,255,255,0.06);
    }

    .nav-btn-inactive:hover {
        background: rgba(255,255,255,0.1);
        color: white !important;
    }

    .nav-icon {
        font-size: 1.2rem;
        width: 24px;
        text-align: center;
    }

    /* ── Main Panel Cards ── */
    .config-card {
        background: var(--bg-white);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 28px;
        box-shadow: var(--shadow-md);
        transition: box-shadow 0.2s ease;
        height: 100%;
    }

    .config-card:hover {
        box-shadow: var(--shadow-lg);
    }

    .config-card-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
        padding-bottom: 16px;
        border-bottom: 2px solid var(--border);
    }

    .config-card-header .icon-circle {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        flex-shrink: 0;
    }

    .icon-jira {
        background: linear-gradient(135deg, #2563eb, #60a5fa);
        color: white;
    }

    .icon-llm {
        background: linear-gradient(135deg, #7c3aed, #a78bfa);
        color: white;
    }

    .config-card-header h3 {
        color: var(--text-dark) !important;
        font-size: 1.1rem;
        font-weight: 700;
        margin: 0;
    }

    .config-card-header p {
        color: var(--text-light);
        font-size: 0.8rem;
        margin: 0;
    }

    /* ── Status Badges ── */
    .badge-connected {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: var(--success-bg);
        border: 1px solid var(--success-border);
        color: var(--success) !important;
        padding: 8px 16px;
        border-radius: 100px;
        font-size: 0.82rem;
        font-weight: 600;
    }

    .badge-failed {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: var(--danger-bg);
        border: 1px solid var(--danger-border);
        color: var(--danger) !important;
        padding: 8px 16px;
        border-radius: 100px;
        font-size: 0.82rem;
        font-weight: 600;
    }

    .badge-pending {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: var(--warning-bg);
        border: 1px solid var(--warning-border);
        color: var(--warning) !important;
        padding: 8px 16px;
        border-radius: 100px;
        font-size: 0.82rem;
        font-weight: 600;
    }

    /* ── Page Header Banner ── */
    .page-header {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
        border-radius: 16px;
        padding: 32px 36px;
        margin-bottom: 28px;
        color: white;
        box-shadow: 0 8px 30px rgba(37,99,235,0.2);
        position: relative;
        overflow: hidden;
    }

    .page-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 300px;
        height: 300px;
        background: rgba(255,255,255,0.06);
        border-radius: 50%;
    }

    .page-header::after {
        content: '';
        position: absolute;
        bottom: -60%;
        left: 10%;
        width: 200px;
        height: 200px;
        background: rgba(255,255,255,0.04);
        border-radius: 50%;
    }

    .page-header h1 {
        color: white !important;
        font-size: 1.6rem !important;
        font-weight: 800;
        margin: 0 0 6px 0 !important;
        position: relative;
        z-index: 1;
    }

    .page-header p {
        color: rgba(255,255,255,0.85);
        font-size: 0.9rem;
        margin: 0;
        position: relative;
        z-index: 1;
    }

    /* ── Ticket Detail Card ── */
    .ticket-card {
        background: var(--bg-white);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 24px 28px;
        box-shadow: var(--shadow-md);
        margin: 16px 0;
    }

    .ticket-card h3 {
        color: var(--primary) !important;
        font-size: 1.05rem;
        font-weight: 700;
        margin: 0 0 16px 0;
        padding-bottom: 12px;
        border-bottom: 2px solid var(--primary-bg);
    }

    .ticket-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr;
        gap: 16px;
        margin-bottom: 16px;
    }

    .ticket-field-label {
        color: var(--text-light);
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
        margin-bottom: 4px;
    }

    .ticket-field-value {
        color: var(--text-dark);
        font-size: 0.88rem;
        font-weight: 500;
        line-height: 1.5;
    }

    .ticket-section {
        margin-top: 16px;
        padding-top: 12px;
        border-top: 1px solid var(--border);
    }

    .ticket-desc {
        color: var(--text-mid);
        font-size: 0.85rem;
        line-height: 1.7;
        white-space: pre-wrap;
        max-height: 180px;
        overflow-y: auto;
        padding: 12px;
        background: #f8fafc;
        border-radius: 8px;
        border: 1px solid var(--border);
    }

    /* ── Progress Steps ── */
    .workflow-steps {
        display: flex;
        gap: 6px;
        margin: 16px 0 24px 0;
        flex-wrap: wrap;
        align-items: center;
    }

    .wf-step {
        padding: 7px 18px;
        border-radius: 100px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }

    .wf-active {
        background: linear-gradient(135deg, var(--primary), #7c3aed);
        color: white;
        box-shadow: 0 3px 12px rgba(37,99,235,0.3);
    }

    .wf-done {
        background: var(--success-bg);
        color: var(--success);
        border: 1px solid var(--success-border);
    }

    .wf-pending {
        background: #f1f5f9;
        color: var(--text-light);
        border: 1px solid var(--border);
    }

    .wf-arrow {
        color: var(--text-light);
        font-size: 0.8rem;
    }

    /* ── Toggle Provider Buttons ── */
    .provider-toggle {
        display: flex;
        background: #f1f5f9;
        border-radius: 10px;
        padding: 4px;
        margin-bottom: 20px;
        border: 1px solid var(--border);
    }

    .provider-opt {
        flex: 1;
        padding: 10px 16px;
        text-align: center;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .provider-opt-active {
        background: var(--bg-white);
        color: var(--primary);
        box-shadow: var(--shadow-sm);
    }

    .provider-opt-inactive {
        background: transparent;
        color: var(--text-light);
    }

    /* ── Locked Panel ── */
    .locked-panel {
        background: var(--bg-white);
        border: 2px dashed var(--border);
        border-radius: 16px;
        padding: 60px 40px;
        text-align: center;
    }

    .locked-panel h2 {
        color: var(--text-mid) !important;
        font-size: 1.2rem;
        font-weight: 700;
    }

    .locked-panel p {
        color: var(--text-light);
        font-size: 0.88rem;
        max-width: 480px;
        margin: 8px auto 0;
        line-height: 1.6;
    }

    /* ── Sidebar Brand ── */
    .sidebar-brand {
        padding: 8px 0 24px 0;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 24px;
        text-align: center;
    }

    .sidebar-brand h2 {
        color: white !important;
        font-size: 1.1rem;
        font-weight: 800;
        margin: 0 0 2px 0;
        letter-spacing: -0.01em;
    }

    .sidebar-brand p {
        color: #64748b !important;
        font-size: 0.72rem;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    /* ── Status Dot for sidebar ── */
    .sidebar-status {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 6px 0;
        font-size: 0.78rem;
    }

    .dot-green { width:8px; height:8px; border-radius:50%; background:#22c55e; display:inline-block; }
    .dot-red { width:8px; height:8px; border-radius:50%; background:#ef4444; display:inline-block; }
    .dot-yellow { width:8px; height:8px; border-radius:50%; background:#eab308; display:inline-block; }

    /* ── Button styling ── */
    .stButton > button {
        border-radius: var(--radius-sm);
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.15s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
    }

    /* ── Remove default Streamlit padding from top ── */
    .block-container {
        padding-top: 2rem !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #f1f5f9; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
</style>
""", unsafe_allow_html=True)


# ─── Session State Defaults ──────────────────────────────────────────────────

def init_session_state():
    defaults = {
        # Navigation
        "active_tab": "config",
        # JIRA
        "jira_base_url": "",
        "jira_email": "",
        "jira_api_token": "",
        "jira_connected": False,
        "jira_status_msg": "",
        # LLM Provider
        "llm_provider": "Ollama (Local)",
        # Groq
        "groq_api_key": "",
        "groq_connected": False,
        "groq_status_msg": "",
        "groq_models": [],
        "groq_selected_model": "llama-3.3-70b-versatile",
        "groq_temperature": 0.1,
        # Ollama
        "ollama_base_url": "http://localhost:11434",
        "ollama_connected": False,
        "ollama_status_msg": "",
        "ollama_models": [],
        "ollama_selected_model": "",
        "ollama_temperature": 0.1,
        # Ticket
        "ticket_data": None,
        "recent_tickets": [],
        # Test Cases
        "test_cases": None,
        "generation_status": "",
        "raw_llm_response": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()


# ─── Helper ──────────────────────────────────────────────────────────────────

def is_ready():
    """Check if both JIRA and at least one LLM provider are connected."""
    jira_ok = st.session_state.jira_connected
    if st.session_state.llm_provider == "Groq (Cloud)":
        llm_ok = st.session_state.groq_connected
    else:
        llm_ok = st.session_state.ollama_connected
    return jira_ok and llm_ok


# ═══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR - Navigation Panel
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    # Brand
    st.markdown("""
    <div class="sidebar-brand">
        <h2>🧪 Smart TC Creator</h2>
        <p>JIRA + LLM Integration</p>
    </div>
    """, unsafe_allow_html=True)

    # Navigation Buttons
    if st.button(
        "⚙️  Configuration Settings",
        key="nav_config",
        use_container_width=True,
        type="primary" if st.session_state.active_tab == "config" else "secondary"
    ):
        st.session_state.active_tab = "config"
        st.rerun()

    if st.button(
        "🤖  Smart Testcase Generator",
        key="nav_generator",
        use_container_width=True,
        type="primary" if st.session_state.active_tab == "generator" else "secondary"
    ):
        st.session_state.active_tab = "generator"
        st.rerun()

    # Connection Status Summary
    st.markdown("---")
    st.markdown("##### Connection Status")

    # JIRA status
    if st.session_state.jira_connected:
        st.markdown('<div class="sidebar-status"><span class="dot-green"></span> JIRA Connected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="sidebar-status"><span class="dot-red"></span> JIRA Not Connected</div>', unsafe_allow_html=True)

    # LLM status
    if st.session_state.llm_provider == "Groq (Cloud)":
        if st.session_state.groq_connected:
            st.markdown('<div class="sidebar-status"><span class="dot-green"></span> Groq Connected</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="sidebar-status"><span class="dot-red"></span> Groq Not Connected</div>', unsafe_allow_html=True)
    else:
        if st.session_state.ollama_connected:
            st.markdown('<div class="sidebar-status"><span class="dot-green"></span> Ollama Connected</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="sidebar-status"><span class="dot-red"></span> Ollama Not Connected</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 1: CONFIGURATION SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

if st.session_state.active_tab == "config":

    # Header
    st.markdown("""
    <div class="page-header">
        <h1>Configuration & Settings</h1>
        <p>Configure your JIRA instance and LLM provider connections</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Two columns side by side: JIRA Config | LLM Provider Settings ─────
    col_jira, col_llm = st.columns(2, gap="large")

    # ═══════════════════════════════════════════
    #  A. JIRA Configuration
    # ═══════════════════════════════════════════
    with col_jira:
        st.markdown("""
        <div class="config-card">
            <div class="config-card-header">
                <div class="icon-circle icon-jira">🔗</div>
                <div>
                    <h3>JIRA Configuration</h3>
                    <p>Connect to your Atlassian JIRA instance</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        jira_url = st.text_input(
            "JIRA Base URL",
            value=st.session_state.jira_base_url,
            placeholder="https://company.atlassian.net",
            key="cfg_jira_url",
        )
        jira_email = st.text_input(
            "Email / Username",
            value=st.session_state.jira_email,
            placeholder="your-email@company.com",
            key="cfg_jira_email",
        )
        jira_token = st.text_input(
            "API Token",
            value=st.session_state.jira_api_token,
            type="password",
            placeholder="Paste your JIRA API token",
            key="cfg_jira_token",
        )

        if st.button("Test JIRA Connection", key="btn_cfg_jira", use_container_width=True, type="primary"):
            with st.spinner("Connecting to JIRA..."):
                st.session_state.jira_base_url = jira_url
                st.session_state.jira_email = jira_email
                st.session_state.jira_api_token = jira_token
                success, msg, _ = test_jira_connection(jira_url, jira_email, jira_token)
                st.session_state.jira_connected = success
                st.session_state.jira_status_msg = msg

        if st.session_state.jira_connected:
            st.markdown(f'<div class="badge-connected">✅ Connected &mdash; {st.session_state.jira_status_msg}</div>', unsafe_allow_html=True)
        elif st.session_state.jira_status_msg:
            st.markdown(f'<div class="badge-failed">❌ Failed &mdash; {st.session_state.jira_status_msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="badge-pending">⏳ Not Connected</div>', unsafe_allow_html=True)

    # ═══════════════════════════════════════════
    #  B. LLM Provider Settings
    # ═══════════════════════════════════════════
    with col_llm:
        st.markdown("""
        <div class="config-card">
            <div class="config-card-header">
                <div class="icon-circle icon-llm">🧠</div>
                <div>
                    <h3>LLM Provider Settings</h3>
                    <p>Choose and configure your AI model provider</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Provider Toggle
        llm_provider = st.radio(
            "Select LLM Provider",
            ["Ollama (Local)", "Groq (Cloud)"],
            index=0 if st.session_state.llm_provider == "Ollama (Local)" else 1,
            key="cfg_llm_toggle",
            horizontal=True,
        )
        st.session_state.llm_provider = llm_provider

        st.markdown("---")

        if llm_provider == "Groq (Cloud)":
            # ── Groq Config ──
            st.markdown("**Groq Configuration**")

            groq_key = st.text_input(
                "Groq API Key",
                value=st.session_state.groq_api_key,
                type="password",
                placeholder="gsk_...",
                key="cfg_groq_key",
            )

            if st.button("Test Groq Connection", key="btn_cfg_groq", use_container_width=True, type="primary"):
                with st.spinner("Connecting to Groq..."):
                    st.session_state.groq_api_key = groq_key
                    success, msg, _ = test_groq_connection(groq_key)
                    st.session_state.groq_connected = success
                    st.session_state.groq_status_msg = msg
                    if success:
                        st.session_state.groq_models = fetch_groq_models(groq_key)

            # Status
            if st.session_state.groq_connected:
                st.markdown(f'<div class="badge-connected">✅ Connected &mdash; {st.session_state.groq_status_msg}</div>', unsafe_allow_html=True)
            elif st.session_state.groq_status_msg:
                st.markdown(f'<div class="badge-failed">❌ Failed &mdash; {st.session_state.groq_status_msg}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="badge-pending">⏳ Not Connected</div>', unsafe_allow_html=True)

            # Model + Temp (shown after connection)
            if st.session_state.groq_connected and st.session_state.groq_models:
                st.markdown("")
                default_idx = 0
                if st.session_state.groq_selected_model in st.session_state.groq_models:
                    default_idx = st.session_state.groq_models.index(st.session_state.groq_selected_model)
                st.session_state.groq_selected_model = st.selectbox(
                    "Model",
                    st.session_state.groq_models,
                    index=default_idx,
                    key="cfg_groq_model",
                )

            st.session_state.groq_temperature = st.slider(
                "Temperature", 0.0, 1.0,
                value=st.session_state.groq_temperature,
                step=0.1,
                key="cfg_groq_temp",
            )

        else:
            # ── Ollama Config ──
            st.markdown("**Ollama Configuration**")

            ollama_url = st.text_input(
                "Ollama Base URL",
                value=st.session_state.ollama_base_url,
                placeholder="http://localhost:11434",
                key="cfg_ollama_url",
            )

            if st.button("Test Ollama Connection", key="btn_cfg_ollama", use_container_width=True, type="primary"):
                with st.spinner("Connecting to Ollama..."):
                    st.session_state.ollama_base_url = ollama_url
                    success, msg, models = test_ollama_connection(ollama_url)
                    st.session_state.ollama_connected = success
                    st.session_state.ollama_status_msg = msg
                    if models:
                        st.session_state.ollama_models = models

            # Status
            if st.session_state.ollama_connected:
                st.markdown(f'<div class="badge-connected">✅ Connected &mdash; {st.session_state.ollama_status_msg}</div>', unsafe_allow_html=True)
            elif st.session_state.ollama_status_msg:
                st.markdown(f'<div class="badge-failed">❌ Failed &mdash; {st.session_state.ollama_status_msg}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="badge-pending">⏳ Not Connected</div>', unsafe_allow_html=True)

            # Model + Temp (shown after connection)
            if st.session_state.ollama_connected and st.session_state.ollama_models:
                st.markdown("")
                default_idx = 0
                if st.session_state.ollama_selected_model in st.session_state.ollama_models:
                    default_idx = st.session_state.ollama_models.index(st.session_state.ollama_selected_model)
                st.session_state.ollama_selected_model = st.selectbox(
                    "Model",
                    st.session_state.ollama_models,
                    index=default_idx,
                    key="cfg_ollama_model",
                )

            st.session_state.ollama_temperature = st.slider(
                "Temperature", 0.0, 1.0,
                value=st.session_state.ollama_temperature,
                step=0.1,
                key="cfg_ollama_temp",
            )


# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 2: SMART TESTCASE GENERATOR AGENT
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.active_tab == "generator":

    # Header
    st.markdown("""
    <div class="page-header">
        <h1>Smart Testcase Generator Agent</h1>
        <p>Fetch JIRA tickets and generate comprehensive test cases using AI</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Check if connections are ready ────────────────────────────────────
    if not is_ready():
        st.markdown("""
        <div class="locked-panel">
            <h2>🔒 Connections Required</h2>
            <p>Please go to <strong>Configuration Settings</strong> and establish both JIRA and LLM provider connections before using the test case generator.</p>
        </div>
        """, unsafe_allow_html=True)

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if not st.session_state.jira_connected:
                st.warning("JIRA is not connected. Configure it in settings.")
            else:
                st.success("JIRA is connected.")
        with col_s2:
            if st.session_state.llm_provider == "Groq (Cloud)" and not st.session_state.groq_connected:
                st.warning("Groq is not connected. Configure it in settings.")
            elif st.session_state.llm_provider == "Ollama (Local)" and not st.session_state.ollama_connected:
                st.warning("Ollama is not connected. Configure it in settings.")
            else:
                st.success("LLM provider is connected.")

        st.stop()

    # ═══════════════════════════════════════════════════════════════════════
    #  ACTIVE WORKSPACE
    # ═══════════════════════════════════════════════════════════════════════

    # ── Step 1: Ticket Input ──────────────────────────────────────────────

    st.markdown("#### Step 1: Enter JIRA Ticket Key")

    col_input, col_btn = st.columns([4, 1])

    with col_input:
        ticket_id = st.text_input(
            "Ticket ID",
            placeholder="e.g., VWO-123, PROJ-456",
            key="gen_ticket_id",
            label_visibility="collapsed",
        )
    with col_btn:
        fetch_clicked = st.button("Fetch Details", key="btn_fetch", use_container_width=True, type="primary")

    # Recent tickets bar
    if st.session_state.recent_tickets:
        st.caption("Recently fetched:")
        recent_cols = st.columns(min(len(st.session_state.recent_tickets), 5))
        for idx, tid in enumerate(st.session_state.recent_tickets[:5]):
            with recent_cols[idx]:
                if st.button(tid, key=f"recent_{idx}", use_container_width=True):
                    ticket_id = tid
                    fetch_clicked = True

    # ── Fetch Logic ───────────────────────────────────────────────────────

    if fetch_clicked and ticket_id:
        ticket_id_clean = ticket_id.strip().upper()

        if not validate_ticket_id(ticket_id_clean):
            st.error("Invalid ticket format. Expected: `PROJECT-123` (e.g., VWO-456)")
        else:
            # Progress
            st.markdown("""
            <div class="workflow-steps">
                <span class="wf-step wf-active">Fetching Ticket</span>
                <span class="wf-arrow">→</span>
                <span class="wf-step wf-pending">Analyzing Context</span>
                <span class="wf-arrow">→</span>
                <span class="wf-step wf-pending">Generating Test Cases</span>
                <span class="wf-arrow">→</span>
                <span class="wf-step wf-pending">Complete</span>
            </div>
            """, unsafe_allow_html=True)

            with st.spinner(f"Fetching {ticket_id_clean} from JIRA..."):
                success, result = fetch_ticket(
                    st.session_state.jira_base_url,
                    st.session_state.jira_email,
                    st.session_state.jira_api_token,
                    ticket_id_clean,
                )

            if success:
                st.session_state.ticket_data = result
                st.session_state.test_cases = None
                st.session_state.raw_llm_response = ""

                if ticket_id_clean not in st.session_state.recent_tickets:
                    st.session_state.recent_tickets.insert(0, ticket_id_clean)
                    st.session_state.recent_tickets = st.session_state.recent_tickets[:5]

                st.toast(f"Ticket {ticket_id_clean} fetched!", icon="✅")
                st.rerun()
            else:
                st.error(result)

    # ── Step 2: Display Ticket Details ────────────────────────────────────

    if st.session_state.ticket_data:
        td = st.session_state.ticket_data

        st.markdown("#### Step 2: Ticket Details")

        st.markdown(f"""
        <div class="ticket-card">
            <h3>🎫 {td['key']} — {td['summary']}</h3>
            <div class="ticket-grid">
                <div>
                    <div class="ticket-field-label">Priority</div>
                    <div class="ticket-field-value">{td['priority']}</div>
                </div>
                <div>
                    <div class="ticket-field-label">Status</div>
                    <div class="ticket-field-value">{td['status']}</div>
                </div>
                <div>
                    <div class="ticket-field-label">Assignee</div>
                    <div class="ticket-field-value">{td['assignee']}</div>
                </div>
                <div>
                    <div class="ticket-field-label">Issue Type</div>
                    <div class="ticket-field-value">{td['issue_type']}</div>
                </div>
            </div>
            <div>
                <div class="ticket-field-label">Labels</div>
                <div class="ticket-field-value">{', '.join(td['labels']) if td['labels'] else 'None'}</div>
            </div>
            <div class="ticket-section">
                <div class="ticket-field-label">Description</div>
                <div class="ticket-desc">{td['description'][:2000]}</div>
            </div>
            <div class="ticket-section">
                <div class="ticket-field-label">Acceptance Criteria</div>
                <div class="ticket-desc">{td['acceptance_criteria'][:1000]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Step 3: Generate Test Cases ───────────────────────────────────

        st.markdown("#### Step 3: Generate Test Cases")

        if st.session_state.llm_provider == "Groq (Cloud)":
            model_label = st.session_state.groq_selected_model
        else:
            model_label = st.session_state.ollama_selected_model

        st.caption(f"Using **{st.session_state.llm_provider}** → Model: **{model_label}**")

        if st.button("🚀 Generate Test Cases", key="btn_generate", use_container_width=True, type="primary"):
            progress_holder = st.empty()
            status_holder = st.empty()

            def show_progress(step_idx):
                labels = ["Fetching Ticket", "Analyzing Context", "Generating Test Cases", "Complete"]
                parts = []
                for i, lbl in enumerate(labels):
                    if i < step_idx:
                        parts.append(f'<span class="wf-step wf-done">{lbl}</span>')
                    elif i == step_idx:
                        parts.append(f'<span class="wf-step wf-active">{lbl}</span>')
                    else:
                        parts.append(f'<span class="wf-step wf-pending">{lbl}</span>')
                    if i < len(labels) - 1:
                        parts.append('<span class="wf-arrow">→</span>')
                progress_holder.markdown(f'<div class="workflow-steps">{"".join(parts)}</div>', unsafe_allow_html=True)

            show_progress(0)
            status_holder.info("Preparing ticket context...")

            show_progress(1)
            status_holder.info("Analyzing ticket data and building LLM prompt...")

            show_progress(2)
            status_holder.info("Generating test cases with live streaming...")

            # ── Live Streaming Output (like ChatGPT) ──
            stream_container = st.empty()
            full_streamed_text = ""
            final_result = None

            try:
                if st.session_state.llm_provider == "Groq (Cloud)":
                    stream_gen = generate_via_groq_stream(
                        st.session_state.groq_api_key,
                        st.session_state.groq_selected_model,
                        td,
                        st.session_state.groq_temperature,
                    )
                else:
                    stream_gen = generate_via_ollama_stream(
                        st.session_state.ollama_base_url,
                        st.session_state.ollama_selected_model,
                        td,
                        st.session_state.ollama_temperature,
                    )

                for chunk_text, is_done, result_data in stream_gen:
                    if not is_done:
                        full_streamed_text += chunk_text
                        stream_container.code(full_streamed_text, language="json")
                    else:
                        final_result = result_data

            except Exception as e:
                final_result = (False, f"Streaming error: {str(e)}", None)

            # ── Process final result ──
            if final_result:
                success, result, raw = final_result
                if success:
                    st.session_state.test_cases = result
                    st.session_state.raw_llm_response = raw or full_streamed_text
                    show_progress(3)
                    status_holder.success(f"Successfully generated {len(result)} test cases!")
                    stream_container.empty()  # Clear streaming view
                    st.rerun()
                else:
                    show_progress(2)
                    status_holder.error(f"Generation failed: {result}")
                    if raw:
                        with st.expander("View Raw LLM Response (Debug)"):
                            st.code(raw, language="json")
            else:
                status_holder.error("No response received from LLM.")

        # ── Step 4: Output Table ──────────────────────────────────────────

        if st.session_state.test_cases:
            st.markdown("#### Step 4: Generated Test Cases")

            # Completed progress
            st.markdown("""
            <div class="workflow-steps">
                <span class="wf-step wf-done">Fetching Ticket</span>
                <span class="wf-arrow">→</span>
                <span class="wf-step wf-done">Analyzing Context</span>
                <span class="wf-arrow">→</span>
                <span class="wf-step wf-done">Generating Test Cases</span>
                <span class="wf-arrow">→</span>
                <span class="wf-step wf-done">Complete ✓</span>
            </div>
            """, unsafe_allow_html=True)

            st.success(f"**{len(st.session_state.test_cases)}** test cases generated for **{td['key']}**")

            df = pd.DataFrame(st.session_state.test_cases)
            df.columns = ["Test Case ID", "Test Case Name", "Steps", "Expected Step Description", "Actual Step Description"]

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                height=min(len(df) * 55 + 60, 600),
                column_config={
                    "Test Case ID": st.column_config.NumberColumn(width="small"),
                    "Test Case Name": st.column_config.TextColumn(width="medium"),
                    "Steps": st.column_config.TextColumn(width="large"),
                    "Expected Step Description": st.column_config.TextColumn(width="large"),
                    "Actual Step Description": st.column_config.TextColumn(width="large"),
                }
            )

            # Export
            st.markdown("---")
            col_dl, col_raw = st.columns(2)

            with col_dl:
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV (Excel-compatible)",
                    data=csv_data,
                    file_name=f"test_cases_{td['key']}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            with col_raw:
                if st.session_state.raw_llm_response:
                    with st.expander("View Raw LLM Response"):
                        st.code(st.session_state.raw_llm_response, language="json")
