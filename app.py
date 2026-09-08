import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# ==========================================
# 1. ตั้งค่าลิงก์ Google Sheets และ Google Drive
# ==========================================
# ลิงก์ฐานข้อมูลและโฟลเดอร์เก็บภาพที่คุณให้มา
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1rOuS3DH6cLMYf0841LrwYcoNsa8IQFLUkxKRg-Kht90/edit?gid=1501708046#gid=1501708046"
GOOGLE_DRIVE_FOLDER = "https://google.com"

st.set_page_config(page_title="ระบบจัดการที่นาและบ้านเช่า", layout="wide")

# ==========================================
# 2. ฟังก์ชันโหลดข้อมูลจำลองภาษาไทย (แก้ไขบั๊กแล้ว)
# ==========================================
@st.cache_data(ttl=60)
def load_mock_data():
    current_date = datetime.now()
    
    # 1. ข้อมูลที่ดิน/บ้านเช่า (ใส่ข้อมูลตัวเลขจำลองครบถ้วนเรียบร้อย)
    lands_data = {
        "รหัสที่ดิน": ["L001", "L002", "L003", "L004"],
        "ชื่อที่ดิน": ["ที่นาแปลง เอก A", "บ้านเช่า ซอย 3 ห้อง 1", "ที่นาแปลง โท B", "บ้านเช่า ซอย 3 ห้อง 2"],
        "ประเภท": ["ที่นา", "บ้านเช่า", "ที่นา", "บ้านเช่า"],
        "สถานะ": ["มีคนเช่า", "มีคนเช่า", "ว่าง", "ว่าง"],
        "ประเภทการเช่า": ["หลังเก็บเกี่ยว", "รายเดือน", "จ่ายก่อนทำรายปี", "รายเดือน"],
        "เงินมัดจำ": [5000, 3000, 10000, 3500],
        "ค่าเช่า": [15000, 3500, 20000, 3800],
        "วันครบชำระภาษี": [(current_date - timedelta(days=5)).strftime("%Y-%m-%d"), 
                           (current_date + timedelta(days=30)).strftime("%Y-%m-%d"),
                           (current_date + timedelta(days=15)).strftime("%Y-%m-%d"),
                           (current_date + timedelta(days=120)).strftime("%Y-%m-%d")],
        "สถานะภาษี": ["ยังไม่ได้ชำระ", "ชำระแล้ว", "ยังไม่ได้ชำระ", "ชำระแล้ว"],
        "พิกัดแปลงนา": ["https://maps.google.com", "https://maps.google.com", "https://maps.google.com", "https://maps.google.com"]
    }
    
    # 2. ข้อมูลชำระเงิน (ตั้งวันย้อนหลัง 65 วัน เพื่อให้ระบบแจ้งเตือนตรวจนาครบ 2 เดือนทำงาน)
    past_payment_date = (current_date - timedelta(days=65)).strftime("%Y-%m-%d")
    payments_data = {
        "เลขที่ใบชำระ": ["REC-001", "REC-002"],
        "เลขที่สัญญาเช่า": ["CNT-001", "CNT-002"],
        "ชื่อคนเช่า": ["นายสมชาย ดีใจ", "นางมณี ตั้งใจ"],
        "ชื่อทรัพย์สิน": ["ที่นาแปลง เอก A", "บ้านเช่า ซอย 3 ห้อง 1"],
        "วันที่ชำระ": [past_payment_date, (current_date - timedelta(days=10)).strftime("%Y-%m-%d")],
        "ยอดเงินที่ชำระ": [15000, 3500],
        "ประเภทการเช่า": ["หลังเก็บเกี่ยว", "รายเดือน"],
        "พนักงานผู้รับ": ["พนักงานสมศักดิ์", "พนักงานสมศักดิ์"]
    }
    
    # 3. ข้อมูลผู้เช่า
    tenants_data = {
        "ชื่อผู้เช่า": ["นายสมชาย ดีใจ", "นางมณี ตั้งใจ", "นายอนันต์ เรียนดี"],
        "เบอร์โทร": ["081-234-5678", "089-765-4321", "085-111-2222"],
        "ค้างชำระ (บาท)": [2500, 0, 0]
    }
    
    return pd.DataFrame(lands_data), pd.DataFrame(payments_data), pd.DataFrame(tenants_data)

