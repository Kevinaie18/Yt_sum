"""
YouTube Transcript Summarizer

A Streamlit app that extracts transcripts from YouTube videos and generates
structured summaries using an LLM.

Designed for deployment on Streamlit Cloud.
"""

import streamlit as st

from modules.transcript import get_transcript
from modules.summarize import summarize_transcript, check_api_configuration
from modules.export import export_summary

# Page configuration
st.set_page_config(
    page_title="YouTube Transcript Summarizer",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a polished, modern UI
st.markdown("""
<style>
    /* Import distinctive font */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Root variables */
    :root {
        --primary: #FF4B4B;
        --primary-dark: #E03E3E;
        --bg-dark: #0E1117;
        --bg-card: #1A1D24;
        --text-primary: #FAFAFA;
        --text-secondary: #8B949E;
        --border: #30363D;
        --success: #2EA043;
        --warning: #D29922;
    }
    
    /* Global styles */
    .stApp {
        font-family: 'DM Sans', sans-serif;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 1.5rem 0 2rem 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 2rem;
    }
    
    .main-header h1 {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #FF4B4B 0%, #FF8E53 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        color: var(--text-secondary);
        font-size: 1rem;
        margin: 0;
    }
    
    /* Section cards */
    .section-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .section-title {
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-secondary);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .section-title .icon {
        font-size: 1rem;
    }
    
    /* Status indicators */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .status-success {
        background: rgba(46, 160, 67, 0.15);
        color: var(--success);
        border: 1px solid rgba(46, 160, 67, 0.3);
    }
    
    .status-warning {
        background: rgba(210, 153, 34, 0.15);
        color: var(--warning);
        border: 1px solid rgba(210, 153, 34, 0.3);
    }
    
    .status-error {
        background: rgba(248, 81, 73, 0.15);
        color: #F85149;
        border: 1px solid rgba(248, 81, 73, 0.3);
    }
    
    /* Transcript display */
    .transcript-box {
        background: #0D1117;
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 1rem;
        max-height: 300px;
        overflow-y: auto;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        line-height: 1.6;
        color: var(--text-secondary);
    }
    
    /* Summary display */
    .summary-box {
        background: linear-gradient(135deg, rgba(255, 75, 75, 0.05) 0%, rgba(255, 142, 83, 0.05) 100%);
        border: 1px solid rgba(255, 75, 75, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
    }
    
    /* Button styling */
    .stButton > button {
        font-family: 'DM Sans', sans-serif;
        font-weight: 500;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        font-family: 'JetBrains Mono', monospace;
        border-radius: 8px;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-family: 'DM Sans', sans-serif;
        font-weight: 500;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: var(--text-secondary);
        font-size: 0.8rem;
        border-top: 1px solid var(--border);
        margin-top: 2rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.8rem;
        }
        .section-card {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'transcript' not in st.session_state:
    st.session_state.transcript = None
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'video_id' not in st.session_state:
    st.session_state.video_id = None
if 'transcript_message' not in st.session_state:
    st.session_state.transcript_message = None


def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎬 YouTube Transcript Summarizer</h1>
        <p>Extract insights from any YouTube video in seconds</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check API configuration
    api_configured, api_message = check_api_configuration()
    
    if not api_configured:
        st.warning(f"⚠️ {api_message}")
    
    # ===== VIDEO INPUT SECTION =====
    st.markdown("""
    <div class="section-title">
        <span class="icon">📺</span> Video Input
    </div>
    """, unsafe_allow_html=True)
    
    # URL input
    url = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="collapsed",
        help="Paste a YouTube video URL to extract its transcript"
    )
    
    # Extract button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        extract_clicked = st.button(
            "🔍 Extract Transcript",
            use_container_width=True,
            type="primary"
        )
    
    # Handle extraction
    if extract_clicked:
        if not url:
            st.error("Please enter a YouTube URL.")
        else:
            with st.spinner("Fetching transcript..."):
                success, message, transcript, video_id = get_transcript(url)
                
                st.session_state.transcript = transcript
                st.session_state.video_id = video_id
                st.session_state.transcript_message = message
                st.session_state.summary = None  # Reset summary
                
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")
    
    # ===== TRANSCRIPT SECTION =====
    if st.session_state.transcript:
        st.markdown("---")
        st.markdown("""
        <div class="section-title">
            <span class="icon">📝</span> Transcript
        </div>
        """, unsafe_allow_html=True)
        
        # Character count badge
        char_count = len(st.session_state.transcript)
        st.caption(f"📊 {char_count:,} characters")
        
        # Transcript expander
        with st.expander("📄 Show transcript", expanded=False):
            st.text_area(
                "Transcript content",
                value=st.session_state.transcript,
                height=300,
                disabled=True,
                label_visibility="collapsed"
            )
        
        # ===== SUMMARIZATION SECTION =====
        st.markdown("---")
        st.markdown("""
        <div class="section-title">
            <span class="icon">✨</span> Summary
        </div>
        """, unsafe_allow_html=True)
        
        # Summarize button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            summarize_clicked = st.button(
                "✨ Generate Summary",
                use_container_width=True,
                type="primary",
                disabled=not api_configured
            )
        
        if not api_configured:
            st.caption("⚠️ Configure your OpenAI API key to enable summarization")
        
        # Handle summarization
        if summarize_clicked:
            progress_placeholder = st.empty()
            
            def update_progress(message):
                progress_placeholder.info(f"🔄 {message}")
            
            with st.spinner("Generating summary..."):
                success, result = summarize_transcript(
                    st.session_state.transcript,
                    progress_callback=update_progress
                )
                
                progress_placeholder.empty()
                
                if success:
                    st.session_state.summary = result
                    st.success("✅ Summary generated successfully!")
                else:
                    st.error(f"❌ {result}")
        
        # Display summary
        if st.session_state.summary:
            st.markdown("---")
            
            # Summary content in a styled container
            st.markdown(st.session_state.summary)
            
            # ===== DOWNLOAD SECTION =====
            st.markdown("---")
            st.markdown("""
            <div class="section-title">
                <span class="icon">💾</span> Download
            </div>
            """, unsafe_allow_html=True)
            
            # Format selection and download
            col1, col2 = st.columns([1, 2])
            
            with col1:
                export_format = st.selectbox(
                    "Format",
                    options=["TXT", "MD", "PDF"],
                    index=1,  # Default to MD
                    label_visibility="collapsed"
                )
            
            with col2:
                # Generate file for download
                try:
                    file_bytes, filename, mime_type = export_summary(
                        st.session_state.summary,
                        export_format,
                        st.session_state.video_id
                    )
                    
                    st.download_button(
                        label=f"⬇️ Download as {export_format}",
                        data=file_bytes,
                        file_name=filename,
                        mime=mime_type,
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error generating file: {str(e)}")
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>Built with Streamlit • Powered by OpenAI</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

