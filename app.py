import streamlit as st
from streamlit_qrcode_scanner import qrcode_scanner
import pandas as pd
import requests

# Set page layout to centered
st.set_page_config(page_title="FDG Cup 2026 - Gate Marshal Portal", page_icon="🛡️", layout="centered")

# Advanced CSS Injector for background, glass card, maximized high-res video, and a custom view finder overlay
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
    
    /* 2. Glassmorphic Central Wrapper Card (Matches Registration Portal) */
    [data-testid="stMainBlockContainer"] {
        background-color: rgba(31, 41, 55, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 24px 32px !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
        max-width: 520px !important;
        margin: 30px auto !important;
    }
    
    /* 3. Streamlined Compact Branding Header */
    .branding-container {
        text-align: center;
        margin-bottom: 15px;
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
    
    /* 4. MAXIMIZE CAMERA & CREATE CUSTOM OVERLAY */
    /* Root container for the scanner component */
    div[data-testid="stCustomComponentV1"] {
        width: 100% !important;
        height: 380px !important; /* Locked window height on mobile screen */
        border-radius: 20px !important;
        border: 3px solid #10b981 !important; /* Emerald Border Frame */
        overflow: hidden !important;
        position: relative !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.6);
        background-color: #000000 !important;
        margin-bottom: 20px !important;
    }
    
    /* Force high-res, full-sized video feed inside the container */
    div[data-testid="stCustomComponentV1"] iframe,
    video {
        width: 100% !important;
        height: 380px !important;
        object-fit: cover !important; /* Edge-to-edge video without magnifying distortion */
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        border: none !important;
    }

    /* 🛑 HIDE THE ORIGINAL TINY VIEWFINDER BORDERS INSIDE SANDBOX */
    div[style*="border"] {
        display: none !important; /* Eliminates the default tiny marks */
    }
    
    /* 🛡️ INJECT OUR CUSTOM MAXIMUM-SIZED VIEWFINDER VECTOR */
    /* This uses gradient lines pinned perfectly to the inner emerald border */
    div[data-testid="stCustomComponentV1"]::after {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        border-radius: 20px;
        pointer-events: none; /* Allows clicks to pass through to the camera */
        background-image: 
            /* Top Left Corner Vector */
            linear-gradient(to bottom, #10b981 3px, transparent 3px), linear-gradient(to right, #10b981 3px, transparent 3px),
            /* Top Right Corner Vector */
            linear-gradient(to bottom, #10b981 3px, transparent 3px), linear-gradient(to left, #10b981 3px, transparent 3px),
            /* Bottom Left Corner Vector */
            linear-gradient(to top, #10b981 3px, transparent 3px), linear-gradient(to right, #10b981 3px, transparent 3px),
            /* Bottom Right Corner Vector */
            linear-gradient(to top, #10b981 3px, transparent 3px), linear-gradient(to left, #10b981 3px, transparent 3px);
        background-position: 
            0 0, 0 0, /* TL */
            100% 0, 100% 0, /* TR */
            0 100%, 0 100%, /* BL */
            100% 100%, 100% 100%; /* BR */
        background-repeat: no-repeat;
        background-size: 35px 35px; /* Size of the custom corner vectors */
        border: 2px solid rgba(16, 185, 129, 0.2); /* Slight inner edge trace for visibility */
        animation: pulseFinder 2.5s infinite ease-in-out;
    }
    
    /* Add dynamic scan-active pulse animation */
    @keyframes pulseFinder {
        0%, 100% { transform: scale(1.0); opacity: 0.8; }
        50% { transform: scale(0.98); opacity: 0.5; }
    }
    
    /* Transaction elements (same as before) */
    div.stButton > button:first-child { 
        background-color: #10b981 !important; 
        color: white !important; 
        font-weight: bold; 
        width: 100% !important; 
        padding: 14px !important;
        border-radius: 12px !important;
        border: none !important;
    }
    
    /* Clutter cleaners */
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
    # Result UI rendering (same as previous)
    # ... (code omitted for brevity, identical to last response)
    
# -------------------------------------------------------------------------
# INTERFACE STATE 2: HIGH-RES EDGE-TO-EDGE VIEWPORT WITH CUSTOM FINDER
# -------------------------------------------------------------------------
else:
    st.markdown("<p style='text-align:center; color:#9ca3af; font-size:13px; margin-bottom:12px;'>Align player pass credentials inside the matrix window box below:</p>", unsafe_allow_html=True)
    
    # Render Active Lens (stretching high-res fully to the inner card edges)
    scanned_raw = qrcode_scanner(key='live_marshal_camera_engine')
    # Cross-reference and update logic (same as previous)
    # ... (code omitted for brevity, identical to last response)