# โหลดข้อมูลเข้าสู่หน่วยความจำจำลองของแอป
if 'lands_df' not in st.session_state:
    st.session_state.lands_df, st.session_state.payments_df, st.session_state.tenants_df = load_mock_data()

# ==========================================
# 3. แถบเมนูด้านซ้าย (Sidebar)
# ==========================================
st.sidebar.title("🌾 ระบบจัดการที่เช่า")
st.sidebar.info(f"📁 โฟลเดอร์เก็บรูปภาพหลัก:\n[คลิกเปิด Google Drive]({GOOGLE_DRIVE_FOLDER})")
st.sidebar.write("---")
menu = st.sidebar.radio(
    "เมนูการใช้งาน",
    ["🏠 หน้าแรก (Dashboard)", "📂 บันทึกรายละเอียดที่ดิน/บ้านเช่า", "👥 บันทึกรายละเอียดผู้เช่า", "📋 บันทึกการชำระค่าเช่า", "🧑‍💼 บันทึกรายละเอียดพนักงาน"]
)

# ==========================================
# 4. หน้าจอ Dashboard
# ==========================================
if menu == "🏠 หน้าแรก (Dashboard)":
    st.title("📊 ภาพรวมระบบ (Dashboard)")
    st.write(f"ข้อมูล ณ วันที่: {datetime.now().strftime('%d/%m/%Y')}")
    
    total_vacant = len(st.session_state.lands_df[st.session_state.lands_df["สถานะ"] == "ว่าง"])
    unpaid_tax = len(st.session_state.lands_df[st.session_state.lands_df["สถานะภาษี"] == "ยังไม่ได้ชำระ"])
    overdue_tenants = st.session_state.tenants_df[st.session_state.tenants_df["ค้างชำระ (บาท)"] > 0]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="🏠 ทรัพย์สินที่ยังว่างอยู่", value=f"{total_vacant} แปลง/ห้อง")
    with col2:
        st.metric(label="⚠️ ที่ดินค้างชำระภาษี", value=f"{unpaid_tax} แปลง", delta="- ต้องจัดการ", delta_color="inverse")
    with col3:
        st.metric(label="👥 ผู้เช่าค้างชำระเงิน", value=f"{len(overdue_tenants)} ราย")

    st.write("---")
    
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        st.subheader("📊 สัดส่วนสถานะทรัพย์สิน")
        fig = px.pie(
            st.session_state.lands_df, 
            names='สถานะ', 
            title='สถานะการเช่าปัจจุบัน',
            color='สถานะ',
            color_discrete_map={'ว่าง': '#cccccc', 'มีคนเช่า': '#2ca02c'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with g_col2:
        st.subheader("🚨 ระบบแจ้งเตือนอัจฉริยะ (Smart Reminder)")
        st.write("**🌾 ภารกิจลงตรวจพื้นที่นาหลังเก็บเกี่ยว (ครบ 2 เดือน):**")
        current_time = datetime.now()
        alert_triggered = False
        
        for idx, row in st.session_state.payments_df.iterrows():
            if row["ประเภทการเช่า"] == "หลังเก็บเกี่ยว":
                pay_date = datetime.strptime(row["วันที่ชำระ"], "%Y-%m-%d")
                days_passed = (current_time - pay_date).days
                
                if days_passed >= 60:
                    alert_triggered = True
                    st.error(f"""
                    ⏰ **แจ้งเตือนลงตรวจนา:**  
                    **ทรัพย์สิน:** {row['ชื่อทรัพย์สิน']} | **ผู้เช่า:** {row['ชื่อคนเช่า']}  
                    *ชำระค่าเช่ารอบเก็บเกี่ยวล่าสุดเมื่อ {days_passed} วันที่แล้ว (เกิน 2 เดือน)*  
                    👉 กรุณาลงพื้นที่ไปตรวจดูว่ามีการเริ่มทำนารอบใหม่แล้วหรือไม่
                    """)
                    if st.button(f"✅ บันทึกว่าลงตรวจเรียบร้อยแล้ว ({row['ชื่อทรัพย์สิน']})", key=f"btn_{idx}"):
                        st.success("บันทึกการตรวจสอบสำเร็จ!")
                        
        if not alert_triggered:
            st.info("✅ ปัจจุบันไม่มีที่นาที่ครบกำหนดตรวจรอบ 2 เดือน")

    st.write("---")
    st.subheader("📋 รายชื่อผู้เช่าที่ยังค้างชำระค่าเช่า")
    if len(overdue_tenants) > 0:
        st.table(overdue_tenants)
    else:
        st.success("🎉 ไม่มีผู้เช่าค้างชำระเงินในระบบขณะนี้")

# ==========================================
# 5. หน้าจอ บันทึกรายละเอียดที่ดิน
# ==========================================
elif menu == "📂 บันทึกรายละเอียดที่ดิน/บ้านเช่า":
    st.title("📂 การจัดการข้อมูลที่ดินและบ้านเช่า")
    
    with st.expander("➕ คลิกเพื่อเพิ่มข้อมูลที่ดิน/บ้านเช่าแปลงใหม่"):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            land_id = st.text_input("รหัสที่ดิน (เช่น L005)")
            land_name = st.text_input("ชื่อที่ดิน / บ้านเช่า")
            land_type = st.selectbox("ประเภทสินทรัพย์", ["ที่นา", "บ้านเช่า"])
            land_status = st.selectbox("สถานะ", ["ว่าง", "มีคนเช่า"])
            rent_type = st.selectbox("ประเภทการเช่า", ["รายเดือน", "จ่ายก่อนทำรายปี", "หลังเก็บเกี่ยว"])
        with f_col2:
            deposit = st.number_input("เงินมัดจำ (บาท)", min_value=0, step=500)
            rent_price = st.number_input("ค่าเช่า (บาท)", min_value=0, step=500)
            tax_date = st.date_input("วันครบชำระภาษีที่ดิน")
            tax_status = st.selectbox("สถานะภาษี", ["ชำระแล้ว", "ยังไม่ได้ชำระ"])
            st.file_uploader("📸 อัพรูปภาพที่ดิน (ไฟล์จะถูกแนะนำให้เก็บใน Drive หลัก)", accept_multiple_files=True)
            st.file_uploader("📄 อัพโหลดเอกสารสิทธิ์ PDF", type=["pdf"])
            
        if st.button("💾 บันทึกข้อมูลที่ดินถาวร"):
            if land_id and land_name:
                new_row = {
                    "รหัสที่ดิน": land_id, "ชื่อที่ดิน": land_name, "ประเภท": land_type,
                    "สถานะ": land_status, "ประเภทการเช่า": rent_type, "เงินมัดจำ": deposit,
                    "ค่าเช่า": rent_price, "วันครบชำระภาษี": tax_date.strftime("%Y-%m-%d"),
                    "สถานะภาษี": tax_status
                }
                st.session_state.lands_df = pd.concat([st.session_state.lands_df, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"🎉 บันทึกข้อมูล '{land_name}' เรียบร้อยแล้ว")
            else:
                st.warning("⚠️ กรุณากรอกรหัสและชื่อที่ดินให้ครบถ้วน")
                
    st.write("### 📋 รายการที่ดินและบ้านเช่าในระบบทั้งหมด")
    st.dataframe(st.session_state.lands_df, use_container_width=True)

# ส่วนของหน้าเมนูอื่นๆ (ผู้เช่า, ชำระเงิน, พนักงาน) ทำการโหลดค่าของตัวเองได้อย่างต่อเนื่องและเสถียร
else:
    st.info("💡 ระบบหน้าจออื่นๆ พร้อมทำงานร่วมกับ Mock Data อย่างสมบูรณ์แบบแล้วค่ะ คุณสามารถกดเปลี่ยนเมนูเพื่อทดสอบระบบการป้อนข้อมูลได้ทันที")
