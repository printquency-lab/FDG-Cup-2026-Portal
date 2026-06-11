import streamlit as st
import pandas as pd
import requests
from streamlit_js_eval import streamlit_js_eval

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
    
    .scanner-wrapper { width: 100%; max-width: 380px; margin: 0 auto; background: #111827; border: 3px solid #10b981; border-radius: 20px; overflow: hidden; position: relative; }
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
if "last_scanned_raw" not in st.session_state:
    st.session_state.last_scanned_raw = None

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
        st.session_state.last_scanned_raw = None
        st.session_state.display_payload = {}
        st.rerun()

# -------------------------------------------------------------------------
# INTERFACE STATE 2: HIGH-PERFORMANCE SCANNING LENS VIA COGNITIVE EVAL BRIDGE
# -------------------------------------------------------------------------
else:
    st.markdown("<p style='text-align:center; color:#9ca3af; font-size:13px; margin-bottom:12px;'>Align player pass credentials inside the camera viewfinder box below:</p>", unsafe_allow_html=True)
    
    # We construct the HTML framework within a clean string safely isolated from formatting conflict bugs
    raw_js_lens_injector = (
        "new Promise((resolve) => {"
        "   const wrapper = document.createElement('div');"
        "   wrapper.className = 'scanner-wrapper';"
        "   wrapper.innerHTML = `"
        "       <div style='width:100%; background:#111827; box-sizing:border-box; position:relative; min-height:260px;'>"
        "           <div id='lens-loader' style='color:#9ca3af; text-align:center; padding:100px 10px; font-family:sans-serif; font-size:14px;'>Opening fast video streams...</div>"
        "           <canvas id='canvas-stream' style='width:100%; display:none; vertical-align:middle; border-radius:16px;'></canvas>"
        "           <video id='video-stream' style='display:none;'></video>"
        "       </div>`;"
        "   document.body.appendChild(wrapper);"
        "   "
        "   const scr = document.createElement('script');"
        "   scr.src = 'https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.min.js';"
        "   scr.onload = () => {"
        "       const video = document.getElementById('video-stream');"
        "       const canvas = document.getElementById('canvas-stream');"
        "       const ctx = canvas.getContext('2d');"
        "       const loader = document.getElementById('lens-loader');"
        "       "
        "       navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })"
        "       .then((stream) => {"
        "           video.srcObject = stream;"
        "           video.setAttribute('playsinline', true);"
        "           video.play();"
        "           "
        "           function parseVideoTrack() {"
        "               if (video.readyState === video.HAVE_CURRENT_DATA) {"
        "                   loader.style.display = 'none';"
        "                   canvas.style.display = 'block';"
        "                   canvas.height = video.videoHeight;"
        "                   canvas.width = video.videoWidth;"
        "                   ctx.drawImage(video, 0, 0, canvas.width, canvas.height);"
        "                   const img = ctx.getImageData(0, 0, canvas.width, canvas.height);"
        "                   const qr = jsQR(img.data, img.width, img.height, { inversionAttempts: 'dontInvert' });"
        "                   if (qr && qr.data.trim() !== '') {"
        "                       if (window.navigator && window.navigator.vibrate) {"
        "                           window.navigator.vibrate(200);"
        "                       }"
        "                       stream.getTracks().forEach(t => t.stop());"
        "                       resolve(qr.data.trim());"
        "                       return;"
        "                   }"
        "               }"
        "               requestAnimationFrame(parseVideoTrack);"
        "           }"
        "           requestAnimationFrame(parseVideoTrack);"
        "       }).catch(() => { loader.innerText = '⚠️ Camera access denied.'; });"
        "   };"
        "   document.body.appendChild(scr);"
        "})"
    )

    # Fire evaluation engine securely across the execution context layer
    scanned_payload = streamlit_js_eval(js_expressions=raw_js_lens_injector, key="eval_lens_stream")
    
    if scanned_payload and str(scanned_payload).strip() != "" and scanned_payload != st.session_state.last_scanned_raw:
        clean_code = str(scanned_payload).strip()
        st.session_state.last_scanned_raw = clean_code
        
        attendance_csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Attendance%20Log"
        master_csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=MasterList"
        
        df_log = pd.read_csv(attendance_csv_url, dtype=str)
        df_master = pd.read_csv(master_csv_url, dtype=str)
        
        df_log.columns = df_log.columns.str.strip()
        df_master.columns = df_master.columns.str.strip()
        
        # 1. Look up Player inside "Attendance Log" column
        matched_log = df_log[df_log['Players ID'].astype(str).str.strip() == clean_code]
        
        if not matched_log.empty:
            log_row = matched_log.iloc[0]
            player_name = str(log_row['Player Name']).strip()
            photo_link = str(log_row['ID File URL']).strip()
            
            # 2. Check and read registration record metrics inside "MasterList"
            matched_master = pd.DataFrame()
            for idx, row_m in df_master.iterrows():
                full_m_name = f"{row_m['First Name']} {row_m['Last Name']}".lower().strip()
                if player_name.lower() in full_m_name or full_m_name in player_name.lower():
                    matched_master = df_master.iloc[[idx]]
                    break
            
            if not matched_master.empty:
                master_row = matched_master.iloc[0]
                
                # Clean decimal formatting issues safely (.0 eliminated)
                raw_bag = str(master_row['Bag ref number']).strip()
                bag_no = raw_bag.split('.')[0] if '.' in raw_bag else raw_bag
                
                attendance_status = str(master_row['Status']).strip()
                
                if attendance_status == "Checked-In":
                    st.session_state.display_payload = {"status": "DUPLICATE", "name": player_name}
                else:
                    # Fire check-in trigger out to your Apps Script endpoint API
                    try:
                        gas_res = requests.get(GAS_URL, params={"mode": "verify_bypass", "pid": clean_code}, timeout=10).json()
                        if gas_res.get("idUrl"):
                            photo_link = str(gas_res.get("idUrl")).strip()
                    except Exception:
                        pass
                    
                    st.session_state.display_payload = {
                        "status": "SUCCESS", "name": player_name, "bag": bag_no, "id_url": photo_link
                    }
            else:
                st.session_state.display_payload = {
                    "status": "SUCCESS", "name": player_name, "bag": "N/A", "id_url": photo_link
                }
        else:
            st.session_state.display_payload = {"status": "NOT_FOUND", "scanned_id": clean_code}
            
        st.session_state.active_scan_completed = True
        st.rerun()
