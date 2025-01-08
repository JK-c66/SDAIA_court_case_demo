import streamlit as st
import json
import base64
from pathlib import Path
import time
import os
import json
import time
import google.generativeai as genai
from random import randint
import datetime
import pandas as pd

NUM_KEYS = 5
#------------------------------------------------------------------------------
# PAGE CONFIGURATION
#------------------------------------------------------------------------------
st.set_page_config(
    layout="wide",
    page_title="ناظر - الرئيسية",
    page_icon="⚖️",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

#------------------------------------------------------------------------------
# STYLES AND SCRIPTS
#------------------------------------------------------------------------------
def load_css():
    """Load external CSS file"""
    css_file = Path(__file__).parent / "static" / "style.css"
    with open(css_file, 'r', encoding='utf-8') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# Load CSS and JavaScript
load_css()

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
        file_path = current_dir / "static" / filename
        with open(file_path, "rb") as f:
            data = f.read()
            return base64.b64encode(data).decode()
    except Exception as e:
        st.warning(f"Could not load logo: {filename}")
        return ""

#------------------------------------------------------------------------------
# Gemini Communication
#------------------------------------------------------------------------------

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini.

    See https://ai.google.dev/gemini-api/docs/prompting_with_media
    """
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def wait_for_files_active(files):
    """Waits for the given files to be active.

    Some files uploaded to the Gemini API need to be processed before they can be
    used as prompt inputs. The status can be seen by querying the file's "state"
    field.

    This implementation uses a simple blocking polling loop. Production code
    should probably employ a more sophisticated approach.
    """
    print("Waiting for file processing...")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
        time.sleep(10)
        file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    print("...all files ready")
    print()

@st.cache_resource(ttl=datetime.timedelta(days=2), show_spinner=False)
def initialize_gemini(key_id):
    genai.configure(api_key=os.environ[f"GEMINI_API_KEY_{key_id}"])
    # Create the model
    generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
    }

    model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
    system_instruction="according to the categories mentinoed. which category does the provided text fit in the most? what is the most appropriate subcategory? and what is the most appropriate type? you must use a category, subcategory, and type from the file only, choose from them what fits the case the most. the output should be in arabic. make the output in json format. the keys are: category, subcategory, type, explanation.",
    )

    # TODO Make these files available on the local file system
    # You may need to update the file paths
    files = [
    upload_to_gemini("classes/details.txt", mime_type="text/plain"),
    ]

    # Some files have a processing delay. Wait for them to be ready.
    wait_for_files_active(files)

    chat_session = model.start_chat(
    history=[
        {
        "role": "user",
        "parts": [
            files[0],
        ],
        },
    ]
    )
    return chat_session

#response = chat_session.send_message("INSERT_INPUT_HERE")
    

#------------------------------------------------------------------------------
# MAIN APPLICATION
#------------------------------------------------------------------------------
def main():
    # Add new session state for delete operations
    if "delete_triggered" not in st.session_state:
        st.session_state.delete_triggered = False
    if "clear_triggered" not in st.session_state:
        st.session_state.clear_triggered = False
    if "delete_clicked" not in st.session_state:
        st.session_state.delete_clicked = False
    if "delete_index" not in st.session_state:
        st.session_state.delete_index = None
    if "key_id" not in st.session_state:
        st.session_state.key_id = randint(1, NUM_KEYS)
        
    # Initialize session state
    if "history" not in st.session_state:
        st.session_state.history = load_history()
    if "case_submitted" not in st.session_state:
        st.session_state.case_submitted = False
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

    notification_icon = "✅"

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
        st.markdown("## 📝 نص الدعوى ")
        
        if "chat_session" in st.session_state:
            user_input = st.text_area(
                label=" ",
                height=300,
                key="rtl_input",
                placeholder="الرجاء إدخال النص هنا للتصنيف...",
                disabled=st.session_state.case_submitted
            )
        else:
            st.markdown("""
                <div class="loading-message">
                    <h3>يتم تهيئة النظام...</h3>
                </div>
            """, unsafe_allow_html=True)
            st.session_state.loading = True
            initialization = initialize_gemini(st.session_state.key_id)
            st.session_state.chat_session = initialization
            st.session_state.loading = False
            st.rerun()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⚖️ تصنيف الدعوى", type="primary", disabled=st.session_state.case_submitted):
                if user_input and user_input.strip():
                    st.session_state.loading = True
                    st.session_state.current_results = None

        with col2:
            def handle_new_case():
                st.session_state.case_submitted = False
                st.session_state.current_results = None
                st.session_state.loading = False
                if "rtl_input" in st.session_state:
                    st.session_state.rtl_input = ""  # Just clear the input value instead of deleting the key

            if st.button("🔄 حالة جديدة", type="secondary", on_click=handle_new_case):
                pass

    # Results section
    with col_results:
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        st.markdown("## ⚡ نتائج التصنيف")
        
        if st.session_state.loading:
            st.markdown("""
                <div class="custom-spinner-container">
                    <div class="custom-spinner"></div>
                    <div class="spinner-text">جاري تحليل وتصنيف الدعوى...</div>
                </div>
            """, unsafe_allow_html=True)
            
            with st.spinner(''):
                print("Sending message to Gemini...")
                start_time = time.time()  # Start timing
                response = st.session_state.chat_session.send_message(user_input)
                end_time = time.time()  # End timing
                duration = end_time - start_time
                print(f"Gemini API response took {duration:.2f} seconds")
                try:
                    data = json.loads(response.text)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    data = False
            
            # After progress completes
            if data == False:
                m_calss_example = "-"
                s_calss_example = "-"
                case_type_example = "-"
            else:
                m_calss_example = data['category']
                s_calss_example = data['subcategory']
                case_type_example = data['type']

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
            st.rerun()

        elif st.session_state.current_results:
            latest_entry = st.session_state.current_results
            
            st.markdown(f"""
                <div class="classification-item main-classification">
                    <div class="classification-label">
                        <span class="classification-icon">📊</span>
                        التصنيف الرئيسي
                    </div>
                    <div class="classification-value">{latest_entry["main_classification"]}</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="classification-item sub-classification">
                    <div class="classification-label">
                        <span class="classification-icon">🔍</span>
                        التصنيف الفرعي
                    </div>
                    <div class="classification-value">{latest_entry["sub_classification"]}</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="classification-item case-type">
                    <div class="classification-label">
                        <span class="classification-icon">⚖️</span>
                        نوع الدعوى
                    </div>
                    <div class="classification-value">{latest_entry["case_type"]}</div>
                </div>
            """, unsafe_allow_html=True)
            
        else:
            st.markdown("""
                <div class="results-card empty-results-card">
                    <img src="https://img.icons8.com/fluency/96/000000/search.png">
                    <h3>أدخل نص الدعوى للحصول على التصنيف</h3>
                </div>
            """, unsafe_allow_html=True)

    # History Section
    st.markdown("""
        <div class="history-title">
            <h2>📜 سجل التصنيفات</h2>
        </div>
    """, unsafe_allow_html=True)

    # Download functionality
    if st.session_state.history:
        # Convert history to DataFrame for download
        df = pd.DataFrame(st.session_state.history)
        df = df[['input', 'main_classification', 'sub_classification', 'case_type']]
        df.columns = ['نص الدعوى', 'التصنيف الرئيسي', 'التصنيف الفرعي', 'نوع الدعوى']
        
        # Create download button
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.markdown('<div class="download-section">', unsafe_allow_html=True)
        st.download_button(
            label="⬇️ تحميل سجل التصنيفات",
            data=csv,
            file_name="history.csv",
            mime="text/csv"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Display history
    if not st.session_state.history:
        st.markdown('<div class="info-message">لا يوجد سجل تصنيفات سابقة</div>', unsafe_allow_html=True)
    else:
        notification_icon = "✅"
        
        # Initialize visibility states for each history item
        for i in range(len(st.session_state.history)):
            if f"item_visible_{i}" not in st.session_state:
                st.session_state[f"item_visible_{i}"] = True
        
        def handle_delete(index):
            st.session_state[f"item_visible_{index}"] = False
            st.session_state.history.pop(index)
            save_history(st.session_state.history)
            st.toast("تم حذف العنصر بنجاح", icon=notification_icon)

        # Reverse the history list for display
        visible_count = 0
        for i, entry in enumerate(reversed(st.session_state.history)):
            real_index = len(st.session_state.history) - 1 - i
            
            if st.session_state.get(f"item_visible_{real_index}", True):
                if visible_count > 0:
                    st.markdown("""
                        <div class="custom-divider">
                            <span>•••</span>
                        </div>
                    """, unsafe_allow_html=True)
                visible_count += 1

                with st.container():
                    st.markdown('<div class="flex-95-5">', unsafe_allow_html=True)
                    col_content, col_delete = st.columns([0.95, 0.05])
                    
                    with col_content:
                        st.markdown(f"""
                        <div class="case-text">
                            <strong>البحث:</strong> {entry["input"]}
                        </div>
                        """, 
                        unsafe_allow_html=True)
                        
                    with col_delete:
                        st.markdown('<div class="delete-button-wrapper">', unsafe_allow_html=True)
                        if st.button("🗑️", key=f"delete_{real_index}", on_click=handle_delete, args=(real_index,)):
                            pass
                        st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Classifications
                    st.markdown(f"""
                        <div class="classification-item main-classification">
                            <div class="classification-label">
                                <span class="classification-icon">📊</span>
                                التصنيف الرئيسي
                            </div>
                            <div class="classification-value">{entry["main_classification"]}</div>
                        </div>
                    """, unsafe_allow_html=True)
                        
                    st.markdown(f"""
                        <div class="classification-item sub-classification">
                            <div class="classification-label">
                                <span class="classification-icon">🔍</span>
                                التصنيف الفرعي
                            </div>
                            <div class="classification-value">{entry["sub_classification"]}</div>
                        </div>
                    """, unsafe_allow_html=True)
                        
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
            if not st.session_state.get('clear_triggered'):
                st.session_state.history = []
                save_history([])
                st.toast("تم مسح السجل بالكامل", icon=notification_icon)
                st.session_state.clear_triggered = True

        st.markdown('<div class="clear-all-button-container">', unsafe_allow_html=True)
        if st.button("مسح السجل بالكامل", type="secondary", on_click=handle_clear_all):
            pass
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()