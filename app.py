import streamlit as st
import json
import base64
from pathlib import Path
import time
#------------------------------------------------------------------------------
# PAGE CONFIGURATION
#------------------------------------------------------------------------------
st.set_page_config(
    layout="wide",
    page_title="ناظر",
    page_icon="⚖️",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

#------------------------------------------------------------------------------
# STYLES
#------------------------------------------------------------------------------
st.markdown("""
<style>
    /* Global Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Kufi+Arabic:wght@400;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Amiri&family=Scheherazade+New:wght@700&display=swap');

    /* Global RTL settings */
    body {
        direction: rtl;
        text-align: right;
        font-family: 'Noto Kufi Arabic', sans-serif;
    }
    
    /* Header Layout */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 20px;
        margin: 0;
        width: 100%;
    }
    
    /* Logo Styling */
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 30px;
    }
    
    .logo-container.left-logos,
    .logo-container.right-logos {
        flex: 0 0 450px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .logo-container img {
        height: auto;
        width: auto;
        object-fit: contain;
    }
    
    .logo-container.left-logos img:nth-child(1) { width: 260px; } /* Najiz logo */
    .logo-container.left-logos img:nth-child(2) { width: 230px; } /* SDAIA logo */
    .logo-container.right-logos img:nth-child(1) { width: 200px; } /* Justice logo */
    .logo-container.right-logos img:nth-child(2) { width: 250px; } /* Gov logo */

    /* Simple Title Styling */
    .app-title {
        flex: 1;
        text-align: center;
    }
    
    .app-title h1 {
        font-family: 'Scheherazade New', serif;
        font-size: 5em;
        font-weight: 700;
        margin: 0;
        color: #1e40af;
    }
    
    .app-title p {
        font-family: 'Noto Kufi Arabic', sans-serif;
        font-size: 1.2em;
        color: #4a5568;
        margin: 5px 0 0;
    }

    /* ===== MAIN CONTENT SECTION ===== */
    .main-container {
        padding: 5px 10px;
        max-width: 1200px;
        margin: 0 auto;
    }

    /* ----- Input/Results Area ----- */
    .content-section {
        margin-top: 1rem;
    }
    
    .stTextArea {
        margin-top: -1rem;
    }
    
    .stTextArea textarea {
        direction: rtl;
        text-align: right;
        margin-bottom: 0;
        font-family: 'Amiri', serif !important;
        font-size: 1.2em !important;
        line-height: 1.6 !important;
        padding: 1rem !important;
    }

    .stTextArea textarea::placeholder {
        font-family: 'Amiri', serif !important;
        font-size: 1.2em !important;
        color: #6b7280 !important;
    }

    /* ----- Classification Results ----- */
    .results-section {
        margin-top: 0.5rem;
        background-color: #f8fafc;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Classification Items */
    .classification-item {
        padding: 1rem;
        border-radius: 12px;
        margin: 0.75rem 0;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
        border: 1px solid red;
    }
    
    .main-classification {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid #fbbf24;
    }
    
    .sub-classification {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border: 1px solid #60a5fa;
    }
    
    .case-type {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border: 1px solid #34d399;
    }

    /* ===== BUTTONS ===== */
    .stButton > button {
        background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);
        color: white;
        font-family: 'Noto Kufi Arabic', sans-serif;
        font-weight: 600;
        padding: 0.5rem 2rem;
        border-radius: 8px;
        border: none;
        transition: all 0.3s ease;
        width: 100%;
        position: relative;
        overflow: hidden;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
    }

    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #64748b 0%, #475569 100%);
        color: white;
    }

    .stButton > button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #475569 0%, #334155 100%);
        box-shadow: 0 4px 12px rgba(71, 85, 105, 0.3);
    }

    /* ===== HISTORY SECTION ===== */
    .entry-container {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }

    /* Rest of existing styles... */
    /* Ensure the title stays centered */
    .app-title {
        flex: 1;
        text-align: center;
        padding: 0;
        margin: 0 auto;
    }
    
    .app-title h1 {
        font-family: 'Scheherazade New', serif;
        font-size: 6em;
        font-weight: 700;
        margin: 0;
        position: relative;
        background: linear-gradient(120deg, 
            #1a365d 0%, 
            #3b82f6 25%,
            #60a5fa 50%,
            #3b82f6 75%,
            #1a365d 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        cursor: default;
        transition: all 0.3s ease;
    }
    
    .app-title h1:hover {
        animation: circleScatter 0.7s ease-in-out;
    }
    
    @keyframes circleScatter {
        0% {
            transform: scale(1) rotate(0deg);
            opacity: 1;
            filter: blur(0);
        }
        50% {
            transform: scale(1.2) rotate(5deg);
            opacity: 0.7;
            filter: blur(2px);
            letter-spacing: 0.2em;
        }
        100% {
            transform: scale(1) rotate(0deg);
            opacity: 1;
            filter: blur(0);
            letter-spacing: 0;
        }
    }

    .app-title p {
        font-family: 'Noto Kufi Arabic', sans-serif;
        font-size: 1.2em;
        color: #4a5568;
        margin: 5px 0 0;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    /* Main container */
    .main-container {
        padding: 5px 10px;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);
        color: white;
        font-family: 'Noto Kufi Arabic', sans-serif;
        font-weight: 600;
        padding: 0.5rem 2rem;
        border-radius: 8px;
        border: none;
        transition: all 0.3s ease;
        width: 100%;
        position: relative;
        overflow: hidden;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
    }

    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
    }

    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #64748b 0%, #475569 100%);
        color: white;
    }

    .stButton > button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #475569 0%, #334155 100%);
        box-shadow: 0 4px 12px rgba(71, 85, 105, 0.3);
    }

    /* Content section headers */
    .content-section h2 {
        font-family: 'Noto Kufi Arabic', sans-serif !important;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 1rem;
    }
    
    /* Text area styling */
    .stTextArea textarea {
        direction: rtl;
        text-align: right;
        margin-bottom: 0;
        font-family: 'Amiri', serif !important;
        font-size: 1.2em !important;
        line-height: 1.6 !important;
        padding: 1rem !important;
    }

    /* Add specific styling for the text area placeholder */
    .stTextArea textarea::placeholder {
        font-family: 'Amiri', serif !important;
        font-size: 1.2em !important;
        color: #6b7280 !important;
    }
    
    /* Remove spacing */
    .block-container {
        padding-top: 2rem;
        margin-top: 0;
    }
    
    .main .block-container {
        padding: 1rem 4rem;
        margin-top: 0;
    }
    
    /* Minimal header */
    header {
        padding: 1rem !important;
        margin: 0 !important;
    }
    
    /* Entry container */
    .entry-container {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .entry-container:hover {
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    .case-text {
        background-color: #f8fafc;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #e5e7eb;
        line-height: 1.6;
    }
    
    /* Results Card Container */
    .results-card {
        background: white;
        border-radius: 16px;
        margin-top: .7rem;
        padding: 1.5rem;
        box-shadow: 0 7px 10px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    /* Classification Item */
    .classification-item {
        padding: 1rem;
        border-radius: 12px;
        margin: 0.75rem 0;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
        border: 1px solid red;
    }
    
    .classification-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Main Classification */
    .main-classification {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid #fbbf24;
    }
    
    /* Sub Classification */
    .sub-classification {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border: 1px solid #60a5fa;
    }
    
    /* Case Type */
    .case-type {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border: 1px solid #34d399;
    }
    
    /* Classification Label */
    .classification-label {
        font-family: 'Noto Kufi Arabic', sans-serif;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Classification Value */
    .classification-value {
        font-family: 'Noto Kufi Arabic', sans-serif;
        color: #374151;
        font-size: 1.1em;
    }
    
    /* Icons */
    .classification-icon {
        width: 24px;
        height: 24px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.5);
        border-radius: 50%;
        margin-left: 0.5rem;
    }

    /* Delete button container */
    .delete-button-container {
        display: flex;
        align-items: start;
        padding-top: 10px;
    }
    
    .delete-button-container .stButton button {
        padding: 0 10px;
        height: 40px;
        line-height: 40px;
        background-color: transparent;
        color: #dc2626;
    }

    /* Loading animation */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }

    .loading {
        animation: pulse 1.5s ease-in-out infinite;
    }

    .stProgress .st-bo {
        background-color: #1e40af;
    }

    .stProgress .st-bp {
        background-color: #bfdbfe;
    }
</style>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const title = document.querySelector('.app-title h1');
        
        title.addEventListener('mouseleave', function() {
            this.style.animation = 'none';
            this.offsetHeight; // Trigger reflow
            this.style.animation = null;
        });
    });
</script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const title = document.querySelector('.app-title h1');
        
        title.addEventListener('animationend', function() {
            this.style.animation = '';
        });
    });
</script>

""", unsafe_allow_html=True)

#------------------------------------------------------------------------------
# UTILITY FUNCTIONS
#------------------------------------------------------------------------------
def load_history():
    """Load classification history from JSON file"""
    try:
        history_file = Path("history.json")
        if not history_file.exists():
            return []
        with open(history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_history(history):
    """Save classification history to JSON file"""
    try:
        with open('history.json', 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Failed to save history: {e}")

def get_base64_logo(filename):
    """Load and encode logo files to base64"""
    try:
        current_dir = Path(__file__).parent
        file_path = current_dir / "assets" / filename
        with open(file_path, "rb") as f:
            data = f.read()
            return base64.b64encode(data).decode()
    except Exception as e:
        st.warning(f"Could not load logo: {filename}")
        return ""

#------------------------------------------------------------------------------
# MAIN APPLICATION
#------------------------------------------------------------------------------
def main():
    # Add new session state for delete operations
    if "delete_clicked" not in st.session_state:
        st.session_state.delete_clicked = False
    if "delete_index" not in st.session_state:
        st.session_state.delete_index = None
        
    # Initialize session state
    if "history" not in st.session_state:
        st.session_state.history = load_history()
    if "case_submitted" not in st.session_state:
        st.session_state.case_submitted = False
    if "clear_input" not in st.session_state:
        st.session_state.clear_input = False
    if "loading" not in st.session_state:
        st.session_state.loading = False
    if "current_results" not in st.session_state:
        st.session_state.current_results = None
    if "progress" not in st.session_state:
        st.session_state.progress = None

    # Load logos
    logos = {
        'najiz': get_base64_logo("logo_najiz.svg"),
        'justice': get_base64_logo("justice.svg"),
        'sdaia': get_base64_logo("SDAIA.svg"),
        'gov': get_base64_logo("DigitaGov.png.svg")
    }

    # Render header
    st.markdown(f'''
        <div class="header-container">
            <div class="logo-container left-logos">
                <img src="data:image/svg+xml;base64,{logos['najiz']}" alt="Najiz Logo">
                <img src="data:image/svg+xml;base64,{logos['sdaia']}" alt="SDAIA Logo">
            </div>
            <div class="app-title">
                <h1>نـاظـر</h1>
                <p>نظام تصنيف القضايا الذكي</p>
            </div>
            <div class="logo-container right-logos">
                <img src="data:image/svg+xml;base64,{logos['justice']}" alt="Justice Logo">
                <img src="data:image/svg+xml;base64,{logos['gov']}" alt="Digital Gov Logo">
            </div>
        </div>
    ''', unsafe_allow_html=True)

    # Create main layout
    col_input, col_results = st.columns([1, 1])

    # Input section
    with col_input:
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        st.markdown("## 📝 البحث ")

        user_input = st.text_area(
            label=" ",
            height=300,
            key="rtl_input",
            placeholder="الرجاء إدخال نص الدعوى هنا للتصنيف...",
            disabled=st.session_state.case_submitted,
            value=" " if st.session_state.clear_input else None
        )
        
        if st.session_state.clear_input:
            st.session_state.clear_input = False

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⚖️ تصنيف الدعوى", type="primary", disabled=st.session_state.case_submitted):
                if user_input and not st.session_state.case_submitted:
                    st.session_state.loading = True
                    st.session_state.current_results = None  # Clear current results while loading

        with col2:
            def handle_new_case():
                st.session_state.case_submitted = False
                st.session_state.clear_input = True
                st.session_state.current_results = None

            if st.button("🔄 حالة جديدة", type="secondary", on_click=handle_new_case):
                pass

    # Results section
    with col_results:
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        st.markdown("## ⚡ نتائج التصنيف")
        
        # Show progress bar when loading
        if st.session_state.loading:
            st.markdown("""
                <div style='text-align: center; padding: 2rem;'>
                    <h3 style='color: #1e40af; font-family: "Noto Kufi Arabic", sans-serif; margin-bottom: 1rem;'>
                        جاري تحليل وتصنيف الدعوى...
                    </h3>
                </div>
            """, unsafe_allow_html=True)
            
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            # After progress completes
            m_calss_example = "أحوال شخصية"
            s_calss_example = "دعاوى الولاية"
            case_type_example = "حجر أو رفعه"

            new_entry = {
                "input": user_input,
                "main_classification": m_calss_example,
                "sub_classification": s_calss_example,
                "case_type": case_type_example,
                "id": len(st.session_state.history)
            }
            
            st.session_state.current_results = new_entry
            st.session_state.history.append(new_entry)
            save_history(st.session_state.history)
            st.session_state.case_submitted = True
            st.session_state.loading = False
            st.rerun()  # Refresh to show results

        elif st.session_state.current_results:
            latest_entry = st.session_state.current_results
            
            # Main Classification
            st.markdown(f"""
                <div class="classification-item main-classification">
                    <div class="classification-label">
                        <span class="classification-icon">📊</span>
                        التصنيف الرئيسي
                    </div>
                    <div class="classification-value">{latest_entry["main_classification"]}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Sub Classification
            st.markdown(f"""
                <div class="classification-item sub-classification">
                    <div class="classification-label">
                        <span class="classification-icon">🔍</span>
                        التصنيف الفرعي
                    </div>
                    <div class="classification-value">{latest_entry["sub_classification"]}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Case Type
            st.markdown(f"""
                <div class="classification-item case-type">
                    <div class="classification-label">
                        <span class="classification-icon">⚖️</span>
                        نوع الدعوى
                    </div>
                    <div class="classification-value">{latest_entry["case_type"]}</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="results-card" style="text-align: center; padding: 3rem;">
                    <img src="https://img.icons8.com/fluency/96/000000/search.png" style="width: 64px; margin-bottom: 1rem;">
                    <h3 style="color: #6b7280; font-family: 'Noto Kufi Arabic', sans-serif;">أدخل نص الدعوى للحصول على التصنيف</h3>
                </div>
            """, unsafe_allow_html=True)

    # History section
    with st.expander("📜 **سجل التصنيفات السابقة**"):
        if not st.session_state.history:
            st.info("لا يوجد سجل تصنيفات سابقة")
        else:
            def handle_delete(index):
                st.session_state.delete_clicked = True
                st.session_state.delete_index = index
                st.session_state.history.pop(index)
                save_history(st.session_state.history)

            # Reverse the history list for display
            for i, entry in enumerate(reversed(st.session_state.history)):
                real_index = len(st.session_state.history) - 1 - i

                # Show divider
                if i > 0:
                    st.markdown("""
                        <div class="custom-divider">
                            <span>•••</span>
                        </div>
                    """, unsafe_allow_html=True)

                with st.container():
                    col_content, col_delete = st.columns([0.95, 0.05])
                    
                    with col_content:
                        st.markdown(f"""
                        <style>
                            @import url('https://fonts.googleapis.com/css2?family=Amiri&display=swap');

                            .case-text {{
                                background: linear-gradient(135deg, #ffffff, #f9f9f9); 
                                border: 1px solid #ddd; 
                                border-radius: 10px; 
                                padding: 15px; 
                                margin-bottom: 15px;
                                font-family: 'Amiri', serif;
                                color: #444;
                                font-size: 20px;
                                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                                transition: transform 0.2s ease, box-shadow 0.2s ease;
                            }}
                            .case-text:hover {{
                                transform: scale(1.02);
                                box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
                            }}
                            .case-text strong {{
                                color: #333;
                                font-size: 20px;
                            }}
                        </style>
                        <div class="case-text">
                            <strong>البحث:</strong> {entry["input"]}
                        </div>
                        """, 
                        unsafe_allow_html=True)


                        
                    with col_delete:
                        st.markdown('<div class="delete-button-container">', unsafe_allow_html=True)
                        if st.button("🗑️", key=f"delete_{real_index}", on_click=handle_delete, args=(real_index,)):
                            pass
                        st.markdown('</div>', unsafe_allow_html=True)

                    # Continue with the classifications...
                    st.markdown(f"""
                        <div class="classification-item main-classification">
                            <div class="classification-label">
                                <span class="classification-icon">📊</span>
                                التصنيف الرئيسي
                            </div>
                            <div class="classification-value">{entry["main_classification"]}</div>
                        </div>
                    """, unsafe_allow_html=True)
                        
                    # Sub Classification
                    st.markdown(f"""
                        <div class="classification-item sub-classification">
                            <div class="classification-label">
                                <span class="classification-icon">🔍</span>
                                التصنيف الفرعي
                            </div>
                            <div class="classification-value">{entry["sub_classification"]}</div>
                        </div>
                    """, unsafe_allow_html=True)
                        
                    # Case Type
                    st.markdown(f"""
                        <div class="classification-item case-type">
                            <div class="classification-label">
                                <span class="classification-icon">⚖️</span>
                                نوع الدعوى
                            </div>
                            <div class="classification-value">{entry["case_type"]}</div>
                        </div>
                    """, unsafe_allow_html=True)

            # Clear all history button
            def handle_clear_all():
                st.session_state.history = []
                st.session_state.current_results = None
                save_history([])

            if st.button("مسح السجل بالكامل", type="secondary", on_click=handle_clear_all):
                pass

if __name__ == "__main__":
    main()