import streamlit as st
from streamlit_qrcode_scanner import qrcode_scanner
import pandas as pd
import requests

# Set page layout to centered
st.set_page_config(page_title="FDG Cup 2026 - Gate Marshal Portal", page_icon="🛡️", layout="centered")

# SAFE CSS INJECTION: Removed the 'f' prefix entirely to prevent bracket-parsing crashes
st.markdown("""
    <style>
    /* 1. Global Background Setup */
    [data-testid="stAppViewContainer"] {
        background-color: #0f172a;
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }
    
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    
    /* 2. Glassmorphic Main Card Layout Container */
    [data-testid="stMainBlockContainer"] {
        background-color: rgba(23, 29, 41, 0.94) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 24px 24px !important;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
        max-width: 480px !important;
        margin: 20px auto !important;
    }
    
    /* 3. Typography and Identity Styles */
    .branding-container {
        text-align: center;
        margin-bottom: 10px;
    }
    .branding-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 30px;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.1;
        margin: 2px 0;
        letter-spacing: -0.5px;
    }
    .branding-subtitle {
        font-family: 'Urbanist', sans-serif;
        font-size: 13px;
        font-weight: 700;
        color: #10b981;
        letter-spacing: 2px;
        margin-top: 4px;
        text-transform: uppercase;
    }
    
    /* 4. Perfectly Formatted Lens Frame Viewfinder Box */
    div[data-testid="stCustomComponentV1"] {
        width: 100% !important;
        height: 290px !important; 
        border-radius: 20px !important;
        border: 3px solid #10b981 !important; 
        overflow: hidden !important; 
        position: relative !important;
        background-color: #111827;
        box-shadow: 0 12px 28px rgba(0,0,0,0.5);
        margin-bottom: 15px !important;
    }
    
    div[data-testid="stCustomComponentV1"] iframe {
        width: 100% !important;
        height: 350px !important; 
        position: absolute !important;
        top: -12px !important; 
        left: 0 !important;
        border: none !important;
    }
    
    /* Action Controls Styling Interface */
    div.stButton > button:first-child { 
        background-color: #10b981 !important; 
        color: white !important; 
        font-weight: bold; 
        width: 100% !important; 
        padding: 14px !important;
        border-radius: 12px !important;
        border: none !important;
        font-size: 15px;
    }
    .badge-container { 
        background: rgba(0, 0, 0, 0.4); 
        padding: 20px; 
        border-radius: 14px; 
        border: 1px solid #10b981; 
        text-align: center;
        margin-top: 10px;
    }
    .badge-container.duplicate { border: 1px solid #ef4444; }
    .badge-number { font-size: 46px; font-weight: 800; color: #facc15; margin: 4px 0; }
    
    /* Verification Image Border Processing */
    .stImage img {
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
    }
    
    /* App Canvas Cleaners */
    #MainMenu, footer {visibility: hidden;}
    .block-container {padding-bottom: 0rem !important;}
    </style>
""", unsafe_allow_html=True)

# Application Identity Headers
st.markdown("""
    <div class="branding-container">
        <div class="branding-title">FDG CUP <span style="color:#facc15;">2026</span></div>
        <div class="branding-subtitle">Gate Marshal Portal</div>
    </div>
""", unsafe_allow_html=True)
st.markdown("---")

# =========================================================================
# SYSTEM INFRASTRUCTURE TARGET CONFIGURATIONS
# =========================================================================
GAS_URL = "https://script.google.com/macros/s/AKfycbz2uVYD8eYngcGTI_IrY5XyxYZnAvGbErtFm0gRfgT1ywF_lpwFrPWl1IJreyJwuCuDIw/exec" 
SPREADSHEET_ID = "1l4khiRO2fGqZQ600xcdrVNY_sP0NvmDdPQiOa-jPfR8"

# Runtime State Controllers
if "active_scan_completed" not in st.session_state:
    st.session_state.active_scan_completed = False
if "display_payload" not in st.session_state:
    st.session_state.display_payload = {}

def get_direct_drive_url(url):
    """Converts a standard sharing link into an open, cookie-free asset endpoint."""
    if not url or "drive.google.com" not in url:
        return url
    try:
        if "/file/d/" in url:
            file_id = url.split("/file/d/")[1].split("/")[0]
        elif "id=" in url:
            file_id = url.split("id=")[1].split("&")[0]
        else:
            return url
        # Using Google's high-speed open delivery CDN subdomain
        return "https://lh3.googleusercontent.com/d/" + str(file_id)
    except Exception:
        return url

def fetch_sheet_data():
    """Streams live matrix rows straight from the registration database."""
    csv_url = "https://docs.google.com/spreadsheets/d/" + SPREADSHEET_ID + "/export?format=csv&gid=0"
    df = pd.read_csv(csv_url, header=None)
    return df.values.tolist()

def send_checkin_to_gas(scanned_pid):
    """Pushes time-stamped check-in status entries to the deployment webhook."""
    try:
        response = requests.get(GAS_URL, params={"mode": "verify_bypass", "pid": scanned_pid}, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return {}

# Cache-load dataset instance
all_records = fetch_sheet_data()

# -------------------------------------------------------------------------
# PORTAL INTERFACE STATE 1: DISPLAY SCAN RESULT TRANSACTION
# -------------------------------------------------------------------------
if st.session_state.active_scan_completed:
    payload = st.session_state.display_payload
    
    if payload["status"] == "SUCCESS":
        st.success("### ✓ Access Authorized & Checked In!")
        
        # Safe String Token Replacement to protect against syntax errors
        success_template = """
        <div class="badge-container">
            <p style="margin:0; font-size:12px; color:#9ca3af; font-weight:700; letter-spacing:0.5px;">ASSIGNED EQUIPMENT DESIGNATION</p>
            <div class="badge-number">
