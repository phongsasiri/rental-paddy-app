import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import os

# Set page config
st.set_page_config(
    page_title="ระบบจัดการที่นาและบ้านเช่า (Ricefield & Property Management)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern design and Thai fonts
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
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
# GOOGLE SHEETS CONNECTION INITIALIZATION
# --------------------------------------------------------------------------------
# แหล่งข้อมูล Google Sheets ที่เชื่อมต่อ
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1rOuS3DH6cLMYf0841LrwYcoNsa8IQFLUkxKRg-Kht90/edit?gid=1501708046#gid=1501708046"

def get_sheet_csv_url(sheet_name):
    # ฟังก์ชันแปลงลิงก์ Google Sheet เป็นลิงก์สำหรับดึง CSV แยกตามชื่อ Sheet (ต้องกดแชร์ให้ทุกคนมีสิทธิ์อ่านลิงก์)
    base_url = "https://docs.google.com/spreadsheets/d/1rOuS3DH6cLMYf0841LrwYcoNsa8IQFLUkxKRg-Kht90/gviz/tq?tqx=out:csv&sheet="
    return f"{base_url}{sheet_name}"

@st.cache_data(ttl=10)
def load_all_data_from_sheets():
    # โหลดข้อมูลจาก Google Sheets หากเกิดข้อผิดพลาดจะใช้ข้อมูลจำลอง (Fallback)
    try:
        properties = pd.read_csv(get_sheet_csv_url("properties"))
        # แปลงวันที่
        if "วันครบชำระภาษี" in properties.columns:
            properties["วันครบชำระภาษี"] = pd.to_datetime(properties["วันครบชำระภาษี"]).dt.date
    except Exception:
        properties = pd.DataFrame([
            {"id": "P001", "ชื่อที่ดิน": "ที่นาแปลงเอก A", "ประเภท": "ที่นา", "สถานะ": "มีคนเช่า", "ผู้เช่าปัจจุบัน": "นายสมชาย ดีใจ", "ประเภทการเช่า": "หลังเก็บเกี่ยว", "เงินมัดจำ": 5000, "ค่าเช่า": 12000, "พิกัด": "17.6242, 100.0956", "วันครบชำระภาษี": (datetime.now() + timedelta(days=15)).date(), "สถานะภาษี": "ยังไม่ได้ชำระ", "รูปภาพ": "['นาแปลงA_1.jpg']", "เอกสาร": "โฉนด_แปลงA.pdf"},
            {"id": "P002", "ชื่อที่ดิน": "บ้านเช่า สุขใจ ซอย 3", "ประเภท": "บ้านเช่า", "สถานะ": "มีคนเช่า", "ผู้เช่าปัจจุบัน": "นางมณี ตั้งใจ", "ประเภทการเช่า": "รายเดือน", "เงินมัดจำ": 6000, "ค่าเช่า": 3500, "พิกัด": "17.6311, 100.0922", "วันครบชำระภาษี": (datetime.now() - timedelta(days=5)).date(), "สถานะภาษี": "ยังไม่ได้ชำระ", "รูปภาพ": "['บ้านสุขใจ.jpg']", "เอกสาร": "สัญญาซื้อขาย_บ้านสุขใจ.pdf"},
            {"id": "P003", "ชื่อที่ดิน": "ที่นาท้ายหมู่บ้าน แปลง B", "ประเภท": "ที่นา", "สถานะ": "ว่าง", "ผู้เช่าปัจจุบัน": "-", "ประเภทการเช่า": "เก็บก่อนทำ (รายปี)", "เงินมัดจำ": 0, "ค่าเช่า": 8000, "พิกัด": "17.6190, 100.1001", "วันครบชำระภาษี": (datetime.now() + timedelta(days=60)).date(), "สถานะภาษี": "ชำระแล้ว", "รูปภาพ": "[]", "เอกสาร": ""},
            {"id": "P004", "ชื่อที่ดิน": "บ้านเช่าเรือนไทย แปลง C", "ประเภท": "บ้านเช่า", "สถานะ": "ว่าง", "ผู้เช่าปัจจุบัน": "-", "ประเภทการเช่า": "รายเดือน", "เงินมัดจำ": 10000, "ค่าเช่า": 5000, "พิกัด": "17.6255, 100.0888", "วันครบชำระภาษี": (datetime.now() + timedelta(days=120)).date(), "สถานะภาษี": "ชำระแล้ว", "รูปภาพ": "[]", "เอกสาร": ""}
        ])

    try:
        employees = pd.read_csv(get_sheet_csv_url("employees"))
    except Exception:
        employees = pd.DataFrame([
            {"ชื่อ": "สมศรี ขยันงาน", "username": "somsri01", "password": "123456", "เบอร์โทร": "081-111-2222", "ที่อยู่": "123 ม.1 ต.ในเมือง อ.เมือง จ.อุตรดิตถ์"},
            {"ชื่อ": "สมบัต มั่นคง", "username": "sombat02", "password": "654321", "เบอร์โทร": "082-222-3333", "ที่อยู่": "45/6 ต.ท่าอิฐ อ.เมือง จ.อุตรดิตถ์"}
        ])

    try:
        tenants = pd.read_csv(get_sheet_csv_url("tenants"))
    except Exception:
        tenants = pd.DataFrame([
            {"ชื่อ": "นายสมชาย ดีใจ", "ที่อยู่": "99 ม.4 ต.ป่าเซ่า อ.เมือง จ.อุตรดิตถ์", "เบอร์โทร": "089-765-4321", "เอกสาร": "['บัตรประชาชน_สมชาย.pdf']", "สัญญาผูกพัน": "CNT001"},
            {"ชื่อ": "นางมณี ตั้งใจ", "ที่อยู่": "88/1 ถ.ชื่นฤดี ต.ท่าอิฐ อ.เมือง จ.อุตรดิตถ์", "เบอร์โทร": "086-543-2109", "เอกสาร": "['บัตรประชาชน_มณี.pdf']", "สัญญาผูกพัน": "CNT002"}
        ])

    try:
        leases = pd.read_csv(get_sheet_csv_url("leases"))
        if "วันครบกำหนดชำระค่าเช่า" in leases.columns:
            leases["วันครบกำหนดชำระค่าเช่า"] = pd.to_datetime(leases["วันครบกำหนดชำระค่าเช่า"]).dt.date
    except Exception:
        leases = pd.DataFrame([
            {"เลขที่สัญญาเช่า": "CNT001", "ชื่อคนเช่า": "นายสมชาย ดีใจ", "เบอร์โทร": "089-765-4321", "ที่นาหรือบ้านเช่า": "ที่นาแปลงเอก A", "เงินมัดจำ": 5000, "เงินค่าเช่า": 12000, "วันครบกำหนดชำระค่าเช่า": (datetime.now() - timedelta(days=5)).date(), "เอกสารสัญญา": "สัญญาเช่าที่นา_สมชาย.pdf"},
            {"เลขที่สัญญาเช่า": "CNT002", "ชื่อคนเช่า": "นางมณี ตั้งใจ", "เบอร์โทร": "086-543-2109", "ที่นาหรือบ้านเช่า": "บ้านเช่า สุขใจ ซอย 3", "เงินมัดจำ": 6000, "เงินค่าเช่า": 3500, "วันครบกำหนดชำระค่าเช่า": (datetime.now() - timedelta(days=2)).date(), "เอกสารสัญญา": "สัญญาเช่าบ้าน_มณี.pdf"}
        ])

    try:
        payments = pd.read_csv(get_sheet_csv_url("payments"))
        if "วันที่ครบกำหนด" in payments.columns:
            payments["วันที่ครบกำหนด"] = pd.to_datetime(payments["วันที่ครบกำหนด"]).dt.date
        if "วันที่ชำระ" in payments.columns:
            payments["วันที่ชำระ"] = pd.to_datetime(payments["วันที่ชำระ"]).dt.date
    except Exception:
        payments = pd.DataFrame([
            {"เลขที่ใบชำระ": "REC-20260701", "เลขที่สัญญาเช่า": "CNT001", "ชื่อคนเช่า": "นายสมชาย ดีใจ", "เบอร์โทร": "089-765-4321", "ชื่อบ้านเช่า_ที่นา": "ที่นาแปลงเอก A", "วันที่ครบกำหนด": (datetime.now() - timedelta(days=65)).date(), "ยอดเงินค่าเช่าที่ต้องชำระ": 12000, "วันที่ชำระ": (datetime.now() - timedelta(days=65)).date(), "ยอดเงินทีชำระ": 12000, "พนักงานที่รับเงิน": "สมศรี ขยันงาน", "หลักฐานการชำระเงิน": "slip_harvest1.jpg"}
        ])

    return properties, employees, tenants, leases, payments

def save_to_google_sheets_notice():
    # แสดงคู่มือการบันทึกข้อมูลกลับไปยัง Google Sheets โดยใช้ streamlit-gsheets connection หรือกูเกิลฟอร์ม/Web App URL
    st.info("""
    💡 **คำแนะนำในการเปิดสิทธิ์บันทึกข้อมูลแบบ Write-back ไปยัง Google Sheets:**
    เนื่องจากการเขียนไฟล์กลับ (Write) ลงกูเกิลชีทโดยตรงผ่านเซิร์ฟเวอร์สาธารณะ ต้องอาศัย Service Account Credential หรือการตั้งค่า `st.connection("gsheets", type=GSheetsConnection)` ในระบบ Streamlit Community Cloud (Secrets) 
    
    **วิธีการตั้งค่าหลังนำโค้ดนี้ไปรัน:**
    1. สร้างไฟล์ `.streamlit/secrets.toml` ในโปรเจกต์ของคุณ
    2. ใส่ข้อมูลพินและคีย์เชื่อมต่อของ Google Service Account ของคุณลงไป
    3. เปิดใช้งานสิทธิ์ของชีทให้เป็น 'Anyone with the link can edit' 
    """)

# ดึงข้อมูลจาก Sheets ลง session state
if 'initialized' not in st.session_state:
    p, e, t, l, pay = load_all_data_from_sheets()
    st.session_state.properties = p
    st.session_state.employees = e
    st.session_state.tenants = t
    st.session_state.leases = l
    st.session_state.payments = pay
    st.session_state.initialized = True

# --------------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------------------------------------
st.sidebar.title("🌾 Ricefield & Property")
st.sidebar.subheader("ระบบจัดการค่าเช่าและที่ดิน")
menu = st.sidebar.radio(
    "เมนูการใช้งาน",
    ["🏠 หน้าแรก (Dashboard)", "🌾 ข้อมูลที่ดิน/บ้านเช่า", "👥 ข้อมูลผู้เช่า", "📋 สัญญาเช่า", "💰 บันทึกการชำระเงิน", "🧑‍💼 ข้อมูลพนักงาน"]
)

st.sidebar.info(
    f"🔗 **แหล่งข้อมูลที่เชื่อมต่อ**\n"
    f"📊 [Google Sheets Database]({GOOGLE_SHEET_URL})\n"
    f"📁 [Google Drive Storage](https://drive.google.com/drive/folders/14i1bb-NlhXDm2ybnTnfIzQexsoLPttnA)"
)

# --------------------------------------------------------------------------------
# 1. DASHBOARD PAGE
# --------------------------------------------------------------------------------
if menu == "🏠 หน้าแรก (Dashboard)":
    st.title("📊 หน้าแรก / แผงควบคุมระบบ (Dashboard)")
    save_to_google_sheets_notice()
    
    # Row 1: Metrics & Analytics
    col1, col2, col3 = st.columns([1, 1.5, 1.5])
    
    with col1:
        st.subheader("สถานะว่าง/มีคนเช่า")
        df_prop = st.session_state.properties
        vacant_count = len(df_prop[df_prop["สถานะ"] == "ว่าง"])
        occupied_count = len(df_prop[df_prop["สถานะ"] == "มีคนเช่า"])
        
        fig = px.pie(
            names=["ว่าง", "มีคนเช่า"],
            values=[vacant_count, occupied_count],
            color=["ว่าง", "มีคนเช่า"],
            color_discrete_map={"ว่าง": "#cbd5e1", "มีคนเช่า": "#28a745"},
            hole=0.4
        )
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=220)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"<div style='text-align:center; font-weight:bold;'>ทรัพย์สินว่างอยู่ {vacant_count} รายการ</div>", unsafe_allow_html=True)

    with col2:
        st.subheader("⚠️ แจ้งเตือนสิทธิ/ภาษีและภารกิจเร่งด่วน")
        unpaid_tax_count = len(df_prop[df_prop["สถานะภาษี"] == "ยังไม่ได้ชำระ"])
        if unpaid_tax_count > 0:
            st.markdown(f'<div class="tax-alert">💸 มีที่ดิน/บ้านเช่าที่ยังไม่ได้ชำระภาษีสะสม: {unpaid_tax_count} แปลง!</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:green; font-weight:bold;">✅ ชำระภาษีครบถ้วนทุกแปลง</div>', unsafe_allow_html=True)
            
        st.markdown("🚨 **ระบบตรวจจับการทำนารอบใหม่ (หลังชำระเงิน 2 เดือน)**")
        harvest_payments = st.session_state.payments[st.session_state.payments["ชื่อบ้านเช่า_ที่นา"].isin(
            df_prop[df_prop["ประเภทการเช่า"] == "หลังเก็บเกี่ยว"]["ชื่อที่ดิน"]
        )]
        
        alert_triggered = False
        for idx, row in harvest_payments.iterrows():
            pay_date = pd.to_datetime(row["วันที่ชำระ"])
            days_passed = (datetime.now() - pay_date).days
            if days_passed >= 60:
                alert_triggered = True
                st.markdown(
                    f'<div class="inspection-alert">'
                    f'⏰ <b>แจ้งลงพื้นที่ตรวจนา:</b> {row["ชื่อบ้านเช่า_ที่นา"]} (ผู้เช่า: {row["ชื่อคนเช่า"]})<br>'
                    f'ชำระค่าเช่าหลังเก็บเกี่ยวไปแล้ว {days_passed} วัน (> 2 เดือน) กรุณาลงตรวจว่ามีการเริ่มทำนารอบใหม่หรือไม่'
                    f'<br><button style="margin-top:5px; border-radius:4px; border:none; padding:3px 8px;">✅ ลงตรวจแล้ว/เริ่มรอบใหม่</button>'
                    f'</div>', 
                    unsafe_allow_html=True
                )
        if not alert_triggered:
            st.write("ไม่มีนัดหมายลงตรวจแปลงนาในระยะนี้")

    with col3:
        st.subheader("💡 รายชื่อผู้เช่าค้างชำระค่าเช่า")
        overdue_leases = st.session_state.leases[st.session_state.leases["วันครบกำหนดชำระค่าเช่า"] < datetime.now().date()]
        if not overdue_leases.empty:
            for idx, row in overdue_leases.iterrows():
                st.error(f"❌ {row['ชื่อคนเช่า']} | ค้างชำระ: {row['ที่นาหรือบ้านเช่า']} | ยอด: {row['เงินค่าเช่า']:,} บาท (กำหนด: {row['วันครบกำหนดชำระค่าเช่า']})")
        else:
            st.success("🎉 ไม่มีผู้เช่าค้างชำระในระบบขณะนี้")

    st.subheader("📋 ตารางสรุปรายการค้างชำระเงินทั้งหมด")
    if not overdue_leases.empty:
        st.dataframe(overdue_leases[["เลขที่สัญญาเช่า", "ชื่อคนเช่า", "เบอร์โทร", "ที่นาหรือบ้านเช่า", "เงินค่าเช่า", "วันครบกำหนดชำระค่าเช่า"]], use_container_width=True)
    else:
        st.write("ไม่มีข้อมูลรายการค้างชำระ")

