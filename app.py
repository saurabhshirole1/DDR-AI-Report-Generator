# app.py
# ---------------------------------------------------------------------------
# Main Streamlit application for DDR Report Generator
# Dark themed UI with full sidebar
# Run with: streamlit run app.py --server.port 8502
# ---------------------------------------------------------------------------

import streamlit as st
import time
from pdf_parser import parse_pdf
from grok_service import generate_ddr_report
from report_generator import build_report_object, format_report_for_display
from pdf_export import export_report_to_pdf
from config import APP_NAME, MAX_FILE_SIZE_MB

# ---------------------------------------------------------------------------
# PAGE CONFIG - must be the very first Streamlit command
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="DDR Report Generator",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"   # Sidebar open by default
)

# ---------------------------------------------------------------------------
# CUSTOM CSS - Dark theme + sidebar styling
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    /* ---- GLOBAL DARK BACKGROUND ---- */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }

    /* ---- SIDEBAR DARK STYLING ---- */
    [data-testid="stSidebar"] {
        background-color: #13161f;
        border-right: 1px solid #2a2a3a;
    }

    [data-testid="stSidebar"] * {
        color: #ffffff;
    }

    /* ---- HIDE default streamlit header and footer ---- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ---- HEADER GRADIENT BOX ---- */
    .header-box {
        background: linear-gradient(135deg, #1a1f3a 0%, #0d47a1 100%);
        border-radius: 16px;
        padding: 40px 20px;
        text-align: center;
        margin-bottom: 30px;
    }

    .header-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: #ff4b4b;
        margin: 0;
        padding: 0;
    }

    .header-subtitle {
        font-size: 1rem;
        color: #aaaacc;
        margin-top: 8px;
    }

    /* ---- UPLOAD BOX LABELS ---- */
    .upload-label {
        font-size: 1.1rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 8px;
    }

    /* ---- GENERATE BUTTON ---- */
    div[data-testid="stButton"] > button {
        background: linear-gradient(90deg, #ff4b4b, #ff6b6b);
        color: white;
        font-size: 1.2rem;
        font-weight: 700;
        border: none;
        border-radius: 10px;
        padding: 18px 40px;
        width: 100%;
        letter-spacing: 0.5px;
    }

    div[data-testid="stButton"] > button:hover {
        opacity: 0.9;
    }

    /* ---- DOWNLOAD BUTTON ---- */
    div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(90deg, #1565c0, #1976d2);
        color: white;
        font-size: 1.1rem;
        font-weight: 700;
        border: none;
        border-radius: 10px;
        padding: 16px 40px;
        width: 100%;
    }

    /* ---- HINT BOX ---- */
    .hint-box {
        text-align: center;
        padding: 40px 20px;
        color: #888;
    }

    .hint-emoji {
        font-size: 2rem;
        margin-bottom: 10px;
    }

    .hint-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 8px;
    }

    .hint-subtitle {
        font-size: 0.9rem;
        color: #aaaaaa;
        line-height: 1.6;
    }

    /* ---- DIVIDER ---- */
    .divider {
        border: none;
        border-top: 1px solid #2a2a3a;
        margin: 20px 0;
    }

    /* ---- SUCCESS CARD ---- */
    .success-card {
        background-color: #1a2a1a;
        border: 1px solid #2e7d32;
        border-radius: 10px;
        padding: 12px 16px;
        margin-top: 8px;
        font-size: 0.9rem;
        color: #81c784;
    }

    /* ---- METRIC CARDS ---- */
    .metric-card {
        background-color: #1a1f2e;
        border: 1px solid #2a2a4a;
        border-radius: 10px;
        padding: 14px;
        text-align: center;
    }

    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
    }

    .metric-label {
        font-size: 0.8rem;
        color: #888888;
        margin-top: 4px;
    }

    /* ---- SIDEBAR STEP BOX ---- */
    .step-box {
        background-color: #1a1f2e;
        border-left: 3px solid #ff4b4b;
        border-radius: 6px;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-size: 0.88rem;
        color: #dddddd;
    }

    /* ---- MODEL INFO BOX ---- */
    .model-box {
        background-color: #1a1f2e;
        border: 1px solid #2a2a4a;
        border-radius: 10px;
        padding: 14px;
        font-size: 0.85rem;
        color: #cccccc;
        line-height: 1.8;
    }

    /* ---- API KEY INPUT ---- */
    .api-key-note {
        font-size: 0.78rem;
        color: #888888;
        margin-top: 4px;
    }

    /* ---- REPORT DISPLAY ---- */
    .report-container {
        background-color: #13161f;
        border: 1px solid #2a2a4a;
        border-radius: 12px;
        padding: 30px;
        margin-top: 20px;
    }

    /* ---- FILE UPLOADER DARK ---- */
    [data-testid="stFileUploader"] {
        background-color: #1a1f2e;
        border: 2px dashed #3a3a5a;
        border-radius: 12px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------

def check_file_size(uploaded_file) -> bool:
    """Check if the uploaded file is within the allowed size limit."""
    # Convert bytes to MB
    file_size_mb = uploaded_file.getbuffer().nbytes / (1024 * 1024)
    return file_size_mb <= MAX_FILE_SIZE_MB


def show_file_stats(pdf_data: dict, doc_num: int):
    """Shows stats cards after a PDF is successfully uploaded and parsed."""
    info = pdf_data["info"]
    word_count = len(pdf_data["text"].split())

    # Three stat cards in a row
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{info['pages']}</div>
            <div class="metric-label">Pages</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{info['file_size_kb']} KB</div>
            <div class="metric-label">File Size</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{word_count:,}</div>
            <div class="metric-label">Words</div>
        </div>""", unsafe_allow_html=True)

    # Small green success note
    st.markdown(f"""
    <div class="success-card">
        ✅ Document {doc_num} loaded — {info['file_name']}
    </div>""", unsafe_allow_html=True)


def reset_app():
    """Clears all data from session state and refreshes the page."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


# ---------------------------------------Due Diligence Report------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------

with st.sidebar:

    # ---- LOGO + TITLE ----
    st.markdown("""
    <div style="text-align: center; padding: 10px 0 20px 0;">
        <div style="font-size: 3rem;">📋</div>
        <div style="font-size: 1.3rem; font-weight: 800; color: #ff4b4b;">DDR Generator</div>
        <div style="font-size: 0.8rem; color: #888; margin-top: 4px;">Detailed Diagnostic Report AI</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ---- API KEY INPUT ----
    st.markdown("### 🔑 Groq API Key")

    # st.text_input with type="password" hides the key while typing
    # This lets users enter their key directly in the app
    # We store it in session_state so it persists across reruns
    api_key_input = st.text_input(
        label="Enter your Groq API Key",
        type="password",                    # Hides the key while typing
        placeholder="gsk_xxxxxxxxxxxx",
        key="api_key_input",
        help="Get your free key at console.groq.com"
    )

    # If user entered a key here, update the environment variable
    # This overrides whatever is in the .env file
    if api_key_input:
        import os
        os.environ["GROQ_API_KEY"] = api_key_input
        st.markdown("""
        <div style="font-size:0.78rem; color:#81c784; margin-top:4px;">
            ✅ API key set successfully
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="api-key-note">
            💡 Or add to <code>.env</code> file:<br>
            <code>GROQ_API_KEY=gsk_xxx</code><br>
            Get free key at <a href="https://console.groq.com" target="_blank" 
            style="color:#4fc3f7;">console.groq.com</a>
        </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ---- HOW TO USE ----
    st.markdown("### 📖 How to Use")

    # Each step is shown as a colored box
    steps = [
        ("1️⃣", "Upload the **Inspection Report** PDF"),
        ("2️⃣", "Upload the **Thermal Images Report** PDF"),
        ("3️⃣", "Click **Generate DDR Report** button"),
        ("4️⃣", "Wait **30-60 seconds** for AI analysis"),
        ("5️⃣", "Read the report on screen"),
        ("6️⃣", "Click **Download as PDF** to save"),
    ]

    for emoji, text in steps:
        st.markdown(f"""
        <div class="step-box">
            {emoji} &nbsp; {text}
        </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ---- AI MODEL INFO ----
    st.markdown("### 🤖 AI Model Info")

    st.markdown("""
    <div class="model-box">
        <b>Provider:</b> Groq AI ⚡<br>
        <b>Model:</b> llama-3.3-70b-versatile<br>
        <b>Context:</b> 128K tokens<br>
        <b>Speed:</b> ~500 tokens/sec<br>
        <b>Cost:</b> Free tier ✅<br>
        <b>Limit:</b> 14,400 req/day
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ---- REPORT SECTIONS ----
    st.markdown("### 📊 Report Sections")

    sections = [
        "Executive Summary",
        "Document 1 Overview",
        "Document 2 Overview",
        "Key Findings",
        "Comparative Analysis",
        "Risk Assessment",
        "Recommendations",
        "Conclusion"
    ]

    for i, section in enumerate(sections, 1):
        st.markdown(f"""
        <div style="font-size:0.82rem; color:#cccccc; padding: 3px 0;">
            <span style="color:#ff4b4b; font-weight:700;">{i}.</span> {section}
        </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ---- RESET BUTTON ----
    st.markdown("### ⚙️ Settings")

    if st.button("🔄 Reset App", use_container_width=True):
        reset_app()

    # Show current status in sidebar
    st.markdown("<br>", unsafe_allow_html=True)

    # Show which files are loaded
    pdf1_loaded = "pdf1_data" in st.session_state
    pdf2_loaded = "pdf2_data" in st.session_state
    report_ready = "report" in st.session_state

    st.markdown(f"""
    <div style="font-size:0.82rem; color:#888; line-height:2;">
        <b>Status:</b><br>
        {'✅' if pdf1_loaded else '⬜'} Inspection PDF<br>
        {'✅' if pdf2_loaded else '⬜'} Thermal PDF<br>
        {'✅' if report_ready else '⬜'} Report Generated
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# MAIN PAGE - HEADER
# ---------------------------------------------------------------------------

st.markdown("""
<div class="header-box">
    <div style="font-size: 2rem; margin-bottom: 8px;">🏢</div>
    <p class="header-title">DDR Report Generator</p>
    <p class="header-subtitle">
        AI-powered Detailed Diagnostic Report from Inspection + Thermal Data
    </p>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# FILE UPLOAD SECTION
# ---------------------------------------------------------------------------

pdf1_data = None
pdf2_data = None

col_left, col_right = st.columns(2)

# ---- LEFT: Inspection Report ----
with col_left:
    st.markdown('<p class="upload-label">📄 Inspection Report</p>', unsafe_allow_html=True)

    pdf1_file = st.file_uploader(
        label="inspection",
        type=["pdf"],
        key="pdf1",
        label_visibility="collapsed",
        help="Upload the Inspection Report PDF (max 10 MB)"
    )

    if pdf1_file is not None:
        if not check_file_size(pdf1_file):
            st.error(f"❌ File too large. Max {MAX_FILE_SIZE_MB} MB.")
        else:
            with st.spinner("Reading Inspection Report..."):
                try:
                    pdf1_data = parse_pdf(pdf1_file)
                    st.session_state["pdf1_data"] = pdf1_data
                    show_file_stats(pdf1_data, 1)

                    with st.expander("👁️ Preview extracted text"):
                        preview = pdf1_data["text"][:600] + "..." \
                            if len(pdf1_data["text"]) > 600 \
                            else pdf1_data["text"]
                        st.caption(preview)

                except Exception as e:
                    st.error(f"❌ Could not read PDF: {str(e)}")

# ---- RIGHT: Thermal Images Report ----
with col_right:
    st.markdown('<p class="upload-label">🌡️ Thermal Images Report</p>', unsafe_allow_html=True)

    pdf2_file = st.file_uploader(
        label="thermal",
        type=["pdf"],
        key="pdf2",
        label_visibility="collapsed",
        help="Upload the Thermal Images Report PDF (max 10 MB)"
    )

    if pdf2_file is not None:
        if not check_file_size(pdf2_file):
            st.error(f"❌ File too large. Max {MAX_FILE_SIZE_MB} MB.")
        else:
            with st.spinner("Reading Thermal Images Report..."):
                try:
                    pdf2_data = parse_pdf(pdf2_file)
                    st.session_state["pdf2_data"] = pdf2_data
                    show_file_stats(pdf2_data, 2)

                    with st.expander("👁️ Preview extracted text"):
                        preview = pdf2_data["text"][:600] + "..." \
                            if len(pdf2_data["text"]) > 600 \
                            else pdf2_data["text"]
                        st.caption(preview)

                except Exception as e:
                    st.error(f"❌ Could not read PDF: {str(e)}")

# Restore from session_state after page reruns
if pdf1_data is None and "pdf1_data" in st.session_state:
    pdf1_data = st.session_state["pdf1_data"]
if pdf2_data is None and "pdf2_data" in st.session_state:
    pdf2_data = st.session_state["pdf2_data"]


# ---------------------------------------------------------------------------
# DIVIDER + GENERATE BUTTON
# ---------------------------------------------------------------------------

st.markdown('<hr class="divider">', unsafe_allow_html=True)

both_uploaded = pdf1_data is not None and pdf2_data is not None

generate_clicked = st.button(
    "🔑 Generate DDR Report",
    disabled=not both_uploaded,
    use_container_width=True
)


# ---------------------------------------------------------------------------
# HINT BOX - shown when files not uploaded yet
# ---------------------------------------------------------------------------

if not both_uploaded:
    missing = []
    if pdf1_data is None:
        missing.append("Inspection Report")
    if pdf2_data is None:
        missing.append("Thermal Images Report")

    st.markdown(f"""
    <div class="hint-box">
        <div class="hint-emoji">👆</div>
        <div class="hint-title">Upload both PDFs and enter your API key to get started</div>
        <div class="hint-subtitle">
            The system will extract text + images, analyze with Groq AI (llama-3.3-70b-versatile),<br>
            and generate a professional DDR report with embedded images.<br><br>
            <span style="color:#ff4b4b;">Still needed: {' + '.join(missing)}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# REPORT GENERATION
# ---------------------------------------------------------------------------

if generate_clicked and both_uploaded:
    st.markdown("---")
    progress = st.progress(0)
    status = st.empty()

    try:
        status.markdown("**📤 Sending documents to Groq AI...**")
        progress.progress(15)
        time.sleep(0.4)

        status.markdown("**🤖 AI is analyzing your documents... (this takes 30-60 seconds)**")
        progress.progress(35)

        # Main AI call - sends PDF content to Groq and gets report back
        raw_report = generate_ddr_report(pdf1_data, pdf2_data)

        progress.progress(70)
        status.markdown("**📝 Structuring the report...**")
        time.sleep(0.3)

        # Build structured report object with metadata
        report = build_report_object(
            raw_report,
            pdf1_data["info"],
            pdf2_data["info"]
        )

        # Save to session_state so it survives page reruns
        st.session_state["report"] = report

        progress.progress(95)
        status.markdown("**✅ Finalizing...**")
        time.sleep(0.3)

        progress.progress(100)
        time.sleep(0.3)

        progress.empty()
        status.empty()

        st.success("🎉 DDR Report generated successfully! Scroll down to read and download.")
        st.rerun()   # Rerun to refresh the sidebar status indicators

    except Exception as e:
        progress.empty()
        status.empty()
        st.error(f"❌ Error: {str(e)}")
        st.info("💡 Make sure your Groq API key is entered in the sidebar or .env file.")


# ---------------------------------------------------------------------------
# DISPLAY REPORT
# ---------------------------------------------------------------------------

if "report" in st.session_state:
    report = st.session_state["report"]

    st.markdown("---")
    st.markdown("## 📊 Your DDR Report")

    # Download button at the top
    try:
        with st.spinner("Preparing PDF for download..."):
            pdf_bytes = export_report_to_pdf(report)

        st.download_button(
            label="⬇️ Download DDR Report as PDF",
            data=pdf_bytes,
            file_name="DDR_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"❌ Could not create PDF: {str(e)}")

    # Report content display
    st.markdown('<div class="report-container">', unsafe_allow_html=True)
    display_text = format_report_for_display(report)
    st.markdown(display_text)
    st.markdown('</div>', unsafe_allow_html=True)

    # Documents summary at bottom
    st.markdown("---")
    st.markdown("### 📎 Documents Analyzed")
    dc1, dc2 = st.columns(2)

    with dc1:
        d1 = report["document_1"]
        st.markdown(f"""
        <div class="metric-card" style="text-align:left; padding:16px;">
            <b>📄 Inspection Report</b><br>
            <small style="color:#aaa">{d1['name']}</small><br><br>
            Pages: <b>{d1['pages']}</b> &nbsp;|&nbsp; Size: <b>{d1['size_kb']} KB</b>
        </div>""", unsafe_allow_html=True)

    with dc2:
        d2 = report["document_2"]
        st.markdown(f"""
        <div class="metric-card" style="text-align:left; padding:16px;">
            <b>🌡️ Thermal Images Report</b><br>
            <small style="color:#aaa">{d2['name']}</small><br><br>
            Pages: <b>{d2['pages']}</b> &nbsp;|&nbsp; Size: <b>{d2['size_kb']} KB</b>
        </div>""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------------

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<p style='text-align:center; color:#333; font-size:0.8rem;'>
    DDR Report Generator &nbsp;|&nbsp;
    Powered by Groq AI (llama-3.3-70b-versatile) &nbsp;|&nbsp;
    Built with Streamlit
</p>
""", unsafe_allow_html=True)