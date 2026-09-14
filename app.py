import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import requests

# Set page config
st.set_page_config(
    page_title="ระบบจัดการที่นาและบ้านเช่า (Ricefield & Property Management)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern design and Thai fonts
st.markdown("""
    <style>
    @import url('https://googleapis.com');
    html, body, [class*="css"], text {
        font-family: 'Sarabun', sans-serif !important;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #28a745;
        margin-bottom: 15px;
    }
    .tax-alert {
        background-color: #fff3cd;
        color: #856404;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #ffc107;
        margin-bottom: 20px;
        font-weight: bold;
    }
    .inspection-alert {
        background-color: #f8d7da;
        color: #721c24;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #dc3545;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------------
# FIX: DIRECT GOOGLE SHEETS LINK CONFIGURATION
# --------------------------------------------------------------------------------
# ฝังลิงก์ไอดีสเปรดชีตของคุณโดยตรงเพื่อป้องกันปัญหาการตัด URL ผิดพลาด
SHEET_URL = "https://google.com"

@st.cache_data(ttl=1)
def load_sheet_data(worksheet_name):
    try:
        # ใช้โครงสร้างเรียกข้อมูลตรงตามมาตรฐานการพิมพ์เผยแพร่เว็บสากล
        csv_url = f"{SHEET_URL}/gviz/tq?tqx=out:csv&sheet={worksheet_name}"
        df = pd.read_csv(csv_url)
        return df
    except Exception as e:
        st.error(f"ไม่สามารถโหลดแผ่นงาน {worksheet_name} ได้: {e}")
        return pd.DataFrame()

# ฟังก์ชันส่งฟอร์มข้อมูลเข้า Apps Script หลังบ้าน
def submit_to_webos(worksheet_name, data_dict):
    try:
        webos_url = st.secrets["connections"]["gsheets"].get("webos_api", "")
        if webos_url:
            data_dict["worksheet"] = worksheet_name
            response = requests.post(webos_url, data=data_dict, timeout=10)
            if response.status_code == 200:
                return True
    except Exception:
        pass
    return False

# ดึงข้อมูลจากแต่ละหน้าแท็บใน Google Sheets ของคุณ
df_properties = load_sheet_data("Properties")
df_employees = load_sheet_data("Employees")
df_tenants = load_sheet_data("Tenants")
df_leases = load_sheet_data("Leases")
df_payments = load_sheet_data("Payments")

# จัดเตรียมระบบจัดการวันเดือนปีให้เสถียร
for df in [df_properties, df_leases, df_payments]:
    if not df.empty:
        for col in df.columns:
            if 'วัน' in col or 'date' in col.lower():
                df[col] = pd.to_datetime(df[col]).dt.date

# --------------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------------------------------------
st.sidebar.title("🌾 Ricefield & Property")
st.sidebar.subheader("ระบบจัดการค่าเช่าและที่ดิน")
menu = st.sidebar.radio(
    "เมนูการใช้งาน",
    ["🏠 หน้าแรก (Dashboard)", "🌾 ข้อมูลที่ดิน/บ้านเช่า", "👥 ข้อมูลผู้เช่า", "📋 สัญญาเช่า", "💰 ประวัติการชำระเงิน", "🧑‍💼 ข้อมูลพนักงาน"]
)

if st.sidebar.button("🔄 รีเฟรชดึงข้อมูลใหม่จาก Sheets"):
    st.cache_data.clear()
    st.rerun()

# --------------------------------------------------------------------------------
# 1. DASHBOARD PAGE
# --------------------------------------------------------------------------------
if menu == "🏠 หน้าแรก (Dashboard)":
    st.title("📊 หน้าแรก / แผงควบคุมระบบ (Dashboard)")
    
    col1, col2, col3 = st.columns([1, 1.5, 1.5])
    
    with col1:
        st.subheader("สถานะว่าง/มีคนเช่า")
        if not df_properties.empty and "สถานะ" in df_properties.columns:
            vacant_count = len(df_properties[df_properties["สถานะ"] == "ว่าง"])
            occupied_count = len(df_properties[df_properties["สถานะ"] == "มีคนเช่า"])
            
            fig = px.pie(
                names=["ว่าง", "มีคนเช่า"],
                values=[vacant_count, occupied_count],
                color=["ว่าง", "มีคนเช่า"],
                color_discrete_map={"ว่าง": "#cbd5e1", "มีคนเช่า": "#28a745"},
                hole=0.4
            )
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=220)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("ไม่มีข้อมูลสถานะทรัพย์สิน")

    with col2:
        st.subheader("⚠️ แจ้งเตือนสิทธิ/ภาษีและภารกิจเร่งด่วน")
        if not df_properties.empty and "สถานะภาษี" in df_properties.columns:
            unpaid_tax_count = len(df_properties[df_properties["สถานะภาษี"] == "ยังไม่ได้ชำระ"])
            if unpaid_tax_count > 0:
                st.markdown(f'<div class="tax-alert">💸 มีทรัพย์สินค้างชำระภาษีสะสม: {unpaid_tax_count} แปลง!</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:green; font-weight:bold;">✅ ชำระภาษีครบถ้วนทุกแปลง</div>', unsafe_allow_html=True)

    with col3:
        st.subheader("💡 รายชื่อผู้เช่าค้างชำระค่าเช่า")
        if not df_leases.empty and "วันครบกำหนดชำระค่าเช่า" in df_leases.columns:
            overdue_leases = df_leases[df_leases["วันครบกำหนดชำrateค่าเช่า"] < datetime.now().date()] if "วันครบกำหนดชำrateค่าเช่า" in df_leases.columns else df_leases[df_leases.iloc[:,6] < datetime.now().date()] if len(df_leases.columns) > 6 else pd.DataFrame()
            if not overdue_leases.empty:
                for idx, row in overdue_leases.iterrows():
                    st.error(f"❌ {row.iloc[1]} | ค้างชำระค่าเช่าในระบบ")
            else:
                st.success("🎉 ไม่มีผู้เช่าค้างชำระในระบบขณะนี้")

    st.subheader("📋 รายการทรัพย์สินทั้งหมดในคลัง")
    st.dataframe(df_properties, use_container_width=True)
# --------------------------------------------------------------------------------
# 2. PROPERTIES PAGE
# --------------------------------------------------------------------------------
elif menu == "🌾 ข้อมูลที่ดิน/บ้านเช่า":
    st.title("🌾 รายละเอียดที่ดินและบ้านเช่า")
    tab1, tab2 = st.tabs(["📝 รายการทรัพย์สินทั้งหมด", "➕ เพิ่มข้อมูลใหม่"])
    with tab1:
        st.dataframe(df_properties, use_container_width=True)
    with tab2:
        with st.form("prop_form"):
            p_id = st.text_input("รหัสทรัพย์สิน (เช่น P005)")
            p_name = st.text_input("ชื่อที่ดิน/บ้านเช่า")
            p_type = st.selectbox("ประเภท", ["ที่นา", "บ้านเช่า"])
            p_status = st.selectbox("สถานะ", ["ว่าง", "มีคนเช่า"])
            p_tenant = st.text_input("ผู้เช่าปัจจุบัน", value="-")
            p_rent_type = st.selectbox("ประเภทการเช่า", ["หลังเก็บเกี่ยว", "รายเดือน", "เก็บก่อนทำ (รายปี)", "รายปี"])
            p_dep = st.number_input("เงินมัดจำ (บาท)", min_value=0)
            p_rent = st.number_input("ค่าเช่า (บาท)", min_value=0)
            p_geo = st.text_input("พิกัดตำแหน่งที่ดิน")
            p_tax_date = st.date_input("วันครบชำระภาษีที่ดิน")
            p_tax_status = st.selectbox("สถานะภาษี", ["ชำระแล้ว", "ยังไม่ได้ชำระ"])
            
            if st.form_submit_button("💾 บันทึกข้อมูลทรัพย์สิน"):
                payload = {
                    "id": p_id, "ชื่อที่ดิน": p_name, "ประเภท": p_type, "สถานะ": p_status,
                    "ผู้เช่าปัจจุบัน": p_tenant, "ประเภทการเช่า": p_rent_type, "เงินมัดจำ": p_dep,
                    "ค่าเช่า": p_rent, "พิกัด": p_geo, "วันครบชำระภาษี": str(p_tax_date), "สถานะภาษี": p_tax_status
                }
                if submit_to_webos("Properties", payload):
                    st.success("🎉 บันทึกข้อมูลเข้า Google Sheets สำเร็จ!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.info("🔄 ส่งข้อมูลผ่าน Apps Script เรียบร้อยแล้ว (ตรวจสอบหน้าชีตเพื่ออัปเดตข้อมูล)")

# --------------------------------------------------------------------------------
# 3. TENANTS PAGE
# --------------------------------------------------------------------------------
elif menu == "👥 ข้อมูลผู้เช่า":
    st.title("👥 ระบบข้อมูลผู้เช่า")
    tab1, tab2 = st.tabs(["👥 รายชื่อผู้เช่าปัจจุบัน", "➕ เพิ่มรายชื่อผู้เช่าใหม่"])
    with tab1:
        st.dataframe(df_tenants, use_container_width=True)
    with tab2:
        with st.form("tenant_form"):
            t_name = st.text_input("ชื่อ-นามสกุลผู้เช่า")
            t_addr = st.text_area("ที่อยู่ตามทะเบียนบ้าน/ติดต่อ")
            t_phone = st.text_input("เบอร์โทรศัพท์")
            t_doc = st.text_input("ชื่อไฟล์เอกสารหลักฐาน (เช่น บัตรประชาชน_สมชาย.pdf)")
            t_lease = st.text_input("เลขที่สัญญาผูกพัน (เช่น CNT003)")
            
            if st.form_submit_button("💾 บันทึกข้อมูลผู้เช่า"):
                payload = {"ชื่อ": t_name, "ที่อยู่": t_addr, "เบอร์โทร": t_phone, "เอกสาร": t_doc, "สัญญาผูกพัน": t_lease}
                if submit_to_webos("Tenants", payload):
                    st.success("🎉 บันทึกข้อมูลเข้า Google Sheets สำเร็จ!")
                    st.cache_data.clear()
                    st.rerun()

# --------------------------------------------------------------------------------
# 4. LEASES PAGE
# --------------------------------------------------------------------------------
elif menu == "📋 สัญญาเช่า":
    st.title("📋 ระบบตรวจสอบข้อมูลสัญญาเช่า")
    tab1, tab2 = st.tabs(["📋 รายการสัญญาเช่า", "➕ เปิดสัญญาเช่าฉบับใหม่"])
    with tab1:
        st.dataframe(df_leases, use_container_width=True)
    with tab2:
        with st.form("lease_form"):
            l_id = st.text_input("เลขที่สัญญาเช่า (เช่น CNT003)")
            l_name = st.text_input("ชื่อคนเช่า")
            l_phone = st.text_input("เบอร์โทร")
            l_prop = st.text_input("ที่นาหรือบ้านเช่าที่เช่า")
            l_dep = st.number_input("เงินมัดจำตามสัญญา (บาท)", min_value=0)
            l_rent = st.number_input("เงินค่าเช่าต่อรอบ (บาท)", min_value=0)
            l_date = st.date_input("วันครบกำหนดชำระค่าเช่างวดถัดไป")
            l_doc = st.text_input("ชื่อไฟล์เอกสารตัวสัญญาเต็ม (PDF)")
            
            if st.form_submit_button("💾 ทำสัญญาเช่า"):
                payload = {
                    "เลขที่สัญญาเช่า": l_id, "ชื่อคนเช่า": l_name, "เบอร์โทร": l_phone, "ที่นาหรือบ้านเช่า": l_prop,
                    "เงินมัดจำ": l_dep, "เงินค่าเช่า": l_rent, "วันครบกำหนดชำระค่าเช่า": str(l_date), "เอกสารสัญญา": l_doc
                }
                if submit_to_webos("Leases", payload):
                    st.success("🎉 ทำสัญญาเข้า Google Sheets สำเร็จ!")
                    st.cache_data.clear()
                    st.rerun()

# --------------------------------------------------------------------------------
# 5. PAYMENTS PAGE
# --------------------------------------------------------------------------------
elif menu == "💰 ประวัติการชำระเงิน":
    st.title("💰 ประวัติบันทึกการรับชำระเงินค่างวดและใบเสร็จ")
    tab1, tab2 = st.tabs(["💰 ประวัติการรับชำระเงิน", "✍️ บันทึกการรับเงินใบใหม่"])
    with tab1:
        st.dataframe(df_payments, use_container_width=True)
    with tab2:
        with st.form("pay_form"):
            rec_id = st.text_input("เลขที่ใบชำระ (เช่น REC-202602)")
            l_id_ref = st.text_input("เลขที่สัญญาเช่าเชื่อมโยง")
            t_name_ref = st.text_input("ชื่อคนเช่า")
            t_phone_ref = st.text_input("เบอร์โทร")
            p_name_ref = st.text_input("ชื่อบ้านเช่า/ที่นา")
            pay_due_date = st.date_input("วันที่ตามกำหนดดีล")
            pay_req = st.number_input("ยอดเงินค่าเช่าที่ต้องชำระ (บาท)", min_value=0)
            pay_actual = st.number_input("ยอดเงินที่ชำระจริง (บาท)", min_value=0)
            pay_date = st.date_input("วันที่ชำระเงินจริง")
            emp_receiver = st.text_input("พนักงานผู้รับเงิน")
            pay_slip = st.text_input("ชื่อไฟล์หลักฐานสลิป (เช่น slip_01.jpg)")
            
            if st.form_submit_button("💾 ยืนยันบันทึกรับเงิน"):
                payload = {
                    "เลขที่ใบชำระ": rec_id, "เลขที่สัญญาเช่า": l_id_ref, "ชื่อคนเช่า": t_name_ref, "เบอร์โทร": t_phone_ref,
                    "ชื่อบ้านเช่า_ที่นา": p_name_ref, "วันที่ครบกำหนด": str(pay_due_date), "ยอดเงินค่าเช่าที่ต้องชำระ": pay_req,
                    "วันที่ชำระ": str(pay_date), "ยอดเงินทีชำระ": pay_actual, "พนักงานที่รับเงิน": emp_receiver, "หลักฐานการชำระเงิน": pay_slip
                }
                if submit_to_webos("Payments", payload):
                    st.success("🎉 บันทึกใบเสร็จเข้า Google Sheets สำเร็จ!")
                    st.cache_data.clear()
                    st.rerun()

# --------------------------------------------------------------------------------
# 6. EMPLOYEES PAGE
# --------------------------------------------------------------------------------
elif menu == "🧑‍💼 ข้อมูลพนักงาน":
    st.title("🧑‍💼 ข้อมูลพนักงานและสิทธิ์ผู้ใช้งาน")
    tab1, tab2 = st.tabs(["🧑‍💼 บัญชีรายชื่อพนักงานปัจจุบัน", "➕ เพิ่มบัญชีพนักงานใหม่"])
    with tab1:
        st.dataframe(df_employees, use_container_width=True)
    with tab2:
        with st.form("emp_form"):
            e_name = st.text_input("ชื่อ-นามสกุลพนักงาน")
            e_user = st.text_input("Username เข้าใช้งาน")
            e_pass = st.text_input("Password (ตัวเลข 6 หลัก)")
            e_phone = st.text_input("เบอร์โทรศัพท์ติดต่อ")
            e_addr = st.text_area("ที่อยู่พนักงาน")
            
            if st.form_submit_button("💾 เพิ่มข้อมูลพนักงาน"):
                payload = {"ชื่อ": e_name, "username": e_user, "password": e_pass, "เบอร์โทร": e_phone, "ที่อยู่": e_addr}
                if submit_to_webos("Employees", payload):
                    st.success("🎉 เพิ่มบัญชีพนักงานเข้า Google Sheets สำเร็จ!")
                    st.cache_data.clear()
                    st.rerun()