# --------------------------------------------------------------------------------
# 2. PROPERTY MANAGEMENT PAGE
# --------------------------------------------------------------------------------
elif menu == "🌾 ข้อมูลที่ดิน/บ้านเช่า":
    st.title("🌾 รายละเอียดที่ดินและบ้านเช่า")
    
    tab1, tab2 = st.tabs(["📝 รายการทรัพย์สินทั้งหมด", "➕ เพิ่ม/แก้ไขข้อมูล"])
    
    with tab1:
        st.dataframe(st.session_state.properties, use_container_width=True)
        
    with tab2:
        with st.form("property_form"):
            st.write("### กรอกรายละเอียดทรัพย์สินใหม่")
            p_name = st.text_input("ชื่อที่ดิน/บ้านเช่า")
            p_type = st.selectbox("ประเภท", ["บ้านเช่า", "ที่นา"])
            p_status = st.selectbox("สถานะ", ["ว่าง", "มีคนเช่า"])
            p_tenant = st.text_input("ถ้ามีคนเช่า ใครเป็นคนเช่า", value="-")
            p_rent_type = st.selectbox("ประเภทการเช่า", ["รายเดือน", "รายปี", "หลังเก็บเกี่ยว", "เก็บก่อนทำ (รายปี)"])
            
            c1, c2 = st.columns(2)
            p_deposit = c1.number_input("เงินมัดจำ (บาท)", min_value=0)
            p_rent = c2.number_input("ค่าเช่า (บาท)", min_value=0)
            
            p_geo = st.text_input("พิกัดตำแหน่งที่ดิน (เช่น Lat, Long หรือ Link Maps)")
            p_tax_date = st.date_input("วันครบชำระภาษีที่ดิน")
            p_tax_status = st.selectbox("สถานะภาษี", ["ยังไม่ได้ชำระ", "ชำระแล้ว"])
            
            st.file_uploader("🖼️ อัปโหลดรูปที่ดิน (สามารถเลือกได้หลายไฟล์)", accept_multiple_files=True)
            st.file_uploader("📄 อัพเอกสารสัญญา/โฉนด (PDF)")
            
            submitted = st.form_submit_button("💾 บันทึกข้อมูลทรัพย์สิน")
            if submitted:
                new_data = {
                    "id": f"P00{len(st.session_state.properties)+1}", "ชื่อที่ดิน": p_name, "ประเภท": p_type,
                    "สถานะ": p_status, "ผู้เช่าปัจจุบัน": p_tenant, "ประเภทการเช่า": p_rent_type,
                    "เงินมัดจำ": p_deposit, "ค่าเช่า": p_rent, "พิกัด": p_geo, "วันครบชำระภาษี": p_tax_date,
                    "สถานะภาษี": p_tax_status, "รูปภาพ": "[]", "เอกสาร": ""
                }
                st.session_state.properties = pd.concat([st.session_state.properties, pd.DataFrame([new_data])], ignore_index=True)
                st.success("บันทึกข้อมูลเรียบร้อยแล้ว! (ระบบบันทึกจำลองใน Session State เรียบร้อย)")
                st.rerun()

