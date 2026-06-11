import streamlit as st
from streamlit_qrcode_scanner import qrcode_scanner
import pandas as pd
import requests

# Set page layout to centered
st.set_page_config(page_title="FDG Cup 2026 - Gate Marshal Portal", page_icon="🛡️", layout="centered")

# Optimized CSS to cleanly frame and center the internal viewfinder crop marks
st.markdown("""
    <style>
    /* 1. Global Background Image Sync */
    [data-testid="stAppViewContainer"] {
        background-image: url('https://lh3.googleusercontent.com/d/1Ta76TkvnUcNszyAPIsmob0oCMoMFzbTC');
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }
    
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    
    /* 2. Glassmorphic Central Wrapper Card */
    [data-testid="stMainBlockContainer"] {
        background-color: rgba(23, 29, 41, 0.92) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 24px 24px !important;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
        max-width: 480px !important;
        margin: 20px auto !important;
    }
    
    /* 3. Streamlined Compact Branding Header */
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
    
    /* 4. PERFECTLY VERTICALLY CENTERED VIEWFINDER WINDOW */
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
    
    /* Result Display Cards Styling */
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
    
    /* Elegant rounded frame styling for the incoming Player ID Image display card */
    .stImage img {
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
    }
    
    /* Interface Clutter Cleaner */
    #MainMenu, footer {visibility: hidden;}
    .block-container {padding-bottom: 0rem !important;}
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# COMPACT BRANDING HEADER BLOCK
# -------------------------------------------------------------------------
st.markdown("""
    <div class="branding-container">
        <img src="https://lh3.googleusercontent.com/d/1M8wUXNnP8dQoNhmE896WXDuwXlLQFk-G" alt="FDG Logo" style="max-width:65px; height:auto; margin-bottom:4px;">
        <div class="branding-title">FDG CUP <span style="color:#facc15;">2026</span></div>
        <div class="branding-subtitle">Gate Marshal Portal</div>
    </div>
""", unsafe_allow_html=True)
st.markdown("---")

# =========================================================================
# CONFIGURATION TARGETS
# =========================================================================
GAS_URL = "https://script.google.com/macros/s/AKfycbxME5wYE0Oj25ceIfA0gKgmh0aRTmWgeuTeHRk1Q_afsKI7BUtnNfir89VjOn9ibnAr/exec" 
SPREADSHEET_ID = "1l4khiRO2fGqZQ600xcdrVNY_sP0NvmDdPQiOa-jPfR8"

# State Management
if "active_scan_completed" not in st.session_state:
    st.session_state.active_scan_completed = False
if "display_payload" not in st.session_state:
    st.session_state.display_payload = {}

# Helper Function: Extracts raw asset IDs from Google Drive URLs to feed direct image matrices
def get_direct_drive_url(url):
    if not url or "drive.google.com" not in url:
        return url
    try:
        if "/file/d/" in url:
            file_id = url.split("/file/d/")[1].split("/")[0]
            return f"https://drive.google.com/uc?export=view&id={file_id}"
        elif "id=" in url:
            file_id = url.split("id=")[1].split("&")[0]
            return f"https://drive.google.com/uc?export=view&id={file_id}"
    except:
        pass
    return url

# Data Pipeline Engine
def fetch_sheet_data():
    csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"
    df = pd.read_csv(csv_url, header=None)
    return df.values.tolist()

# Updated to parse out backend payload configurations
def send_checkin_to_gas(scanned_pid):
    try:
        response = requests.get(GAS_URL, params={"mode": "verify_bypass", "pid": scanned_pid}, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {}

all_records = fetch_sheet_data()

# -------------------------------------------------------------------------
# INTERFACE STATE 1: TRANSACTION RESULT MONITOR
# -------------------------------------------------------------------------
if st.session_state.active_scan_completed:
    payload = st.session_state.display_payload
    
    if payload["status"] == "SUCCESS":
        st.success("### ✓ Access Authorized & Checked In!")
        st.markdown(f"""
            <div class="badge-container">
                <p style="margin:0; font-size:12px; color:#9ca3af; font-weight:700; letter-spacing:0.5px;">ASSIGNED EQUIPMENT DESIGNATION</p>
                <div class="badge-number">BAG #{payload['bag']}</div>
                <p style="margin:0; font-size:17px; color:#ffffff; font-weight:600;">Player: {payload['name']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Render the identification photo seamlessly right beneath the asset metrics card
        if payload.get("id_url"):
            st.markdown("<p style='margin:15px 0 5px 5px; font-size:12px; color:#9ca3af; font-weight:700; letter-spacing:0.5px;'>VERIFICATION PROFILE PHOTO</p>", unsafe_allow_html=True)
            direct_img_link = get_direct_drive_url(payload["id_url"])
            st.image(direct_img_link, use_container_width=True)
        
    elif payload["status"] == "DUPLICATE":
        st.error("### ⚠️ Security Alert: Already Checked In")
        st.markdown(f"""
            <div class="badge-container duplicate">
                <p style="margin:0; font-size:12px; color:#ef4444; font-weight:700; letter-spacing:0.5px;">FLAGGED RETRY ATTEMPT</p>
                <div class="badge-number" style="color:#ef4444;">DENIED</div>
                <p style="margin:0; font-size:17px; color:#ffffff; font-weight:600;">Player: {payload['name']}</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📷 Open Lens For Next Player"):
        st.session_state.active_scan_completed = False
        st.rerun()

# -------------------------------------------------------------------------
# INTERFACE STATE 2: ALIGNED ACTIVE SCANNER SCREEN
# -------------------------------------------------------------------------
else:
    st.markdown("<p style='text-align:center; color:#9ca3af; font-size:13px; margin-bottom:12px;'>Align player pass credentials inside the matrix window box below:</p>", unsafe_allow_html=True)
    
    # Render Active Lens
    scanned_raw = qrcode_scanner(key='live_marshal_camera_engine')
    
    if scanned_raw:
        try:
            parts = scanned_raw.split("-")
            row_id = int(parts[1]) 
            
            player_row = all_records[row_id] 
            player_name = f"{player_row[1]} {player_row[0]}"
            bag_number = player_row[5] 
            attendance_status = str(player_row[6]).strip()

            if attendance_status == "Checked-In":
                st.session_state.display_payload = {"status": "DUPLICATE", "name": player_name}
            else:
                # Passing the full parsed raw code (e.g. FDG26-716) makes log matching reliable
                gas_data = send_checkin_to_gas(scanned_raw)
                st.session_state.display_payload = {
                    "status": "SUCCESS", 
                    "name": player_name, 
                    "bag": bag_number,
                    "id_url": gas_data.get("idUrl", "")
                }
            
            st.session_state.active_scan_completed = True
            st.rerun()
        except Exception as e:
            st.error(f"Error parsing scan data pipeline: {e}")
