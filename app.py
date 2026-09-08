import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# ==========================================
# 1. การตั้งค่าระบบและลิงก์ฐานข้อมูลภายนอก
# ==========================================
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1rOuS3DH6cLMYf0841LrwYcoNsa8IQFLUkxKRg-Kht90/edit?gid=1501708046#gid=1501708046"
GOOGLE_DRIVE_FOLDER = "https://google.com"

st.set_page_config(page_title="ระบบจัดการที่นาและบ้านเช่า", layout="wide")

# ==========================================
# 2. ฟังก์ชันจดจำและจำลองหน่วยความจำ (Session State)
# ==========================================
def initialize_persistent_data():
    current_date = datetime.now()
    past_payment_date = (current_date - timedelta(days=65)).strftime("%Y-%m-%d")
    
    # 1. ข้อมูลที่ดิน / บ้านเช่า
    if 'lands_df' not in st.session_state:
        lands_data = {
            "รหัสที่ดิน": ["L001", "L002", "L003", "L004"],
            "ชื่อที่ดิน": ["ที่นาแปลง เอก A", "บ้านเช่า ซอย 3 ห้อง 1", "ที่นาแปลง โท B", "บ้านเช่า ซอย 3 ห้อง 2"],
            "ประเภท": ["ที่นา", "บ้านเช่า", "ที่นา", "บ้านเช่า"],
            "สถานะ": ["มีคนเช่า", "มีคนเช่า", "ว่าง", "ว่าง"],
            "ประเภทการเช่า": ["หลังเก็บเกี่ยว", "รายเดือน", "จ่ายก่อนทำรายปี", "รายเดือน"],
            "เงินมัดจำ": [5000.0, 3500.0, 10000.0, 3500.0],
            "ค่าเช่า": [12000.0, 3500.0, 25000.0, 3500.0],
            "วันครบชำระภาษี": [(current_date - timedelta(days=5)).strftime("%Y-%m-%d"), 
                               (current_date + timedelta(days=30)).strftime("%Y-%m-%d"),
                               (current_date + timedelta(days=15)).strftime("%Y-%m-%d"),
                               (current_date + timedelta(days=120)).strftime("%Y-%m-%d")],
            "สถานะภาษี": ["ยังไม่ได้ชำระ", "ชำระแล้ว", "ยังไม่ได้ชำระ", "ชำระแล้ว"]
        }
        st.session_state.lands_df = pd.DataFrame(lands_data)
        
    # 2. ข้อมูลประวัติการชำระเงิน
    if 'payments_df' not in st.session_state:
        payments_data = {
            "เลขที่ใบชำระ": ["REC-001", "REC-002"],
            "เลขที่สัญญาเช่า": ["CNT-001", "CNT-002"],
            "ชื่อคนเช่า": ["นายสมชาย ดีใจ", "นางมณี ตั้งใจ"],
            "ชื่อทรัพย์สิน": ["ที่นาแปลง เอก A", "บ้านเช่า ซอย 3 ห้อง 1"],
            "วันที่ชำระ": [past_payment_date, (current_date - timedelta(days=10)).strftime("%Y-%m-%d")],
            "ยอดเงินที่ชำระ": [12000.0, 3500.0],
            "ประเภทการเช่า": ["หลังเก็บเกี่ยว", "รายเดือน"],
            "พนักงานผู้รับ": ["พนักงานสมศักดิ์", "พนักงานสมศักดิ์"]
        }
        st.session_state.payments_df = pd.DataFrame(payments_data)
        
    # 3. ข้อมูลรายชื่อผู้เช่า
    if 'tenants_df' not in st.session_state:
        tenants_data = {
            "ชื่อผู้เช่า": ["นายสมชาย ดีใจ", "นางมณี ตั้งใจ", "นายอนันต์ เรียนดี"],
            "เบอร์โทร": ["081-234-5678", "089-765-4321", "085-111-2222"],
            "ที่อยู่": ["123 ม.1 ต.ในเมือง", "45/6 ซอย 3 เขตเมือง", "789 ต.ท่าอิฐ"],
            "ค้างชำระ (บาท)": [0.0, 3500.0, 0.0]
        }
        st.session_state.tenants_df = pd.DataFrame(tenants_data)

    # 4. ข้อมูลพนักงาน
    if 'staff_df' not in st.session_state:
        staff_data = {
            "ชื่อ-นามสกุล": ["พนักงานสมศักดิ์", "พนักงานรักดี"],
            "Username": ["somsak01", "rakdee02"],
            "เบอร์โทร": ["082-111-2222", "083-444-5555"],
            "ที่อยู่": ["ต.ในเมือง อ.เมือง", "ต.ท่าอิฐ อ.เมือง"]
        }
        st.session_state.staff_df = pd.DataFrame(staff_data)

