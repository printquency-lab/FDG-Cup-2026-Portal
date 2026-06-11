import streamlit as st
import requests
from streamlit_js_eval import streamlit_js_eval

# 1. Page Config Setup
st.set_page_config(page_title="FDG Cup 2026 - Gate Marshal Portal", page_icon="🛡️", layout="centered")

# 2. Layout Stylesheet Overrides
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
    
    div.stButton > button:first-child { background-color: #10b981 !important; color: white !important; font-weight: bold; width: 100% !important; padding: 14px !important; border-radius: 12px !important; }
    .badge-container { background: rgba(0, 0, 0, 0.4); padding: 20px; border-radius: 14px; border: 1px solid #10b981; text-align: center; margin-top: 10px; }
    .badge-container.duplicate { border: 1px solid #ef4444; }
    .badge-number { font-size: 46px; font-weight: 800; color: #facc15; margin: 4px 0; }
    #MainMenu, footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='branding-container'><div class='branding-title'>FDG CUP <span style='color:#facc15;'>2026</span></div><div class='branding-subtitle'>Gate Marshal Portal</div></div>", unsafe_allow_html=True)
st.markdown("---")

# Backend Webhook Configuration Target
GAS_URL = "https://script.google.com/macros/s/AKfycbw83tC6XyAYgPnNg2nTB8NyZN0J9DvjtUAEiSNb3yS3Ze2EVz5q2qqZP8BkDbE6cM42NQ/exec"

# Initialize Session Memory States Safely
if "active_scan_completed" not in st.session_state:
    st.session_state.active_scan_completed = False
if "display_payload" not in st.session_state:
    st.session_state.display_payload = {}
if "last_scanned_raw" not in st.session_state:
    st.session_state.last_scanned_raw = None

def get_embed_photo_url(drive_url):
    """Normalizes the direct Google Drive link to a browser-embeddable thumbnail."""
    if not drive_url:
        return None
    url_str = str(drive_url).strip()
    if "drive.google.com" not in url_str:
        return None
    try:
        if "/file/d/" in url_str:
            file_id = url_str.split("/file/d/")[1].split("/")[0]
        else:
            file_id = url_str.split("id=")[1].split("&")[0]
        return f"https://drive.google.com/thumbnail?id={file_id}&sz=w600"
    except Exception:
        return None

# -------------------------------------------------------------------------
# INTERFACE STATE A: DISPATCH PLAYER CHECK-IN SCAN RESULTS
# -------------------------------------------------------------------------
if st.session_state.active_scan_completed:
    res = st.session_state.display_payload
    status = res.get("status")
    
    if status == "SUCCESS":
        st.success("### ✓ Access Authorized & Checked In!")
        st.markdown(f"""
            <div class='badge-container'>
                <p style='margin:0; font-size:12px; color:#9ca3af; font-weight:700;'>ASSIGNED EQUIPMENT DESIGNATION</p>
                <div class='badge-number'>BAG #{res.get('bag', 'N/A')}</div>
                <p style='margin:0; font-size:17px; color:#ffffff; font-weight:600;'>Player: {res.get('name')}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Display profile photo
        img_url = get_embed_photo_url(res.get("idUrl"))
        if img_url:
            st.markdown("<p style='text-align:center; margin:18px 0 0 0; font-size:12px; color:#9ca3af; font-weight:700;'>VERIFICATION PROFILE PHOTO</p>", unsafe_allow_html=True)
            st.image(img_url, use_container_width=True)
                
    elif status == "DUPLICATE":
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
        scanned_id = res.get('scanned_id', 'Unknown')
        st.warning(f"The scanned identifier **{scanned_id}** does not exist in the registration database.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📷 Open Lens For Next Player"):
        st.session_state.active_scan_completed = False
        st.session_state.last_scanned_raw = None
        st.session_state.display_payload = {}
        st.rerun()

# -------------------------------------------------------------------------
# INTERFACE STATE B: LIVE LIVE CAMERA SCANNING LENS (AUTO-GROW INSTALLED)
# -------------------------------------------------------------------------
else:
    st.markdown("<p style='text-align:center; color:#9ca3af; font-size:13px; margin-bottom:12px;'>Align player pass credentials inside the camera viewfinder box below:</p>", unsafe_allow_html=True)
    
    # Custom JS component containing the window frame auto-expansion layout fix
    js_camera_lens_injector = """
    new Promise((resolve) => {
        // Force the wrapper container iframe to hold its layout height open at 350px
        if (window.frameElement) {
            window.frameElement.style.height = '350px';
        }
        document.documentElement.style.margin = '0';
        document.body.style.margin = '0';
        
        if (window.jsQRInitialized) { return; }
        window.jsQRInitialized = true;
        
        const div = document.createElement('div');
        div.style.cssText = 'width:100%;max-width:420px;margin:0 auto;background:#111827;border:3px solid #10b981;border-radius:20px;overflow:hidden;position:relative;height:300px;box-sizing:border-box;';
        div.innerHTML = '<div id="lvl" style="color:#9ca3af;text-align:center;padding:130px 10px;font-family:sans-serif;font-size:14px;font-weight:600;">Initializing mobile camera stream...</div><canvas id="cvs" style="width:100%;height:100%;display:none;object-fit:cover;"></canvas><video id="vid" style="display:none;" playsinline></video>';
        
        document.body.innerHTML = '';
        document.body.appendChild(div);
        
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.min.js';
        script.onload = () => {
            const video = document.getElementById('vid
