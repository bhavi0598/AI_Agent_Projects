import streamlit as st
import traceback
from tools.handshake import check_ollama
from tools.llm_engine import generate_playwright_conversion_stream

# --- UI Configuration (Phase 4: Stylize) ---
st.set_page_config(
    page_title="Selenium to Playwright Auto-Converter",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for UI Polish
st.markdown("""
    <style>
    .stTextArea textarea {
        font-family: 'Courier New', Courier, monospace;
        font-size: 14px;
    }
    .badge-local {
        background-color: #1e3a8a;
        color: #bfdbfe;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
    .badge-secure {
        background-color: #064e3b;
        color: #a7f3d0;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        margin-left: 5px;
    }
    .app-header {
        margin-bottom: -15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<h1 class="app-header">🔄 Selenium to Playwright Auto-Converter</h1>', unsafe_allow_html=True)
st.markdown('''
<span><span class="badge-local">Local LLM Architecture</span><span class="badge-secure">100% Data Privacy - Offline</span></span>
''', unsafe_allow_html=True)
st.markdown("---")

# --- State Management ---
if 'converted_code' not in st.session_state:
    st.session_state.converted_code = ""

# --- Sidebar Configuration ---
st.sidebar.title("⚙️ AI Engine Settings")
st.sidebar.markdown("This tool utilizes your local **Ollama** infrastructure.")

# Check for local models
@st.cache_data(ttl=60)
def get_model_status():
    return check_ollama()

health = get_model_status()

selected_model = None
if health['status'] == 'success':
    available_models = health.get('models', [])
    if not available_models:
        st.sidebar.error("❌ No LLM models found in your local Ollama setup.")
    else:
        st.sidebar.success("✅ Connected to Local Ollama.")
        # Attempt to default to qwen3:4b or llama3.2:1b if available
        default_index = 0
        preferred = ["qwen3:4b", "llama3.2:1b"]
        for p in preferred:
            if p in available_models:
                default_index = available_models.index(p)
                break
        
        selected_model = st.sidebar.selectbox("Select LLM Model Layer", available_models, index=default_index)

else:
    st.sidebar.error(f"❌ Failed to reach Ollama at localhost. Ensure the service is running. Details: {health.get('message', 'Unknown Error')}")


st.sidebar.markdown("---")
st.sidebar.markdown("### Conversion Rules")
st.sidebar.info("- 🎭 **Auto-waiting** enforced.\n- 🔎 **getByRole** prioritized.\n- ⏳ Asynchronous Typescript output.")

# --- Main Editor Area ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Source Script")
    source_lang = st.selectbox("Select Source Language", ["Selenium Java", "Selenium Python"])
    source_code = st.text_area("Paste Selenium Code Here:", height=400, placeholder=f"// Paste {source_lang} logic here...")

    can_convert = bool(source_code.strip()) and (selected_model is not None)
    
    submit_button = st.button("🚀 Convert to Playwright", type="primary", disabled=not can_convert, use_container_width=True)

with col2:
    st.subheader("⚡ Playwright TypeScript")
    st.selectbox("Output Framework", ["Playwright TypeScript"], disabled=True)
    
    # Render streaming text when button is pressed
    if submit_button:
        with st.spinner(f"Connecting to {selected_model}..."):
            try:
                stream_generator = generate_playwright_conversion_stream(source_lang, source_code, selected_model)
                # This explicitly gives the "ChatGPT" character-by-character typing vibe:
                result_text = st.write_stream(stream_generator)
                st.session_state.converted_code = result_text
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
                st.write(traceback.format_exc())
                
    # Display the stored text permanently without wiping after reloads
    elif st.session_state.converted_code:
        st.markdown(st.session_state.converted_code)
    else:
        st.info("Your translated Playwright script will appear here.")
        
    if st.session_state.converted_code:
        st.download_button(
            label="💾 Download Conversation Output (.md)",
            data=st.session_state.converted_code,
            file_name="converted_output.md",
            mime="text/plain",
            use_container_width=True
        )
