import streamlit as st
from streamlit_qrcode_scanner import qrcode_scanner
import pandas as pd
import requests

# Set page layout to centered
st.set_page_config(page_title="FDG Cup 2026 - Gate Marshal Portal", page_icon="🛡️", layout="centered")

# Advanced CSS Injector for expanded camera view and exact header replication
st.markdown("""
    <style>
    /* Main container background tuning */
    .main { background-color: #111827; }
    
    /* Branding Header Blocks */
    .branding-container {
        text-align: center;
        margin-bottom: 25px;
        padding-top: 10px;
    }
    .branding-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 42px;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.1;
        margin: 5px 0;
        letter-spacing: -1px;
    }
    .branding-subtitle {
        font-family: 'Urbanist', sans-serif;
        font-size: 18px;
        font-weight: 700;
        color: #10b981; /* Precise signature emerald green from your design */
        letter-spacing: 2px;
        margin-top: 12px;
        text-transform: uppercase;
    }
    
    /* FORCE CAMERA VIEWPORT EXPANSION */
    /* Targets the embedded video elements inside the third-party scanner component */
    div div data-testid="stMarkdownContainer" video,
    div.element-container video,
    video {
        width: 100% !important;
        max-width: 580px !important; /* Forces the camera preview box to be much larger */
        height: auto !important;
        border-radius: 20px !important;
        border: 4px solid #10b981 !important; /* Highlights scanner frame window with theme color */
        box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        margin: 0 auto !important;
        display: block !important;
    }
    
    /* Transaction Result Display Styling */
    div.stButton > button:first-child { 
        background-color: #10b981 !important; 
        color: white !important; 
        font-weight: bold; 
        width: 100% !important; 
        padding: 16px !important;
        border-radius: 12px !important;
        border: none !important;
        font-size: 16px;
        transition: all 0.2s ease;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-1px);
        filter: brightness(1.1);
    }
    .badge-container { 
        background: rgba(31, 41, 55, 0.6); 
        padding: 24px; 
        border-radius: 16px; 
        border: 1px solid #10b981; 
        text-align: center; 
        margin-top: 15px;
        backdrop-filter: blur(12px);
    }
    .badge-container.duplicate { border: 1px solid #ef4444; }
    .badge-number { font-size: 48px; font-weight: 800; color: #facc15; margin: 6px 0; }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# NEW REPLICATED BRANDING HEADER BLOCK
# -------------------------------------------------------------------------
st.markdown("""
    <div class="branding-container">
        <img src="https://lh3.googleusercontent.com/d/1M8wUXNnP8dQoNhmE896WXDuwXlLQFk-G" alt="FDG Logo" style="max-width:130px; height:auto; margin-bottom:5px;">
        <div class="branding-title">FDG CUP <span style="color:#facc15;">2026</span></div>
        <div class="branding-subtitle">Gate Marshal Portal</div>
    </div>
""", unsafe_allow_html=True)
st.markdown("---")

# =========================================================================
# CONFIGURATION TARGETS
# =========================================================================
GAS_URL = "https://script.google.com/macros/s/AKfycbxWasvts-sTpJijDUC5K0KKdLuclSt89j3YxE5qO8g4jyYqq7sd4i9lduGpcfrd9AO20w/exec" 
SPREADSHEET_ID = "1l4khiRO2fGqZQ600xcdrVNY_sP0NvmDdPQiOa-jPfR8"

# State Management
if "active_scan_completed" not in st.session_state:
    st.session_state.active_scan_completed = False
if "display_payload" not in st.session_state:
    st.session_state.display_payload = {}

# Data Pipeline Engine
def fetch_sheet_data():
    csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"
    df = pd.read_csv(csv_url, header=None)
    return df.values.tolist()

def send_checkin_to_gas(row_id):
    try:
        requests.get(GAS_URL, params={"mode": "verify_bypass", "pid": row_id}, timeout=10)
    except:
        pass

all_records = fetch_sheet_data()

# -------------------------------------------------------------------------
# INTERFACE STATE 1: SCREEN ENTRY MONITOR (SUCCESS / DUPLICATE)
# -------------------------------------------------------------------------
if st.session_state.active_scan_completed:
    payload = st.session_state.display_payload
    
    if payload["status"] == "SUCCESS":
        st.success("### ✓ Access Authorized & Checked In!")
        st.markdown(f"""
            <div class="badge-container">
                <p style="margin:0; font-size:13px; color:#9ca3af; font-weight:700; letter-spacing:0.5px;">ASSIGNED EQUIPMENT DESIGNATION</p>
                <div class="badge-number">BAG #{payload['bag']}</div>
                <p style="margin:0; font-size:18px; color:#ffffff; font-weight:600;">Player: {payload['name']}</p>
            </div>
        """, unsafe_allow_html=True)
        
    elif payload["status"] == "DUPLICATE":
        st.error("### ⚠️ Security Alert: Already Checked In")
        st.markdown(f"""
            <div class="badge-container duplicate">
                <p style="margin:0; font-size:13px; color:#ef4444; font-weight:700; letter-spacing:0.5px;">FLAGGED RETRY ATTEMPT</p>
                <div class="badge-number" style="color:#ef4444;">DENIED</div>
                <p style="margin:0; font-size:18px; color:#ffffff; font-weight:600;">Player: {payload['name']}</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📷 Open Lens For Next Player"):
        st.session_state.active_scan_completed = False
        st.rerun()

# -------------------------------------------------------------------------
# INTERFACE STATE 2: ENLARGED ACTIVE SCANNER MATRIX SCREEN
# -------------------------------------------------------------------------
else:
    st.markdown("<p style='text-align:center; color:#9ca3af; font-size:14px; margin-bottom:15px;'>Align player pass credentials inside the matrix window box below:</p>", unsafe_allow_html=True)
    
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
                send_checkin_to_gas(row_id)
                st.session_state.display_payload = {
                    "status": "SUCCESS", 
                    "name": player_name, 
                    "bag": bag_number
                }
            
            st.session_state.active_scan_completed = True
            st.rerun()
        except Exception as e:
            st.error(f"Error parsing scan data pipeline: {e}")