# --------------------------------------------------------------------------------
# 3. TENANT MANAGEMENT PAGE
# --------------------------------------------------------------------------------
elif menu == "👥 ข้อมูลผู้เช่า":
    st.title("👥 ระบบจัดการข้อมูลผู้เช่า")
    st.dataframe(st.session_state.tenants, use_container_width=True)
    
    with st.expander("➕ เพิ่มรายชื่อผู้เช่าใหม่"):
        with st.form("tenant_form"):
            t_name = st.text_input("ชื่อ-นามสกุล")
            t_address = st.text_area("ที่อยู่ตามทะเบียนบ้าน/ติดต่อ")
            t_phone = st.text_input("เบอร์โทรศัพท์")
            st.file_uploader("📄 แนบเอกสารตรวจสอบสิทธิ์ (เช่น สำเนาบัตรประชาชน)")
            
            t_submit = st.form_submit_button("💾 เพิ่มผู้เช่า")
            if t_submit:
                new_t = {"ชื่อ": t_name, "ที่อยู่": t_address, "เบอร์โทร": t_phone, "เอกสาร": "[]", "สัญญาผูกพัน": "-"}
                st.session_state.tenants = pd.concat([st.session_state.tenants, pd.DataFrame([new_t])], ignore_index=True)
                st.success("เพิ่มข้อมูลผู้เช่าสำเร็จ!")
                st.rerun()

