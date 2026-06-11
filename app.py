import streamlit as st
import pandas as pd
import requests
import json
import re

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
GAS_URL = "https://script.google.com/macros/s/AKfycbz2uVYD8eYngcGTI_IrY5XyxYZnAvGbErtFm0gRfgT1ywF_lpwFrPWl1IJreyJwuCuDIw/exec"
SPREADSHEET_ID = "1l4khiRO2fGqZQ600xcdrVNY_sP0NvmDdPQiOa-jPfR8"

if "active_scan_completed" not in st.session_state:
    st.session_state.active_scan_completed = False
if "display_payload" not in st.session_state:
    st.session_state.display_payload = {}

def fetch_sheet_with_links(sheet_name):
    """Fetches full structural data grid including hidden hyperlink URL targets."""
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:json&sheet={sheet_name}"
    try:
        response = requests.get(url, timeout=10)
        # Clean json wrapper response template
        raw_text = response.text
        start_idx = raw_text.find("google.visualization.Query.setResponse(") + len("google.visualization.Query.setResponse(")
        end_idx = raw_text.rfind(");")
        json_data = json.loads(raw_text[start_idx:end_idx])
        
        columns = [col.get("label", "").strip() for col in json_data["table"]["cols"]]
        rows_list = []
        
        for row in json_data["table"]["rows"]:
            row_cells = []
            for cell in row["c"]:
                if cell is None:
                    row_cells.append("")
                elif "v" in cell and str(cell["v"]).startswith("http"):
                    row_cells.append(str(cell["v"]))
                elif "f" in cell and "hyperlink" in str(cell.get("f", "")).lower():
                    # Parse out string URL locations hiding inside Hyperlink formula definitions
                    matches = re.findall(r'https?://[^\s"\']+', cell["f"])
                    row_cells.append(matches[0] if matches else cell.get("v", ""))
                else:
                    row_cells.append(cell.get("v", "") if cell else "")
            rows_list.append(row_cells)
            
        return pd.DataFrame(rows_list, columns=columns)
    except Exception:
        # Fallback to default fetch if structural json parse errors occur
        csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        return pd.read_csv(csv_url)

def get_embed_photo_url(drive_url):
    """Converts a parsed Google Drive string path down to raw browser view embed target."""
    if not drive_url or pd.isna(drive_url) or "drive.google.com" not in str(drive_url):
        return None
    try:
        url_str = str(drive_url)
        if "/file/d/" in url_str:
            file_id = url_str.split("/file/d/")[1].split("/")[0]
        else:
            file_id = url_str.split("id=")[1].split("&")[0]
        return f"https://drive.google.com/uc?id={file_id}"
    except Exception:
        pass
    return None

# -------------------------------------------------------------------------
# INTERFACE STATE 1: REVEAL TRANSACTION SUCCESS OR WARNING SCREENS
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
                st.markdown(f"<img src='{embed_img_url}' class='photo-display-frame' alt='Verification Frame'/>", unsafe_allow_html=True)
            else:
                st.info("ℹ️ Profile photo link format unrecognized or empty.")
        else:
            st.info("ℹ️ Profile verified. No identification attachment found in cell data.")
                
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
# INTERFACE STATE 2: RENDERING CAMERA VIEWFINDER STREAM LENS
# -------------------------------------------------------------------------
else:
    st.markdown("<p style='text-align:center; color:#9ca3af; font-size:13px; margin-bottom:12px;'>Align player pass credentials inside the camera viewfinder box below:</p>", unsafe_allow_html=True)
    
    from streamlit_qrcode_scanner import qrcode_scanner
    scanned_code = qrcode_scanner(key='live_marshal_camera_engine')
    
    if scanned_code:
        clean_code = str(scanned_code).strip()
        
        # Load advanced sheets data engines explicitly bypassing standard string masking limits
        df_log = fetch_sheet_with_links("Attendance%20Log")
        df_master = fetch_sheet_with_links("MasterList")
        
        df_log.columns = df_log.columns.str.strip()
        df_master.columns = df_master.columns.str.strip()
        
        # 1. Look up code inside the Attendance Log sheet column data
        matched_log = df_log[df_log['Players ID'].astype(str).str.strip() == clean_code]
        
        if not matched_log.empty:
            log_row = matched_log.iloc[0]
            player_name = str(log_row['Player Name']).strip()
            photo_link = log_row['ID File URL'] # Grab unmasked Google Drive path link directly
            
            # 2. Look up the player status data details inside MasterList grid rows
            matched_master = pd.DataFrame()
            for idx, row_m in df_master.iterrows():
                full_m_name = f"{row_m['First Name']} {row_m['Last Name']}".lower().strip()
                if player_name.lower() in full_m_name or full_m_name in player_name.lower():
                    matched_master = df_master.iloc[[idx]]
                    break
            
            if not matched_master.empty:
                master_row = matched_master.iloc[0]
                bag_no = master_row['Bag ref number']
                attendance_status = str(master_row['Status']).strip()
                
                if attendance_status == "Checked-In":
                    st.session_state.display_payload = {"status": "DUPLICATE", "name": player_name}
                else:
                    # Update database backend log
                    try:
                        gas_res = requests.get(GAS_URL, params={"mode": "verify_bypass", "pid": clean_code}, timeout=10).json()
                        if gas_res.get("idUrl"):
                            photo_link = gas_res.get("idUrl")
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
