import streamlit as st
from streamlit_qrcode_scanner import qrcode_scanner
import pandas as pd
import requests

# Set page layout to centered
st.set_page_config(page_title="FDG Cup 2026 - Gate Marshal Portal", page_icon="🛡️", layout="centered")

# Advanced CSS Injector for maximum camera scaling and edge-to-edge frame layout
st.markdown("""
    <style>
    /* 1. Global Background Setup */
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
    
    /* 2. Optimized Glassmorphic Card Container */
    [data-testid="stMainBlockContainer"] {
        background-color: rgba(23, 29, 41, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 20px 20px !important; /* Tighter padding to give layout elements more breathing room */
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
        max-width: 480px !important;
        margin: 15px auto !important;
    }
    
    /* 3. Streamlined Compact Branding Header */
    .branding-container {
        text-align: center;
        margin-bottom: 10px;
    }
    .branding-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 28px;
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
        margin-top: 2px;
        text-transform: uppercase;
    }
    
    /* 4. MAXIMIZE CAMERA VIEWPORT & IFRAME WRAPPER */
    /* Forces the third-party camera element and its iframe container to grow vertically */
    iframe {
        height: 400px !important; /* Blows up the vertical footprint on mobile screens */
        width: 100% !important;
        border-radius: 16px !important;
    }
    
    div div data-testid="stMarkdownContainer" video,
    div.element-container video,
    video {
        width: 100% !important;
        height: 400px !important; /* Matches wrapper height perfectly */
        object-fit: cover !important; /* CRUCIAL: Crops outer landscape space to fill the card portrait-style */
        border-radius: 16px !important;
        border: 3px solid #10b981 !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        margin: 0 auto !important;
        display: block !important;
    }
    
    /* Transaction Result UI Enhancements */
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
    
    /* Eliminates default deployment footer margins */
    #MainMenu, footer {visibility: hidden;}
    .block-container {padding-bottom: 0rem !important;}
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# COMPACT BRANDING HEADER BLOCK
# -------------------------------------------------------------------------
st.markdown("""
    <div class="branding-container">
        <img src="https://lh3.googleusercontent.com/d/1M8wUXNnP8dQoNhmE896WXDuwXlLQFk-G" alt="FDG Logo" style="max-width:60px; height:auto; margin-bottom:2px;">
        <div class="branding-title">FDG CUP <span style="color:#facc15;">2026</span></div>
        <div class="branding-subtitle">Gate Marshal Portal</div>
    </div>
""", unsafe_allow_html=True)
st.markdown("---")

# =========================================================================
# CONFIGURATION TARGETS
# =========================================================================
GAS_URL = "https://script.google.com/macros/s/AKfycbxRFe12YikzzzbaNsFuun22bfzqfydewNaAeafqWY2lfXNlibQhqkwBMsynOiGwJIGRDw/exec" 
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
# INTERFACE STATE 2: MAXIMIZED ACTIVE SCANNER VIEWPORT
# -------------------------------------------------------------------------
else:
    st.markdown("<p style='text-align:center; color:#9ca3af; font-size:13px; margin-bottom:10px;'>Align player pass credentials inside the matrix window box below:</p>", unsafe_allow_html=True)
    
    # Active Scanning Lens
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