# เริ่มรันการจดจำข้อมูลจำลอง
initialize_persistent_data()

# ==========================================
# 3. แถบเมนูด้านซ้าย (Sidebar Navigation)
# ==========================================
st.sidebar.title("🌾 ระบบจัดการที่เช่า")
st.sidebar.info(f"🔗 ลิงก์เชื่อมโยงฐานข้อมูลหลัก:\n* [เปิดดู Google Sheets]({GOOGLE_SHEET_URL})\n* [เปิดคลังภาพ Google Drive]({GOOGLE_DRIVE_FOLDER})")
st.sidebar.write("---")
menu = st.sidebar.radio(
    "เลือกหน้าเมนูการใช้งาน",
    ["🏠 หน้าแรก (Dashboard)", "📂 บันทึกรายละเอียดที่ดิน/บ้านเช่า", "👥 บันทึกรายละเอียดผู้เช่า", "📋 บันทึกการชำระค่าเช่า", "🧑‍💼 บันทึกรายละเอียดพนักงาน"]
)

# ==========================================
# 4. การแสดงผลฟอร์มและตารางฝั่งขวา
# ==========================================

# --- 1. หน้า Dashboard ---
if menu == "🏠 หน้าแรก (Dashboard)":
    st.title("📊 ภาพรวมระบบจัดการค่าเช่า (Dashboard)")
    
    total_vacant = len(st.session_state.lands_df[st.session_state.lands_df["สถานะ"] == "ว่าง"])
    unpaid_tax = len(st.session_state.lands_df[st.session_state.lands_df["สถานะภาษี"] == "ยังไม่ได้ชำระ"])
    overdue_tenants = st.session_state.tenants_df[st.session_state.tenants_df["ค้างชำระ (บาท)"] > 0]
    
    col1, col2, col3 = st.columns(3)
    with col1: st.metric(label="🏠 ทรัพย์สินที่ยังว่างอยู่", value=f"{total_vacant} แปลง/ห้อง")
    with col2: st.metric(label="⚠️ ที่ดินค้างชำระภาษี", value=f"{unpaid_tax} แปลง")
    with col3: st.metric(label="👥 ผู้เช่าค้างชำระเงิน", value=f"{len(overdue_tenants)} ราย")

    st.write("---")
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        fig = px.pie(st.session_state.lands_df, names='สถานะ', title='📊 แผนภูมิสถานะการเช่าปัจจุบัน', color='สถานะ', color_discrete_map={'ว่าง': '#cccccc', 'มีคนเช่า': '#2ca02c'})
        st.plotly_chart(fig, use_container_width=True)
        
    with g_col2:
        st.subheader("🚨 ระบบแจ้งเตือนอัจฉริยะ (Smart Reminder)")
        st.write("**🌾 รายการลงตรวจแปลงนาหลังเก็บเกี่ยว (ครบกำหนด 2 เดือน):**")
        current_time = datetime.now()
        alert_triggered = False
        
        for idx, row in st.session_state.payments_df.iterrows():
            if row["ประเภทการเช่า"] == "หลังเก็บเกี่ยว":
                pay_date = datetime.strptime(row["วันที่ชำระ"], "%Y-%m-%d")
                days_passed = (current_time - pay_date).days
                
                if days_passed >= 60:
                    alert_triggered = True
                    st.error(f"""
                    ⏰ **แจ้งเตือนความคืบหน้าแปลงนา:**  
                    *   **ชื่อทรัพย์สิน:** {row['ชื่อทรัพย์สิน']} | **ผู้เช่า:** {row['ชื่อคนเช่า']}  
                    *   **สถานะเวลา:** ชำระรอบล่าสุดมาแล้ว {days_passed} วัน (เกิน 2 เดือน)  
                    👉 **สิ่งที่ต้องทำ:** เจ้าของควรลงพื้นที่ไปตรวจดูว่าเริ่มทำนารอบใหม่แล้วหรือยัง
                    """)
                    if st.button(f"✅ บันทึกว่าลงตรวจแล้ว ({row['ชื่อทรัพย์สิน']})", key=f"check_{idx}"):
                        st.success("บันทึกการตรวจสอบเรียบร้อยแล้ว!")
                        
        if not alert_triggered:
            st.info("🟢 ปัจจุบันไม่มีรายการที่นาค้างตรวจรอบ 2 เดือนค่ะ")

    st.write("---")
    st.subheader("📋 รายชื่อผู้เช่าที่ค้างชำระเงิน ณ ปัจจุบัน")
    if len(overdue_tenants) > 0:
        st.table(overdue_tenants[["ชื่อผู้เช่า", "เบอร์โทร", "ค้างชำระ (บาท)"]])
    else:
        st.success("🎉 ไม่มีรายชื่อผู้เช่าค้างชำระเงินในระบบขณะนี้")

