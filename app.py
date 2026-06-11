import streamlit as st
import pandas as pd
import requests
import cv2
import numpy as np
from pyzbar.pyzbar import decode

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="FDG Cup 2026 - Gate Marshal", page_icon="🛡️", layout="centered")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0f172a; }
    .badge-container { background: rgba(0, 0, 0, 0.4); padding: 20px; border-radius: 14px; border: 1px solid #10b981; text-align: center; margin-top: 10px; }
    .badge-number { font-size: 40px; font-weight: 800; color: #facc15; }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "scan_completed" not in st.session_state: st.session_state.scan_completed = False
if "result" not in st.session_state: st.session_state.result = None

# --- CONFIG ---
GAS_URL = "https://script.google.com/macros/s/AKfycbw83tC6XyAYgPnNg2nTB8NyZN0J9DvjtUAEiSNb3yS3Ze2EVz5q2qqZP8BkDbE6cM42NQ/exec"

# --- UI LOGIC ---
st.markdown("<h2 style='text-align:center; color:white;'>Gate Marshal Portal</h2>", unsafe_allow_html=True)

if not st.session_state.scan_completed:
    st.markdown("<p style='text-align:center;'>Scan QR code to check in player:</p>", unsafe_allow_html=True)
    # Native camera widget - works on all mobile devices
    img_file = st.camera_input("Scan QR")
    
    if img_file:
        with st.spinner("Processing..."):
            # Decode image
            bytes_data = img_file.getvalue()
            cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            decoded = decode(cv2_img)
            
            if decoded:
                scanned_code = decoded[0].data.decode('utf-8')
                try:
                    # Validate against your backend
                    resp = requests.get(GAS_URL, params={"mode": "verify_bypass", "pid": scanned_code}, timeout=10).json()
                    st.session_state.result = resp
                    st.session_state.scan_completed = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("No QR detected. Please try again.")

else:
    # --- RESULT VIEW ---
    res = st.session_state.result
    if res.get("status") == "SUCCESS":
        st.success("### ✓ Authorized")
        st.markdown(f"""<div class='badge-container'>
            <div class='badge-number'>BAG #{res.get('bag', 'N/A')}</div>
            <p style='color:white;'>Player: {res.get('name')}</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.error(f"### ❌ {res.get('status', 'Denied')}")
        st.write(res.get('message', 'Check credentials.'))
    
    if st.button("Scan Next Player"):
        st.session_state.scan_completed = False
        st.session_state.result = None
        st.rerun()
