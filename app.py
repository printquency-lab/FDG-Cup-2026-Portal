import streamlit as st
import pandas as pd
import requests

# 1. Page Configuration
st.set_page_config(page_title="FDG Cup 2026 - Gate Marshal Portal", page_icon="🛡️", layout="centered")

# 2. Clean, Safe CSS (No 'f' prefix means CSS brackets won't cause syntax crashes)
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
    .branding-title { font-size: 30px; font-weight: 800; color: #ffffff; }
    .branding-subtitle { font-size: 13px; font-weight: 700; color: #10b981; letter-spacing: 2px; text-transform: uppercase; }
    
    /* Viewfinder Box Constraints */
    div[data-testid="stCustomComponentV1"] {
        width: 100% !important; height: 290px !important; 
        border-radius: 20px !important; border: 3px solid #10b981 !important; 
        overflow: hidden !important; position: relative !important;
        background-color: #111827; margin-bottom: 15px !important;
    }
    div[data-testid="stCustomComponentV1"] iframe {
        width: 100% !important; height: 350px !important; 
        position: absolute !important; top: -12px !important; left: 0 !important;
    }
    
    div.stButton > button:first-child { 
        background-color: #10b981 !important; color: white !important; 
        font-weight: bold; width: 100% !important; padding: 14px !important; border-radius: 12px !important;
    }
    .badge-container { 
        background: rgba(0, 0, 0, 0.4); padding: 20px; border-radius: 14px; 
        border: 1px solid #10b981; text-align: center; margin-top: 10px;
    }
    .badge-container.duplicate { border: 1px solid #ef4444; }
    .badge-number { font-size: 46px; font-weight: 800; color: #facc15; margin: 4px 0; }
    .stImage img { border-radius: 16px !important; box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4); }
    #MainMenu, footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# 3. App Header UI
st.markdown("<div class='branding-container'><div class='branding-title'>FDG CUP <span style='color:#facc15;'>2026</span></div><div class='branding-subtitle'>Gate Marshal Portal</div></div>", unsafe_allow_html=True)
st.markdown("---")

# 4. System Core Constants
GAS_URL = "https://script.google.com/macros/s/AKfycbz2uVYD8eYngcGTI_IrY5XyxYZnAvGbErtFm0gRfgT1ywF_lpwFrPWl1IJreyJwuCuDIw/exec"
SPREADSHEET_ID = "1l4khiRO2fGqZQ600xcdrVNY_sP0NvmDdPQiOa-jPfR8"

# Initialize Session State Variables
if "active_scan_completed" not in st.session_state:
    st.session_state.active_scan_completed = False
if "display_payload" not in st.session_state:
    st.session_state.display_payload = {}

def get_raw_image_bytes(drive_url):
    """Extracts ID from Google Drive links and fetches raw image file bytes safely."""
    if not drive_url or "drive.google.com" not in str(drive_url):
        return None
    try:
        url_str = str(drive_url)
        file_id = ""
        if "/file/d/" in url_str:
            file_id = url_str.split("/file/d/")[1].split("/")[0]
        elif "id=" in url_str:
            file_id = url_str.split("id=")[1].split("&")[0]
            
        if file_id:
            download_url = f"https://docs.google.com/uc?export=download&id={file_id}"
            # Fetch bytes via the server backend to avoid browser cross-origin blocking
            response = requests.get(download_url, timeout=10)
            if response.status_code == 200 and len(response.content) > 1000:
                return response.content
    except Exception:
        pass
    return None

# -------------------------------------------------------------------------
# INTERFACE VIEW 1: RESULTS DASHBOARD
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
        
        # Profile Picture Block
        if res.get("id_url"):
            st.markdown("<p style='margin:15px 0 5px 5px; font-size:12px; color:#9ca3af; font-weight:700;'>VERIFICATION PROFILE PHOTO</p>", unsafe_allow_html=True)
            image_data = get_raw_image_bytes(res["id_url"])
            if image_data:
                st.image(image_data, use_container_width=True)
            else:
                st.info("ℹ️ Profile photo unavailable or not found.")
                
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
        st.warning(f"The scanned identity code **{res.get('scanned_id')}** was not found in the roster database.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📷 Open Lens For Next Player"):
        st.session_state.active_scan_completed = False
        st.rerun()

# -------------------------------------------------------------------------
# INTERFACE VIEW 2: ACTIVE LIVE SCANNER
# -------------------------------------------------------------------------
else:
    st.markdown("<p style='text-align:center; color:#9ca3af; font-size:13px; margin-bottom:12px;'>Align player pass credentials inside the camera viewfinder box:</p>", unsafe_allow_html=True)
    
    from streamlit_qrcode_scanner import qrcode_scanner
    scanned_code = qrcode_scanner(key='live_marshal_camera_engine')
    
    if scanned_code:
        clean_code = str(scanned_code).strip()
        
        # Fetch clean real-time list data from Google Sheets
        csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"
        records = pd.read_csv(csv_url, header=None).values.tolist()
        
        # Isolate digits to allow flexible matching (e.g., matching "1" with "FDG26-1")
        only_digits = "".join(filter(str.isdigit, clean_code))
        
        matched_row = None
        for row in records:
            for cell in row:
                cell_text = str(cell).strip()
                if cell_text == clean_code or (only_digits and cell_text == only_digits):
                    matched_row = row
                    break
            if matched_row is not None:
                break
                
        if matched_row is not None:
            try:
                full_name = f"{matched_row[1]} {matched_row[0]}"
                bag_no = matched_row[5]
                checked_in = str(matched_row[6]).strip() == "Checked-In"
                
                if checked_in:
                    st.session_state.display_payload = {"status": "DUPLICATE", "name": full_name}
                else:
                    # Notify Google Apps Script database webhook
                    gas_res = requests.get(GAS_URL, params={"mode": "verify_bypass", "pid": clean_code}, timeout=10).json()
                    st.session_state.display_payload = {
                        "status": "SUCCESS", "name": full_name, "bag": bag_no, "id_url": gas_res.get("idUrl", "")
                    }
            except Exception:
                st.session_state.display_payload = {"status": "NOT_FOUND", "scanned_id": clean_code}
        else:
            st.session_state.display_payload = {"status": "NOT_FOUND", "scanned_id": clean_code}
            
        st.session_state.active_scan_completed = True
        st.rerun()