# --------------------------------------------------------------------------------
# 4. LEASE AGREEMENT PAGE
# --------------------------------------------------------------------------------
elif menu == "📋 สัญญาเช่า":
    st.title("📋 ระบบลงบันทึกสัญญาเช่า")
    st.dataframe(st.session_state.leases, use_container_width=True)
    
    with st.expander("➕ ทำสัญญาเช่าฉบับใหม่"):
        with st.form("lease_form"):
            l_id = st.text_input("เลขที่สัญญาเช่า", value=f"CNT00{len(st.session_state.leases)+1}")
            l_tenant = st.selectbox("เลือกผู้เช่า", st.session_state.tenants["ชื่อ"].tolist())
            l_prop = st.selectbox("เลือกที่ดิน/บ้านเช่า", st.session_state.properties[st.session_state.properties["สถานะ"]=="ว่าง"]["ชื่อที่ดิน"].tolist() if any(st.session_state.properties["สถานะ"]=="ว่าง") else st.session_state.properties["ชื่อที่ดิน"].tolist())
            
            l_dep = st.number_input("เงินมัดจำตามสัญญา (บาท)")
            l_rent = st.number_input("เงินค่าเช่าต่อรอบ (บาท)")
            l_due = st.date_input("วันครบกำหนดชำระค่าเช่างวดแรก/ถัดไป")
            st.file_uploader("📄 อัพโหลดไฟล์เอกสารตัวสัญญาเต็ม (PDF)")
            
            l_submit = st.form_submit_button("บันทึกสัญญาเช่า")
            if l_submit:
                phone = st.session_state.tenants[st.session_state.tenants["ชื่อ"]==l_tenant]["เบอร์โทร"].values[0]
                new_l = {
                    "เลขที่สัญญาเช่า": l_id, "ชื่อคนเช่า": l_tenant, "เบอร์โทร": phone, 
                    "ที่นาหรือบ้านเช่า": l_prop, "เงินมัดจำ": l_dep, "เงินค่าเช่า": l_rent, 
                    "วันครบกำหนดชำระค่าเช่า": l_due, "เอกสารสัญญา": ""
                }
                st.session_state.leases = pd.concat([st.session_state.leases, pd.DataFrame([new_l])], ignore_index=True)
                st.session_state.properties.loc[st.session_state.properties["ชื่อที่ดิน"] == l_prop, "สถานะ"] = "มีคนเช่า"
                st.session_state.properties.loc[st.session_state.properties["ชื่อที่ดิน"] == l_prop, "ผู้เช่าปัจจุบัน"] = l_tenant
                st.success("บันทึกข้อมูลสัญญาเช่าเรียบร้อยแล้ว!")
                st.rerun()

