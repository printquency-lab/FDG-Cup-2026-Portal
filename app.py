import streamlit as st
import requests
from streamlit_js_eval import streamlit_js_eval

# 1. Page Configuration Setup
st.set_page_config(page_title="FDG Cup 2026 - Gate Marshal Portal", page_icon="🛡️", layout="centered")

# 2. Complete Layout Stylesheet Customization
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
    
    .photo-display-frame {
        width: 100%; max-width: 320px; margin: 12px auto 0 auto;
        border-radius: 16px; border: 2px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 10px 25px rgba(0,0,0,0.5); display: block;
    }
    #MainMenu, footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='branding-container'><div class='branding-title'>FDG CUP <span style='color:#facc15;'>2026</span></div><div class='branding-subtitle'>Gate Marshal Portal</div></div>", unsafe_allow_html=True)
st.markdown("---")

# 3. Webhook Endpoint Target Parameter Setup
GAS_URL = "https://script.google.com/macros/s/AKfycbw83tC6XyAYgPnNg2nTB8NyZN0J9DvjtUAEiSNb3yS3Ze2EVz5q2qqZP8BkDbE6cM42NQ/exec"

if "active_scan_completed" not in st.session_state:
    st.session_state.active_scan_completed = False
if "display_payload" not in st.session_state:
    st.session_state.display_payload = {}
if "last_scanned_raw" not in st.session_state:
    st.session_state.last_scanned_raw = None

def get_embed_photo_url(drive_url):
    """Converts a restricted file link into a secure, allowed web preview thumbnail."""
    if not drive_url or any(x in str(drive_url) for x in ["None", "NaN", "undefined", "View ID"]) or "drive.google.com" not in str(drive_url):
        return None
    try:
        url_str = str(drive_url).strip()
        if "/file/d/" in url_str:
            file_id = url_str.split("/file/d/")[1].split("/")[0]
        else:
            file_id = url_str.split("id=")[1].split("&")[0]
        return f"https://drive.google.com/thumbnail?id={file_id}&sz=w600"
    except Exception:
        pass
    return None

# -------------------------------------------------------------------------
# INTERFACE STATE 1: VIEW METRICS CHECK-IN RESULT SCREEN
# -------------------------------------------------------------------------
if st.session_state.active_scan_completed:
    res = st.session_state.display_payload
    
    if res.get("status") == "SUCCESS":
        st.success("### ✓ Access Authorized & Checked In!")
        st.markdown(f"""
            <div class='badge-container'>
                <p style='margin:0; font-size:12px; color:#9ca3af; font-weight:700;'>ASSIGNED EQUIPMENT DESIGNATION</p>
                <div class='badge-number'>BAG #{res.get('bag', 'N/A')}</div>
                <p style='margin:0; font-size:17px; color:#ffffff; font-weight:600;'>Player: {res.get('name')}</p>
            </div>
        """, unsafe_allow_html=True)
        
        embed_img_url = get_embed_photo_url(res.get("idUrl"))
        if embed_img_url:
            st.markdown("<p style='text-align:center; margin:18px 0 0 0; font-size:12px; color:#9ca3af; font-weight:700; letter-spacing:0.5px;'>VERIFICATION PROFILE PHOTO</p>", unsafe_allow_html=True)
            st.markdown(f"<img src='{embed_img_url}' class='photo-display-frame' alt='ID Photo'/>", unsafe_allow_html=True)
        else:
            st.info("ℹ️ Profile photo unavailable or private folder permissions need updating.")
                
    elif res.get("status") == "DUPLICATE":
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
        st.warning(f"The scanned credential identifier **{res.get('scanned_id', 'Unknown')}** does not exist in the registration database.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📷 Open Lens For Next Player"):
        st.session_state.active_scan_completed = False
        st.session_state.last_scanned_raw = None
        st.session_state.display_payload = {}
        st.rerun()

# -------------------------------------------------------------------------
# INTERFACE STATE 2: HIGH-PERFORMANCE LIVE HARDWARE SCANNING LENS
# -------------------------------------------------------------------------
else:
    st.markdown("<p style='text-align:center; color:#9ca3af; font-size:13px; margin-bottom:12px;'>Align player pass credentials inside the camera viewfinder box below:</p>", unsafe_allow_html=True)
    
    # Fully contained clean JS string injection block - avoids syntax crashes
    js_camera_lens_injector = """
    new Promise((resolve) => {
        if (window.jsQRInitialized) { return; }
        window.jsQRInitialized = true;
        
        const div = document.createElement('div');
        div.style.cssText = 'width:100%;max-width:380px;margin:0 auto;background:#111827;border:3px solid #10b981;border-radius:20px;overflow:hidden;position:relative;min-height:250px;box-sizing:border-box;';
        div.innerHTML = '<div id="lvl" style="color:#9ca3af;text-align:center;padding:95px 10px;font-family:sans-serif;font-size:14px;">Initializing mobile camera stream...</div><canvas id="cvs" style="width:100%;display:none;vertical-align:middle;"></canvas><video id="vid" style="display:none;" playsinline></video>';
        document.body.appendChild(div);
        
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.min.js';
        script.onload = () => {
            const video = document.getElementById('vid');
            const canvas = document.getElementById('cvs');
            const ctx = canvas.getContext('2d');
            const loader = document.getElementById('lvl');
            
            navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
            .then((stream) => {
                video.srcObject = stream;
                video.play();
                
                function loop() {
                    if (video.readyState === video.HAVE_CURRENT_DATA) {
                        loader.style.display = 'none';
                        canvas.style.display = 'block';
                        canvas.height = video.videoHeight;
                        canvas.width = video.videoWidth;
                        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                        
                        const img = ctx.getImageData(0, 0, canvas.width, canvas.height);
                        const qr = jsQR(img.data, img.width, img.height, { inversionAttempts: 'dontInvert' });
                        
                        if (qr && qr.data.trim() !== '') {
                            if (navigator.vibrate) { navigator.vibrate(200); }
                            stream.getTracks().forEach(t => t.stop());
                            div.remove();
                            window.jsQRInitialized = false;
                            resolve(qr.data.trim());
                            return;
                        }
                    }
                    requestAnimationFrame(loop);
                }
                requestAnimationFrame(loop);
            }).catch(() => { loader.innerText = '⚠️ Camera blocked or environment lens unavailable.'; });
        };
        document.body.appendChild(script);
    });
    """

    scanned_payload = streamlit_js_eval(js_expressions=js_camera_lens_injector, key="live_marshal_lens")
    
    if scanned_payload and str(scanned_payload).strip() != "" and scanned_payload != st.session_state.last_scanned_raw:
        clean_code = str(scanned_payload).strip()
        st.session_state.last_scanned_raw = clean_code
        
        # Pull registration data directly from the live Google Apps Script endpoint
        with st.spinner("Verifying credentials live..."):
            try:
                gas_res = requests.get(GAS_URL, params={"mode": "verify_bypass", "pid": clean_code}, timeout=12).json()
                if gas_res.get("status") == "NOT_FOUND":
                    st.session_state.display_payload = {"status": "NOT_FOUND", "scanned_id": clean_code}
                else:
                    st.session_state.display_payload = gas_res
            except Exception as e:
                st.session_state.display_payload = {"status": "ERROR", "message": str(e)}
                
        st.session_state.active_scan_completed = True
        st.rerun()