# --- 2. หน้าบันทึกรายละเอียดที่ดิน ---
elif menu == "📂 บันทึกรายละเอียดที่ดิน/บ้านเช่า":
    st.title("📂 บันทึกและจัดการข้อมูลที่ดิน/บ้านเช่า")
    
    with st.form("land_form", clear_on_submit=True):
        st.write("### ➕ เพิ่มรายละเอียดข้อมูลแปลงที่ดิน/บ้านเช่าใหม่")
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            land_id = st.text_input("รหัสทรัพย์สิน (เช่น L005)")
            land_name = st.text_input("ชื่อเรียกที่ดิน หรือ ชื่อบ้านเช่า")
            land_type = st.selectbox("ประเภทสินทรัพย์เช่า", ["ที่นา", "บ้านเช่า"])
            land_status = st.selectbox("สถานะการใช้งานปัจจุบัน", ["ว่าง", "มีคนเช่า"])
            rent_type = st.selectbox("ข้อตกลงประเภทการเช่า", ["รายเดือน", "จ่ายก่อนทำรายปี", "หลังเก็บเกี่ยว"])
        with f_col2:
            deposit = st.number_input("เงินมัดจำล่วงหน้า (บาท)", min_value=0.0, value=0.0, step=500.0)
            rent_price = st.number_input("เงินค่าเช่า/รอบชำระ (บาท)", min_value=0.0, value=0.0, step=500.0)
            tax_date = st.date_input("วันครบกำหนดชำระภาษีที่ดินประจำปี")
            tax_status = st.selectbox("สถานะการชำระภาษีที่ดิน", ["ชำระแล้ว", "ยังไม่ได้ชำระ"])
            st.file_uploader("📸 อัปโหลดรูปภาพที่ดิน (บันทึกภาพลง Drive)", accept_multiple_files=True)
            st.file_uploader("📄 เอกสารสิทธิ์ PDF (สำเนาโฉนด/เอกสารภาษี)", type=["pdf"])
            
        submit_land = st.form_submit_button("💾 บันทึกข้อมูลทรัพย์สินถาวร")
        
        if submit_land:
            if land_id and land_name:
                new_land = {
                    "รหัสที่ดิน": land_id, "ชื่อที่ดิน": land_name, "ประเภท": land_type,
                    "สถานะ": land_status, "ประเภทการเช่า": rent_type, "เงินมัดจำ": deposit,
                    "ค่าเช่า": rent_price, "วันครบชำระภาษี": tax_date.strftime("%Y-%m-%d"),
                    "สถานะภาษี": tax_status
                }
                st.session_state.lands_df = pd.concat([st.session_state.lands_df, pd.DataFrame([new_land])], ignore_index=True)
                st.success(f"🎉 บันทึกข้อมูลที่ดิน '{land_name}' เรียบร้อยแล้ว!")
            else:
                st.error("❌ กรุณากรอกรหัสทรัพย์สินและชื่อเรียกให้ครบถ้วน")

    st.write("---")
    st.write("### 📋 บัญชีรายการที่ดินและบ้านเช่าทั้งหมดในระบบ")
    st.dataframe(st.session_state.lands_df, use_container_width=True)

# --- 3. หน้าบันทึกรายละเอียดผู้เช่า ---
elif menu == "👥 บันทึกรายละเอียดผู้เช่า":
    st.title("👥 ระบบลงทะเบียนและจัดการข้อมูลผู้เช่า")
    
    with st.form("tenant_form", clear_on_submit=True):
        st.write("### ➕ เพิ่มประวัติและลงทะเบียนผู้เช่ารายใหม่")
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            t_name = st.text_input("ชื่อ - นามสกุล ผู้เช่า")
            t_phone = st.text_input("เบอร์โทรศัพท์ติดต่อมือถือ")
        with t_col2:
            t_overdue = st.number_input("ยอดเงินค้างชำระค้างเก่า (บาท)", min_value=0.0, value=0.0, step=100.0)
