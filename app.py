import streamlit as st
import pandas as pd
import requests
import cv2
import numpy as np
from pyzbar.pyzbar import decode

# --- PAGE CONFIG ---
st.set_page_config(page_title="FDG Cup 2026 - Gate Marshal Portal", page_icon="🛡️", layout="centered")

# --- FULL CSS (RESTORED) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0f172a; }
    [data-testid="stMainBlockContainer"] {
        background-color: rgba(23, 29, 41, 0.92) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px; padding: 24px !important;
        backdrop-filter: blur(15px); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
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

# --- CONFIG & DATA FETCHING ---
GAS_URL = "https://script.google.com/macros/s/AKfycbw83tC6XyAYgPnNg2nTB8NyZN0J9DvjtUAEiSNb3yS3Ze2EVz5q2qqZP8BkDbE6cM42NQ/exec" 
SPREADSHEET_ID = "1l4khiRO2fGqZQ600xcdrVNY_sP0NvmDdPQiOa-jPfR8"

@st.cache_data(ttl=600)
def fetch_sheet_data():
    csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"
    df = pd.read_csv(csv_url, header=None)
    return df.values.tolist()

# --- STATE ---
if "scan_completed" not in st.session_state: st.session_state.scan_completed = False
if "payload" not in st.session_state: st.session_state.payload = None

# --- APP LOGIC ---
if not st.session_state.scan_completed:
    st.markdown("<p style='text-align:center; color:#9ca3af;'>Align pass in camera to scan:</p>", unsafe_allow_html=True)
    
    img_file = st.camera_input("Scanner")
    
    if img_file:
        with st.spinner("Decoding..."):
            # Process image natively
            bytes_data = img_file.getvalue()
            cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            decoded = decode(cv2_img)
            
            if decoded:
                scanned_code = decoded[0].data.decode('utf-8')
                
                # Logic: Find player in sheet
                all_records = fetch_sheet_data()
                # Assuming your logic: code corresponds to index or search
                # Example: checking status via your GAS_URL
                try:
                    resp = requests.get(GAS_URL, params={"mode": "verify_bypass", "pid": scanned_code}, timeout=10).json()
                    st.session_state.payload = resp
                    st.session_state.scan_completed = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("No QR code detected.")

else:
    # --- RESULT UI ---
    p = st.session_state.payload
    st.success("### ✓ Checked In")
    st.markdown(f"""
        <div class="badge-container">
            <div class="badge-number">BAG #{p.get('bag', 'N/A')}</div>
            <p style='color:white;'>Player: {p.get('name', 'Unknown')}</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("📷 Scan Next Player"):
        st.session_state.scan_completed = False
        st.rerun()
