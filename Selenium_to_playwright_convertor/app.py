import streamlit as st
import traceback
from tools.handshake import check_ollama
from tools.llm_engine import generate_playwright_conversion_stream

# --- UI Configuration ---
st.set_page_config(page_title="Selenium to Playwright Auto-Converter", page_icon="🔄", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS ---
st.markdown("""
<style>
.sidebar .sidebar-content { background-color: #1E2130; }
.card { background-color: white; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; color: black; }
.card h4 { color: #1e3a8a; }
.badge-local { background-color: #1e3a8a; color: #bfdbfe; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; }
.badge-secure { background-color: #064e3b; color: #a7f3d0; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; margin-left: 5px; }
</style>
""", unsafe_allow_html=True)

# --- State Management ---
if "page" not in st.session_state: st.session_state.page = "config"
if "llm_provider" not in st.session_state: st.session_state.llm_provider = "Ollama (Local)"
if "ollama_url" not in st.session_state: st.session_state.ollama_url = "http://localhost:11434"
if "groq_api_key" not in st.session_state: st.session_state.groq_api_key = ""
if "selected_model" not in st.session_state: st.session_state.selected_model = None
if "connection_status" not in st.session_state: st.session_state.connection_status = "Not Connected"
if "converted_code" not in st.session_state: st.session_state.converted_code = ""
if "ollama_models" not in st.session_state: st.session_state.ollama_models = []

# --- Sidebar Navigation ---
st.sidebar.markdown("### 🔄 Auto-Converter App")
if st.sidebar.button("⚙️ Configuration Settings", use_container_width=True):
    st.session_state.page = "config"
if st.sidebar.button("🚀 Selenium to Playwright Auto-Converter", use_container_width=True):
    st.session_state.page = "converter"

st.sidebar.markdown("---")
st.sidebar.markdown("**Connection Status**")
if st.session_state.connection_status == "Connected":
    st.sidebar.success(f"🟢 Connected connecting to {st.session_state.llm_provider}")
else:
    st.sidebar.error("🔴 Server Not Connected")

# --- Page 1: Configuration Settings ---
if st.session_state.page == "config":
    st.markdown("<div style='background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%); padding: 30px; border-radius: 10px; color: white; margin-bottom: 20px;'><h2>Configuration & Settings</h2><p>Configure your LLM provider connections</p></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='card'><h4>🧠 LLM Provider Settings</h4><p>Choose and configure your AI model provider</p><hr></div>", unsafe_allow_html=True)
    
    provider_choice = st.radio("Select LLM Provider", ["Ollama (Local)", "Groq (Cloud)"], index=0 if st.session_state.llm_provider=="Ollama (Local)" else 1)
    st.session_state.llm_provider = provider_choice
    
    if st.session_state.llm_provider == "Ollama (Local)":
        url_input = st.text_input("Ollama Base URL", value=st.session_state.ollama_url)
        if st.button("Test Ollama Connection", type="primary"):
            st.session_state.ollama_url = url_input
            with st.spinner("Testing connection..."):
                health = check_ollama(url_input)
                if health['status'] == 'success':
                    st.session_state.connection_status = "Connected"
                    st.session_state.ollama_models = health.get('models', [])
                    st.success("✅ Connected to Ollama successfully!")
                else:
                    st.session_state.connection_status = "Not Connected"
                    st.error(f"Failed to connect: {health.get('message')}")
        
        if st.session_state.connection_status == "Connected" and st.session_state.ollama_models:
            st.session_state.selected_model = st.selectbox("Select LLM Model Layer", st.session_state.ollama_models, index=0)
                    
    elif st.session_state.llm_provider == "Groq (Cloud)":
        token_input = st.text_input("Groq API Token", type="password", value=st.session_state.groq_api_key)
        if st.button("Test Groq Connection", type="primary"):
            st.session_state.groq_api_key = token_input
            if token_input:
                st.session_state.connection_status = "Connected"
                st.success("✅ Connected to Groq successfully!")
            else:
                st.session_state.connection_status = "Not Connected"
                st.error("Please provide an API key.")
        
        groq_models = ["openai/gpt-oss-120b", "llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768", "gemma2-9b-it", "gemma-7b-it"]
        st.session_state.selected_model = st.selectbox("Select LLM Model Layer", groq_models)

# --- Page 2: Auto-Converter ---
elif st.session_state.page == "converter":
    st.markdown("<h2>🔄 Selenium to Playwright Auto-Converter</h2>", unsafe_allow_html=True)
    st.markdown('''<span><span class="badge-local">Multi-LLM Architecture</span><span class="badge-secure">Strict 17-Rule Engine</span></span>''', unsafe_allow_html=True)
    st.markdown("---")
    
    if st.session_state.connection_status != "Connected" or not st.session_state.selected_model:
        st.warning("⚠️ Please establish a connection in **Configuration Settings** first.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📝 Source Script")
            source_lang = st.selectbox("Select Source Language", ["Selenium Java", "Selenium Python"])
            source_code = st.text_area("Paste Selenium Code Here:", height=400)
            can_convert = bool(source_code.strip())
            submit_button = st.button("🚀 Convert to Playwright", type="primary", disabled=not can_convert, use_container_width=True)

        with col2:
            st.subheader("⚡ Playwright TypeScript")
            st.selectbox("Output Framework", ["Playwright TypeScript"], disabled=True)
            
            output_container = st.container()
            
            if submit_button:
                with st.spinner(f"Converting via {st.session_state.selected_model} on {st.session_state.llm_provider}..."):
                    try:
                        stream_gen = generate_playwright_conversion_stream(
                            source_lang, 
                            source_code, 
                            st.session_state.selected_model,
                            provider=st.session_state.llm_provider,
                            base_url=st.session_state.ollama_url,
                            api_key=st.session_state.groq_api_key
                        )
                        st.session_state.converted_code = output_container.write_stream(stream_gen)
                    except Exception as e:
                        st.error(f"Error: {e}")
                        st.write(traceback.format_exc())
            elif st.session_state.converted_code:
                output_container.markdown(st.session_state.converted_code)
            else:
                output_container.info("Your translated Playwright script will appear here.")
