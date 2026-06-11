import streamlit as st
from streamlit_qrcode_scanner import qrcode_scanner
import pandas as pd
import requests

# Set page layout to centered
st.set_page_config(page_title="FDG Cup 2026 - Gate Marshal Portal", page_icon="🛡️", layout="centered")

# Optimized CSS to cleanly frame layouts and center viewport elements
st.markdown("""
    <style>
    /* 1. Global Dark Mode Clean Canvas */
    [data-testid="stAppViewContainer"] {
        background-color: #0f172a;
    }
    
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    
    /* 2. Glassmorphic Central Content Wrapper Card */
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
    
    /* 3. Branding Titles */
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
    
    /* 4. Center-Aligned Viewfinder Container Matrix */
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
    
    /* Reset Buttons styling */
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
    
    /* Clean Photo Frame Card layouts */
    .stImage img {
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
    }
    
    /* System Clutter Cleaner */
    #MainMenu, footer {visibility: hidden;}
    .block-container {padding-bottom: 0rem !important;}
    </style>
""", unsafe_allow_html=True)

# Branding Layout Header Block
st.markdown("""
    <div class="branding-container">
        <div class="branding-title">FDG CUP <span style="color:#facc15;">2026</span></div>
        <div class="branding-subtitle">Gate Marshal Portal</div>
    </div>
""", unsafe_allow_html=True)
st.markdown("---")

# =========================================================================
# SYSTEM CONFIGURATION TARGETS
# =========================================================================
GAS_URL = "https://script.google.com/macros/s/AKfycbz2uVYD8eYngcGTI_IrY5XyxYZnAvGbErtFm0gRfgT1ywF_lpwFrPWl1IJreyJwuCuDIw/exec" 
SPREADSHEET_ID = "1l4khiRO2fGqZQ600xcdrVNY_sP0NvmDdPQiOa-jPfR8"

# Session State Persistence Engines
if "active_scan_completed" not in st.session_state:
    st.session_state.active_scan_completed = False
if "display_payload" not in st.session_state:
    st.session_state.display_payload = {}

def get_direct_drive_url(url):
    """Converts a standard Google Drive share link into a backend streamable URL link."""
    if not url or "drive.google.com" not in url:
        return url
    try:
        if "/file/d/" in url:
            file_id = url.split("/file/d/")[1].split("/")[0]
        elif "id=" in url:
            file_id = url.split("id=")[1].split("&")[0]
        else:
            return url
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    except Exception:
        return url

def fetch_sheet_data():
    """Fetches real-time student/player records directly from the target database."""
    csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"
    df = pd.read_csv(csv_url, header=None)
    return df.values.tolist()

