import streamlit as st
from streamlit_qrcode_scanner import qrcode_scanner
import pandas as pd
import requests

# Set page layout
st.set_page_config(page_title="FDG Cup 2026 - Gate Marshal Portal", page_icon="🛡️", layout="centered")

# --- CSS STYLING ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0f172a; }
    [data-testid="stMainBlockContainer"] {
        background-color: rgba(23, 29, 41, 0.92) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px; padding: 24px !important;
        backdrop-filter: blur(15px); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
        max-width: 480px !important; margin: 20px auto !important;
    }
    .branding-container { text-align: center; margin-bottom: 20px; }
    .branding-title { font-size: 30px; font-weight: 800; color: #ffffff; }
    .branding-subtitle { font-size: 13px; font-weight: 700; color: #10b981; letter-spacing: 2px; text-transform: uppercase; }
    .badge-container { background: rgba(0, 0, 0, 0.4); padding: 20px; border-radius: 14px; border: 1px solid #10b981; text-align: center; margin-top: 10px; }
    .badge-number { font-size: 46px; font-weight: 800; color: #facc15; }
    div.stButton > button:first-child { background-color: #10b981 !important; color: white !important; font-weight: bold; width: 100% !important; padding: 14px !important; border-radius: 12px !important; }
    </style>
""", unsafe_allow_html=True)

# --- RESTORED LOGO ---
st.markdown("""
    <div class="branding-container">
        <img src="https://lh3.googleusercontent.com/d/1M8wUXNnP8dQoNhmE896WXDuwXlLQFk-G" alt="FDG Logo" style="max-width:65px; height:auto; margin-bottom:4px;">
        <div class="branding-title">FDG CUP <span style="color:#facc15;">2026</span></div>
        <div class="branding-subtitle">Gate Marshal Portal</div>
    </div>
""", unsafe_allow_html=True)
st.markdown("---")

# --- CONFIG ---
GAS_URL = "https://script.google.com/macros/s/AKfycbx7VLxQDXeCK8JXpWzXsH-aJEIftRwOTfRBPKaaLMoVNptLrNEl6l0TBopDQ4HymrHKPQ/exec" 
SPREADSHEET_ID = "1l4khiRO2fGqZQ600xcdrVNY_sP0NvmDdPQiOa-jPfR8"

# --- SESSION STATE ---
if "active_scan_completed" not in st.session_state: st.session_state.active_scan_completed = False
if "display_payload" not in st.session_state: st.session_state.display_payload = {}

# --- LOGIC ---
def fetch_sheet_data():
    try:
        csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"
        df = pd.read_csv(csv_url, header=None)
        return df.values.tolist()
    except:
        return []

if st.session_state.active_scan_completed:
    payload = st.session_state.display_payload
    if payload.get("status") == "SUCCESS":
        st.success("### ✓ Access Authorized!")
        st.markdown(f"""<div class="badge-container">
            <div class="badge-number">BAG #{payload.get('bag')}</div>
            <p style='color:white;'>Player: {payload.get('name')}</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.error("### ⚠️ Security Alert")
        st.write("Access Denied.")
        
    if st.button("📷 Open Lens For Next Player"):
        st.session_state.active_scan_completed = False
        st.rerun()

else:
    st.markdown("<p style='text-align:center; color:#9ca3af;'>Align pass in camera to scan:</p>", unsafe_allow_html=True)
    scanned_raw = qrcode_scanner(key='live_marshal_camera_engine')
    
    if scanned_raw:
        try:
            # Logic to handle scan
            all_records = fetch_sheet_data()
            parts = scanned_raw.split("-")
            row_id = int(parts[1])
            player_row = all_records[row_id]
            
            # Simple check-in simulation
            st.session_state.display_payload = {
                "status": "SUCCESS", 
                "name": f"{player_row[1]} {player_row[0]}", 
                "bag": player_row[5]
            }
            st.session_state.active_scan_completed = True
            st.rerun()
        except Exception as e:
            st.error(f"Scan error: {e}")
