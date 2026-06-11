import streamlit as st

from streamlit_qrcode_scanner import qrcode_scanner

import pandas as pd

import requests



# Set page layout to centered

st.set_page_config(page_title="FDG Cup 2026 - Gate Marshal Portal", page_icon="🛡️", layout="centered")



# Optimized CSS to cleanly frame and center the internal viewfinder crop marks

# ... lines 1-10 are imports and config ...

# THE CSS STARTS HERE AT LINE 11:
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0f172a; }
    [data-testid="stMainBlockContainer"] {
        background-color: rgba(23, 29, 41, 0.92) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px; padding: 24px !important;
        backdrop-filter: blur(15px);
        max-width: 480px !important; margin: 20px auto !important;
    }
    .branding-container { text-align: center; margin-bottom: 20px; }
    .branding-title { font-size: 30px; font-weight: 800; color: #ffffff; margin: 5px 0; }
    .branding-subtitle { font-size: 13px; font-weight: 700; color: #10b981; letter-spacing: 2px; text-transform: uppercase; }
    div.stButton > button:first-child { 
        background-color: #10b981 !important; color: white !important; font-weight: bold; 
        width: 100% !important; padding: 14px !important; border-radius: 12px !important; 
    }
    .badge-container { background: rgba(0, 0, 0, 0.4); padding: 20px; border-radius: 14px; border: 1px solid #10b981; text-align: center; }
    .badge-number { font-size: 46px; font-weight: 800; color: #facc15; }
    </style>
""", unsafe_allow_html=True) 
# THE CSS ENDS HERE AT LINE 31



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

GAS_URL = "https://script.google.com/macros/s/AKfycbx7VLxQDXeCK8JXpWzXsH-aJEIftRwOTfRBPKaaLMoVNptLrNEl6l0TBopDQ4HymrHKPQ/exec" 

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

