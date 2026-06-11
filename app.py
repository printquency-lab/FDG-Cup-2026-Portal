import streamlit as st
import pandas as pd
import requests

# 1. Page Configuration Setup
st.set_page_config(page_title="FDG Cup 2026 - Gate Marshal Portal", page_icon="🛡️", layout="centered")

# 2. Crash-Proof Static CSS Stylesheet Configuration
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0f172a; }
    [data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stMainBlockContainer"] {
        background-color: rgba(23, 29, 41, 0.94) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px; padding: 24px !important;
        max-width: 480px !important; margin: 20px auto !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
    }
    .branding-container { text-align: center; margin-bottom: 10px; }
    .branding-title { font-size: 30px; font-weight: 800; color: #ffffff; font-family: 'Space Grotesk', sans-serif; }
    .branding-subtitle { font-size: 13px; font-weight: 700; color: #10b981; letter-spacing: 2px; text-transform: uppercase; }
    
    div[data-testid="stCustomComponentV1"] {
        width: 100% !important; height: 290px !important; 
        border-radius: 20px !important; border: 3px solid #10b981 !important; 
        overflow: hidden !important; position: relative !important; background-color: #111827; margin-bottom: 15px !important;
    }
    div[data-testid="stCustomComponentV1"] iframe { width: 100% !important; height: 350px !important; position: absolute !important; top: -12px !important; left: 0 !important; }
    div.stButton > button:first-child { background-color: #10b981 !important; color: white !important; font-weight: bold; width: 100% !important; padding: 14px !important; border-radius: 12px !important; }
    .badge-container { background: rgba(0, 0, 0, 0.4); padding: 20px; border-radius: 14px; border: 1px solid #10b981; text-align: center; margin-top: 10px; }
    .badge-container.duplicate { border: 1px solid #ef4444; }
    .badge-number { font-size: 46px; font-weight: 800; color: #facc15; margin: 4px 0; }
    
    .photo-display-frame {
        width: 100%; max-width: 320px; margin: 12px auto 0 auto;
        border-radius: 16px; border: 2px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 10px 25px rgba(0,0,0,0.5); overflow: hidden; display: block;
    }
    #MainMenu, footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='branding-container'><div class='branding-title'>FDG CUP <span style='color:#facc15;'>2026</span></div><div class='branding-subtitle'>Gate Marshal Portal</div></div>", unsafe_allow_html=True)
st.markdown("---")

# 3. Core System Parameters Configuration
GAS_URL = "https://script.google.com/macros/s/AKfycbxCdt8gpKIyOdWW42pqML38LcrztPEI_WnkWCElx9WX8841Xe5pPMK1HECgf_YzniPsEA/exec"
SPREADSHEET_ID = "1l4khiRO2fGqZQ600xcdrVNY_sP0NvmDdPQiOa-jPfR8"

if "active_scan_completed" not in st.session_state:
    st.session_state.active_scan_completed = False
if "display_payload" not in st.session_state:
    st.session_state.display_payload = {}

def get_embed_photo_url(drive_url):
    """Converts a standard Google Drive link directly into a native web image stream."""
    if not drive_url or pd.isna(drive_url) or "drive.google.com" not in str(drive_url):
        return None
    try:
        url_str = str(drive_url).strip()
        if "/file/d/" in url_str:
            file_id = url_str.split("/file/d/")[1].split("/")[0]
        else:
            file_id = url_str.split("id=")[1].split("&")[0]
        return f"https://drive.google.com/uc?id={file_id}"
    except Exception:
        pass
    return None

# -------------------------------------------------------------------------
# INTERFACE STATE 1: VIEW RESULTS METRICS SCREEN
# -------------------------------------------------------------------------
if st.session_state.active_scan_completed:
    res = st.session_state.display_payload
    
    if res["status"] == "SUCCESS":
        st.success("### ✓ Access Authorized & Checked In!")
        st.markdown(f"""
            <div class='badge-container'>
                <p style='margin:0; font-size:12px; color:#9ca3af; font-weight:700;'>ASSIGNED EQUIPMENT DESIGNATION</p>
                <div class='badge-number'>BAG #{res.get('bag', 'N/A')}</div>
                <p style='margin:0; font-size:17px; color:#ffffff; font-weight:600;'>Player: {res.get('name')}</p>
            </div>
        """, unsafe_allow_html=True)
        
        if res.get("id_url") and "drive.google.com" in str(res.get("id_url")):
            st.markdown("<p style='text-align:center; margin:18px 0 0 0; font-size:12px; color:#9ca3af; font-weight:700; letter-spacing:0.5px;'>VERIFICATION PROFILE PHOTO</p>", unsafe_allow_html=True)
            embed_img_url = get_embed_photo_url(res["id_url"])
            if embed_img_url:
                st.markdown(f"<img src='{embed_img_url}' class='photo-display-frame' alt='Verification ID Photo'/>", unsafe_allow_html=True)
            else:
                st.info("ℹ️ Profile photo format link path is missing or invalid.")
        else:
            st.info("ℹ️ Check-in verified. No identification photo attached to this player record yet.")
                
    elif res["status"] == "DUPLICATE":
        st.error("### ⚠️ Security Alert: Already Checked In")
        st.markdown(f"""
            <div class='badge-container duplicate'>
                <p style='margin:0; font-size:12px; color:#ef4444; font-weight:700;'>FLAGGED RETRY ATTEMPT</p>
                <div class='badge-number' style='color:#ef4444;'>DENIED</div>
                <p style='margin:0; font-size:17px; color:#ffffff; font-weight:600;'>Player: {res.get('name')}</p>
            </div>
        """, unsafe_allow_html=True)
        
    else:
        st.error("### ❌ Access Denied: Invalid Credentials")
        st.warning(f"The scanned credential identifier **{res.get('scanned_id')}** does not exist in the registration database.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📷 Open Lens For Next Player"):
        st.session_state.active_scan_completed = False
        st.rerun()

# -------------------------------------------------------------------------
# INTERFACE STATE 2: SCANNING CAMERA VIEWFINDER STREAM LENS
# -------------------------------------------------------------------------
else:
    st.markdown("<p style='text-align:center; color:#9ca3af; font-size:13px; margin-bottom:12px;'>Align player pass credentials inside the camera viewfinder box below:</p>", unsafe_allow_html=True)
    
    from streamlit_qrcode_scanner import qrcode_scanner
    scanned_code = qrcode_scanner(key='live_marshal_camera_engine')
    
    if scanned_code:
        clean_code = str(scanned_code).strip
