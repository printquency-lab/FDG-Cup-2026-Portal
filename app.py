import streamlit as st
from streamlit_qrcode_scanner import qrcode_scanner
import pandas as pd
import requests

# Set page layout to match premium tournament aesthetic
st.set_page_config(page_title="FDG Cup 2026 - Marshal Gate Desk", page_icon="🛡️", layout="centered")

# Custom CSS for UI consistency (Glassmorphism + Gold/Emerald Accents)
st.markdown("""
    <style>
    .main { background-color: #111827; }
    h1 { font-family: 'Space Grotesk', sans-serif; color: #ffffff; text-align: center; font-weight: 700; }
    div.stButton > button:first-child { 
        background-color: #10b981 !important; 
        color: white !important; 
        font-weight: bold; 
        width: 100% !important; 
        padding: 14px !important;
        border-radius: 12px !important;
        border: none !important;
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
    .badge-container.duplicate {
        border: 1px solid #ef4444;
    }
    .badge-number { font-size: 46px; font-weight: 800; color: #facc15; margin: 8px 0; letter-spacing: -1px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🏆 FDG CUP <span style='color:#facc15;'>2026</span><br><span style='font-size:16px; color:#10b981; letter-spacing:1px; vertical-align:middle;'>GATE MARSHAL PORTAL</span></h1>", unsafe_allow_html=True)
st.markdown("---")

# =========================================================================
# CONFIGURATION TARGETS (Update these with your fresh 2026 deployment IDs)
# =========================================================================
GAS_URL = "https://script.google.com/macros/s/AKfycbxRFe12YikzzzbaNsFuun22bfzqfydewNaAeafqWY2lfXNlibQhqkwBMsynOiGwJIGRDw/exec" 
SPREADSHEET_ID = "1l4khiRO2fGqZQ600xcdrVNY_sP0NvmDdPQiOa-jPfR8"

# State Management (Fixed the session_state assignment bug here)
if "active_scan_completed" not in st.session_state:
    st.session_state.active_scan_completed = False
if "display_payload" not in st.session_state:
    st.session_state.display_payload = {}

# Backend Communication Engine
def fetch_sheet_data():
    csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"
    df = pd.read_csv(csv_url, header=None)
    return df.values.tolist()

def send_checkin_to_gas(row_id):
    try:
        # Handshake transmission out to Apps Script routing infrastructure
        requests.get(GAS_URL, params={"mode": "verify_bypass", "pid": row_id}, timeout=10)
    except:
        pass

# Initialize Data Cache Fetch
all_records = fetch_sheet_data()

# -------------------------------------------------------------------------
# RENDER SCREEN 1: TRANSACTION RESULT MONITOR
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
# RENDER SCREEN 2: ACTIVE HARDWARE SCANNING VIEWPORT
# -------------------------------------------------------------------------
else:
    st.markdown("<p style='text-align:center; color:#9ca3af; font-size:15px;'>Align player credentials token inside camera matrix frame window</p>", unsafe_allow_html=True)
    scanned_raw = qrcode_scanner(key='live_marshal_camera_engine')
    
    if scanned_raw:
        try:
            # Parse row tracking sequence from alphanumeric token string (e.g., "FDG26-14")
            parts = scanned_raw.split("-")
            row_id = int(parts[1]) 
            
            # Cross-reference row index direct to target Google Sheet array block
            player_row = all_records[row_id] 
            
            # Map standard spreadsheet columns indices safely
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
