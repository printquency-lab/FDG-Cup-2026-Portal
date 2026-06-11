import streamlit as st
import requests
from streamlit_js_eval import streamlit_js_eval

# 1. Page Configuration
st.set_page_config(page_title="FDG Cup 2026 - Gate Marshal Portal", page_icon="🛡️", layout="centered")

# 2. Complete CSS Custom UI Layer Override
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

# Production Webhook API Endpoint
GAS_URL = "https://script.google.com/macros/s/AKfycbw83tC6XyAYgPnNg2nTB8NyZN0J9DvjtUAEiSNb3yS3Ze2EVz5q2qqZP8BkDbE6cM42NQ/exec"

# Initialize App Cache Framework States safely
if "active_scan_completed" not in st.session_state:
    st.session_state.active_scan_completed = False
if "display_payload" not in st.session_state:
    st.session_state.display_payload = {}
if "last_scanned_raw" not in st.session_state:
    st.session_state.last_scanned_raw = None

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
        
        # Pull backend image parameter natively
        img_url = res.get("idUrl")
        if img_url and str(img_url).startswith("http"):
            st.markdown("<p style='text-align:center; margin:18px 0 0 0; font-size:12px; color:#9ca3af; font-weight:700;'>VERIFICATION PROFILE PHOTO</p>", unsafe_allow_html=True)
            st.image(str(img_url).strip(), use_container_width=True)
                
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
        st.warning(f"The scanned credential identifier **{scanned_id}** does not exist within the active registration sheet database.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📷 Open Lens For Next Player"):
        st.session_state.active_scan_completed = False
        st.session_state.last_scanned_raw = None
        st.session_state.display_payload = {}
        st.rerun()

# -------------------------------------------------------------------------
# INTERFACE STATE B: LIVE LIVE CAMERA SCANNING LENS (FLEX-INIT IMPLEMENTED)
# -------------------------------------------------------------------------
else:
    st.markdown("<p style='text-align:center; color:#9ca3af; font-size:13px; margin-bottom:12px;'>Align player pass credentials inside the camera viewfinder box below:</p>", unsafe_allow_html=True)
    
    # Highly resilient JS camera stream engine with explicit iframe size bindings
    js_camera_lens_injector = """
    new Promise((resolve) => {
        if (window.frameElement) {
            window.frameElement.style.height = '380px';
        }
        document.documentElement.style.margin = '0';
        document.body.style.margin = '0';
        
        if (window.jsQRInitialized) { return; }
        window.jsQRInitialized = true;
        
        const div = document.createElement('div');
        div.style.cssText = 'width:100%;max-width:420px;margin:0 auto;background:#111827;border:3px solid #10b981;border-radius:20px;overflow:hidden;position:relative;height:320px;box-sizing:border-box;';
        div.innerHTML = '<div id="lvl" style="color:#9ca3af;text-align:center;padding:140px 10px;font-family:sans-serif;font-size:14px;font-weight:600;">Initializing mobile camera stream...</div><canvas id="cvs" style="width:100%;height:100%;display:none;object-fit:cover;"></canvas><video id="vid" style="display:none;" autoplay playsinline muted></video>';
        
        document.body.innerHTML = '';
        document.body.appendChild(div);
        
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.min.js';
        script.onload = () => {
            const video = document.getElementById('vid');
            const canvas = document.getElementById('cvs');
            const ctx = canvas.getContext('2d');
            const loader = document.getElementById('lvl');
            
            // Highly robust mobile multi-scenario camera configuration constraints
            const constraints = {
                video: {
                    facingMode: 'environment',
                    width: { ideal: 640 },
                    height: { ideal: 480 }
                }
            };
            
            function launchStream(mediaConstraints) {
                navigator.mediaDevices.getUserMedia(mediaConstraints)
                .then((stream) => {
                    video.srcObject = stream;
                    video.setAttribute("playsinline", true);
                    video.setAttribute("muted", true);
                    video.play().catch(e => console.log("Play error:", e));
                    
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
                })
                .catch((err) => {
                    // Fallback branch if ideal camera parameters are blocked on older device engines
                    if (mediaConstraints.video.width) {
                        console.log("Retrying with loose constraints...");
                        launchStream({ video: { facingMode: 'environment' } });
                    } else {
                        loader.innerHTML = '⚠️ Camera Blocked<br><span style="font-size:11px;color:#ef4444;font-weight:normal;">Please grant site camera permissions & reload.</span>';
                    }
                });
            }
            
            launchStream(constraints);
        };
        document.body.appendChild(script);
    });
    """

    scanned_payload = streamlit_js_eval(js_expressions=js_camera_lens_injector, key="live_marshal_lens_v2")
    
    if scanned_payload and str(scanned_payload).strip() != "" and scanned_payload != st.session_state.last_scanned_raw:
        clean_code = str(scanned_payload).strip()
        st.session_state.last_scanned_raw = clean_code
        
        with st.spinner("Verifying credentials live..."):
            try:
                # Target parameter 'pid' instead of 'id' to seamlessly align with your functional backend routing setup
                gas_res = requests.get(GAS_URL, params={"mode": "verify_bypass", "pid": clean_code}, timeout=12).json()
                if gas_res.get("status") == "NOT_FOUND":
                    st.session_state.display_payload = {"status": "NOT_FOUND", "scanned_id": clean_code}
                else:
                    st.session_state.display_payload = gas_res
            except Exception as e:
                st.session_state.display_payload = {"status": "ERROR", "message": str(e), "scanned_id": clean_code}
                
        st.session_state.active_scan_completed = True
        st.rerun()