# --------------------------------------------------------------------------------
# 5. PAYMENT ENTRY PAGE
# --------------------------------------------------------------------------------
elif menu == "💰 บันทึกการชำระเงิน":
    st.title("💰 ระบบบันทึกการชำระเงินค่างวดและออกใบเสร็จ")
    st.dataframe(st.session_state.payments, use_container_width=True)
    
    st.write("---")
    st.subheader("✍️ บันทึกการชำระเงินใบใหม่ (Auto-fill Connected)")
    
    lease_ids = st.session_state.leases["เลขที่สัญญาเช่า"].tolist()
    selected_lease = st.selectbox("เลือกเลขที่สัญญาเช่าเชื่องโยงข้อมูล", ["-- เลือกใบสัญญา --"] + lease_ids)
    
    if selected_lease != "-- เลือกใบสัญญา --":
        lease_row = st.session_state.leases[st.session_state.leases["เลขที่สัญญาเช่า"] == selected_lease].iloc[0]
        
        c1, c2, c3 = st.columns(3)
        c1.text_input("ชื่อคนเช่า", value=lease_row["ชื่อคนเช่า"], disabled=True)
        c2.text_input("เบอร์โทร", value=lease_row["เบอร์โทร"], disabled=True)
        c3.text_input("ชื่อทรัพย์สินเช่า", value=lease_row["ที่นาหรือบ้านเช่า"], disabled=True)
        
        c4, c5 = st.columns(2)
        c4.text_input("วันครบกำหนดตามดีล", value=str(lease_row["วันครบกำหนดชำระค่าเช่า"]), disabled=True)
        c5.number_input("ยอดเงินค่าเช่าที่ต้องชำระ (บาท)", value=float(lease_row["เงินค่าเช่า"]), disabled=True)
        
        with st.form("pay_form"):
            rec_id = st.text_input("เลขที่ใบชำระเงิน", value=f"REC-2026{len(st.session_state.payments)+1:02d}")
            pay_actual = st.number_input("ยอดเงินที่ชำระจริง (สามารถปรับได้ตามผลผลิตหน้างานสำหรับที่นา)", value=float(lease_row["เงินค่าเช่า"]))
            pay_date = st.date_input("วันที่ชำระเงินจริง")
            emp_receiver = st.selectbox("พนักงานผู้รับเงิน", st.session_state.employees["ชื่อ"].tolist())
            st.file_uploader("📸 แนบหลักฐานการโอนเงิน/สลิปธนาคาร")
            
            pay_submit = st.form_submit_button("💾 ยืนยันบันทึกการรับชำระและออกใบเสร็จ")
            if pay_submit:
                new_p = {
                    "เลขที่ใบชำระ": rec_id, "เลขที่สัญญาเช่า": selected_lease, "ชื่อคนเช่า": lease_row["ชื่อคนเช่า"], 
                    "เบอร์โทร": lease_row["เบอร์โทร"], "ชื่อบ้านเช่า_ที่นา": lease_row["ที่นาหรือบ้านเช่า"], 
                    "วันที่ครบกำหนด": lease_row["วันครบกำหนดชำระค่าเช่า"], "ยอดเงินค่าเช่าที่ต้องชำระ": lease_row["เงินค่าเช่า"],
                    "วันที่ชำระ": pay_date, "ยอดเงินทีชำระ": pay_actual, "พนักงานที่รับเงิน": emp_receiver, "หลักฐานการชำระเงิน": "uploaded_slip.jpg"
                }
                st.session_state.payments = pd.concat([st.session_state.payments, pd.DataFrame([new_p])], ignore_index=True)
                st.session_state.leases.loc[st.session_state.leases["เลขที่สัญญาเช่า"] == selected_lease, "วันครบกำหนดชำระค่าเช่า"] = lease_row["วันครบกำหนดชำระค่าเช่า"] + timedelta(days=30)
                st.success("👍 บันทึกรับเงินเข้าคลังสำเร็จ")
                st.rerun()