def send_checkin_to_gas(scanned_pid):
    """Hits the Apps Script deployment webhook and saves check-in times."""
    try:
        response = requests.get(GAS_URL, params={"mode": "verify_bypass", "pid": scanned_pid}, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return {}

# Load working database copy
all_records = fetch_sheet_data()

# -------------------------------------------------------------------------
# INTERFACE STATE 1: TRANSACTION RESULT LOOKUP LAYOUT
# -------------------------------------------------------------------------
if st.session_state.active_scan_completed:
    payload = st.session_state.display_payload
    
    if payload["status"] == "SUCCESS":
        st.success("### ✓ Access Authorized & Checked In!")
        
        success_badge = """
        <div class="badge-container">
            <p style="margin:0; font-size:12px; color:#9ca3af; font-weight:700; letter-spacing:0.5px;">ASSIGNED EQUIPMENT DESIGNATION</p>
            <div class="badge-number">BAG #{bag}</div>
            <p style="margin:0; font-size:17px; color:#ffffff; font-weight:600;">Player: {name}</p>
        </div>
        """.format(bag=payload.get('bag', 'N/A'), name=payload.get('name', 'Unknown Player'))
        st.markdown(success_badge, unsafe_allow_html=True)
        
        # Profile Photo Streaming Component
        if payload.get("id_url") and str(payload["id_url"]).strip():
            st.markdown("<p style='margin:15px 0 5px 5px; font-size:12px; color:#9ca3af; font-weight:700; letter-spacing:0.5px;'>VERIFICATION PROFILE PHOTO</p>", unsafe_allow_html=True)
            direct_img_link = get_direct_drive_url(payload["id_url"])
            
            try:
                # Backend-side content stream bypasses browser cross-origin policy blockades entirely
                img_response = requests.get(direct_img_link, timeout=8)
                if img_response.status_code == 200 and "image" in img_response.headers.get("Content-Type", ""):
                    st.image(img_response.content, use_container_width=True)
                else:
                    st.warning("⚠️ Photo found, but Google Drive rejected the external image data request.")
            except Exception as e:
                st.error(f"Failed to stream target verification asset: {e}")
        else:
            st.info("ℹ️ Account verified. No attached photo found.")
        
    elif payload["status"] == "DUPLICATE":
        st.error("### ⚠️ Security Alert: Already Checked In")
        
        duplicate_badge = """
        <div class="badge-container duplicate">
            <p style="margin:0; font-size:12px; color:#ef4444; font-weight:700; letter-spacing:0.5px;">FLAGGED RETRY ATTEMPT</p>
            <div class="badge-number" style="color:#ef4444;">DENIED</div>
            <p style="margin:0; font-size:17px; color:#ffffff; font-weight:600;">Player: {name}</p>
        </div>
        """.format(name=payload.get('name', 'Unknown'))
        st.markdown(duplicate_badge, unsafe_allow_html=True)
        
    elif payload["status"] == "NOT_FOUND":
        st.error("### ❌ Access Denied: Invalid Credentials")
        st.warning(f"The scanned credential identifier **{payload.get('scanned_id')}** does not exist within the active registration sheet database.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📷 Open Lens For Next Player"):
        st.session_state.active_scan_completed = False
        st.rerun()

# -------------------------------------------------------------------------
# INTERFACE STATE 2: LIVE VIEWFINDER SCREEN
# -------------------------------------------------------------------------
else:
    st.markdown("<p style='text-align:center; color:#9ca3af; font-size:13px; margin-bottom:12px;'>Align player pass credentials inside the viewfinder window box:</p>", unsafe_allow_html=True)
    
    # Fire up active scanner hardware lens
    scanned_raw = qrcode_scanner(key='live_marshal_camera_engine')
    
    if scanned_raw:
        scanned_raw_clean = str(scanned_raw).strip()
        
        # DYNAMIC RE-ENGINEERED DATABASE SEARCH: Looks across rows to find exact string match
        player_row = None
        for row in all_records:
            if any(str(cell).strip() == scanned_raw_clean for cell in row):
                player_row = row
                break
        
        # CRASH PROTECTED ROUTING PIPELINE
        if player_row is not None:
            try:
                player_name = "{0} {1}".format(player_row[1], player_row[0])
                bag_number = player_row[5] 
                attendance_status = str(player_row[6]).strip()

                if attendance_status == "Checked-In":
                    st.session_state.display_payload = {"status": "DUPLICATE", "name": player_name}
                else:
                    gas_data = send_checkin_to_gas(scanned_raw_clean)
                    st.session_state.display_payload = {
                        "status": "SUCCESS", 
                        "name": player_name, 
                        "bag": bag_number,
                        "id_url": gas_data.get("idUrl", "")
                    }
            except Exception as e:
                st.session_state.display_payload = {"status": "NOT_FOUND", "scanned_id": scanned_raw_clean}
        else:
            # Fallback instead of crash if random QR code gets read by camera
            st.session_state.display_payload = {"status": "NOT_FOUND", "scanned_id": scanned_raw_clean}
            
        st.session_state.active_scan_completed = True
        st.rerun()
