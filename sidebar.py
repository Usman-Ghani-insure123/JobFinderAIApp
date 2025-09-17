from pathlib import Path
# sidebar.py  — scoped sidebar only (no global overrides)

THEME = {
    "muted": "#CBD5E1",                     # sidebar secondary text
    "sidebar_gradient": "linear-gradient(180deg, #1E1B4B 0%, #312E81 100%)"
}

def inject_sidebar_css():
    import streamlit as st
    st.markdown("""
    <style>
      /* Sidebar width only when expanded */
      section[data-testid="stSidebar"][aria-expanded="true"] {
        min-width: 390px !important;
        max-width: 370px !important;
      }

      /* Sidebar background */
      section[data-testid="stSidebar"] > div {
        background: linear-gradient(180deg, #1E1B4B 0%, #312E81 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
      }

      /* Content inside sidebar */
      #jf-sidebar { 
        color: #E5E7EB; 
        font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Helvetica Neue, Arial; 
      }
      #jf-sidebar .jf-title { font-weight: 800; font-size: 24px; margin: 6px 0 2px; }
      #jf-sidebar .jf-subtitle { color: #CBD5E1; font-size: 13.5px; margin-bottom: 10px; }

      #jf-sidebar .jf-divider {
        border: none; height: 1px; background: rgba(255,255,255,0.1);
        margin: 12px 0 16px;
      }

      #jf-sidebar .jf-section-title { font-weight: 700; margin: 8px 0 6px; }
      #jf-sidebar .jf-list, #jf-sidebar .jf-bullets { margin: 0 0 6px 18px; padding: 0; }
      #jf-sidebar .jf-list li, #jf-sidebar .jf-bullets li { margin: 6px 0; color: #E5E7EB; }
      #jf-sidebar a { color: #A5B4FC; text-decoration: none; }
      #jf-sidebar a:hover { text-decoration: underline; }
    </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    import streamlit as st
    from pathlib import Path

    LOGO_PATH = Path(__file__).parent / "assets" / "jobfinder_logo.png"

    with st.sidebar:
        # Logo
        st.image(str(LOGO_PATH), use_container_width=True)

        # Title & tagline
        st.markdown(
            """
            <div id="jf-sidebar">
              <div class="jf-title">JobFinder</div>
              <div class="jf-subtitle">Your AI assistant for smarter job applications</div>

              <hr class="jf-divider"/>

              <div class="jf-section-title">How it works</div>
              <ol class="jf-list">
                <li>📄 <b>Upload</b> your CV (PDF or DOCX)</li>
                <li>🌍 Select your <b>Preferred Country</b> and <b>City</b></li>
                <li>🤖 AI will <b>analyze your skills</b></li>
                <li>💼 Discover <b>top matching jobs</b></li>
                <li>✨ Get a <b>tailored CV & Cover Letter</b> instantly</li>
              </ol>

              <hr class="jf-divider"/>

              <div class="jf-section-title">Tips for Best Results</div>
              <ul class="jf-bullets">
                <li>📌 Use an up-to-date CV for accurate skill extraction</li>
                <li>🌆 Try different locations to explore more opportunities</li>
                <li>✏️ Review and fine-tune your CV & cover letter before sending</li>
              </ul>

              <hr class="jf-divider"/>
              <div style="font-size:12px; opacity:.9">🔒 Your CV is processed securely. Nothing is shared.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