# --------------------------------------------------------------------------------
# 6. EMPLOYEE MANAGEMENT PAGE
# --------------------------------------------------------------------------------
elif menu == "🧑‍💼 ข้อมูลพนักงาน":
    st.title("🧑‍💼 ข้อมูลพนักงานและสิทธิ์ผู้ใช้งาน")
    st.dataframe(st.session_state.employees, use_container_width=True)
    
    with st.expander("➕ เพิ่มบัญชีผู้ดูแล/พนักงานใหม่"):
        with st.form("emp_form"):
            e_name = st.text_input("ชื่อ-นามสกุลพนักงาน")
            e_user = st.text_input("Username เข้าใช้งาน")
            e_pass = st.text_input("Password (ต้องระบุเป็นตัวเลข 6 หลักเท่านั้น)", max_chars=6, help="ใส่ตัวเลข 6 ตัวในการกดบันทึก")
            e_phone = st.text_input("เบอร์โทรศัพท์ติดต่อ")
            e_addr = st.text_area("ที่อยู่พนักงาน")
            
            e_submit = st.form_submit_button("💾 เพิ่มข้อมูลพนักงาน")
            if e_submit:
                if not e_pass.isdigit() or len(e_pass) != 6:
                    st.error("❌ บันทึกไม่สำเร็จ: รหัสผ่านของคุณต้องประกอบด้วย 'ตัวเลขเท่านั้นความยาว 6 หลัก'")
                else:
                    new_e = {"ชื่อ": e_name, "username": e_user, "password": e_pass, "เบอร์โทร": e_phone, "ที่อยู่": e_addr}
                    st.session_state.employees = pd.concat([st.session_state.employees, pd.DataFrame([new_e])], ignore_index=True)
                    st.success("บันทึกประวัติพนักงานรายใหม่สำเร็จ!")
                    st.rerun()
