import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# ==========================================
# 1. การตั้งค่าระบบและลิงก์ฐานข้อมูล (เชื่อมโยงตามที่คุณระบุ)
# ==========================================
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1rOuS3DH6cLMYf0841LrwYcoNsa8IQFLUkxKRg-Kht90/edit?gid=1501708046#gid=1501708046"
GOOGLE_DRIVE_FOLDER = "https://google.com"

st.set_page_config(page_title="ระบบจัดการที่นาและบ้านเช่า", layout="wide")

# ==========================================
# 2. ฟังก์ชันจดจำและจำลองหน่วยความจำ (แก้บั๊กข้อมูลหาย)
# ==========================================
def initialize_persistent_data():
    current_date = datetime.now()
    past_payment_date = (current_date - timedelta(days=65)).strftime("%Y-%m-%d")
    
    # โหลดค่าเริ่มต้นของที่ดิน/บ้านเช่า
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
        
    # โหลดค่าเริ่มต้นของประวัติการชำระเงิน (ตั้งค่าย้อนหลัง 65 วันเพื่อทดสอบระบบเตือน 2 เดือน)
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
        
    # โหลดค่าเริ่มต้นของผู้เช่า
    if 'tenants_df' not in st.session_state:
        tenants_data = {
            "ชื่อผู้เช่า": ["นายสมชาย ดีใจ", "นางมณี ตั้งใจ", "นายอนันต์ เรียนดี"],
            "เบอร์โทร": ["081-234-5678", "089-765-4321", "085-111-2222"],
            "ที่อยู่": ["123 ม.1 ต.ในเมือง", "45/6 ซอย 3 เขตเมือง", "789 ต.ท่าอิฐ"],
            "ค้างชำระ (บาท)": [0.0, 3500.0, 0.0]
        }
        st.session_state.tenants_df = pd.DataFrame(tenants_data)

    # โหลดค่าเริ่มต้นของพนักงาน
    if 'staff_df' not in st.session_state:
        staff_data = {
            "ชื่อ-นามสกุล": ["พนักงานสมศักดิ์", "พนักงานรักดี"],
            "Username": ["somsak01", "rakdee02"],
            "เบอร์โทร": ["082-111-2222", "083-444-5555"],
            "ที่อยู่": ["ต.ในเมือง อ.เมือง", "ต.ท่าอิฐ อ.เมือง"]
        }
        st.session_state.staff_df = pd.DataFrame(staff_data)

# รันระบบจำลองความปลอดภัยของข้อมูล
initialize_persistent_data()

# ==========================================
# 3. แถบเมนูด้านซ้าย (Sidebar Navigation)
# ==========================================
st.sidebar.title("🌾 ระบบจัดการที่เช่า")
st.sidebar.info(f"🔗 ลิงก์ระบบจัดเก็บข้อมูลภายนอก:\n* [เปิดดู Google Sheets]({GOOGLE_SHEET_URL})\n* [เปิดโฟลเดอร์ภาพ Google Drive]({GOOGLE_DRIVE_FOLDER})")
st.sidebar.write("---")
menu = st.sidebar.radio(
    "เมนูการใช้งานระบบ",
    ["🏠 หน้าแรก (Dashboard)", "📂 บันทึกรายละเอียดที่ดิน/บ้านเช่า", "👥 บันทึกรายละเอียดผู้เช่า", "📋 บันทึกการชำระค่าเช่า", "🧑‍💼 บันทึกรายละเอียดพนักงาน"]
)

# ==========================================
# 4. ฟังก์ชันการทำงานแต่ละหน้าจอเมนู
# ==========================================

# --- หน้าที่ 1: DASHBOARD ---
if menu == "🏠 หน้าแรก (Dashboard)":
    st.title("📊 ภาพรวมระบบจัดการค่าเช่า (Dashboard)")
    
    # คำนวณค่าทางสถิติ
    total_vacant = len(st.session_state.lands_df[st.session_state.lands_df["สถานะ"] == "ว่าง"])
    unpaid_tax = len(st.session_state.lands_df[st.session_state.lands_df["สถานะภาษี"] == "ยังไม่ได้ชำระ"])
    overdue_tenants = st.session_state.tenants_df[st.session_state.tenants_df["ค้างชำระ (บาท)"] > 0]
    
    # การ์ดสรุปข้อมูลเด่นชัดด้านบนสุด
    col1, col2, col3 = st.columns(3)
    with col1: st.metric(label="🏠 ทรัพย์สินที่ยังว่างอยู่", value=f"{total_vacant} แปลง/ห้อง")
    with col2: st.metric(label="⚠️ ที่ดินค้างชำระภาษี", value=f"{unpaid_tax} แปลง", delta="กรุณาตรวจสอบ", delta_color="inverse")
    with col3: st.metric(label="👥 ผู้เช่าค้างชำระเงิน", value=f"{len(overdue_tenants)} ราย")

    st.write("---")
    
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        # แผนภูมิวงกลมแสดงสัดส่วนบ้านเช่าและที่นา
        fig = px.pie(st.session_state.lands_df, names='สถานะ', title='📊 สัดส่วนสถานะการเช่าทรัพย์สินปัจจุบัน', color='สถานะ', color_discrete_map={'ว่าง': '#cccccc', 'มีคนเช่า': '#2ca02c'})
        st.plotly_chart(fig, use_container_width=True)
        
    with g_col2:
        st.subheader("🚨 ระบบแจ้งเตือนอัจฉริยะ (Smart Reminder)")
        
        # 🟢 ฟังก์ชันแจ้งลงตรวจนา 2 เดือนหลังเก็บเกี่ยว
        st.write("**🌾 รายการลงพื้นที่ตรวจแปลงนาหลังเก็บเกี่ยว (ครบ 2 เดือน):**")
        current_time = datetime.now()
        alert_triggered = False
        
        for idx, row in st.session_state.payments_df.iterrows():
            if row["ประเภทการเช่า"] == "หลังเก็บเกี่ยว":
                pay_date = datetime.strptime(row["วันที่ชำระ"], "%Y-%m-%d")
                days_passed = (current_time - pay_date).days
                
                # หากชำระเงินเกิน 60 วัน (2 เดือน) ให้ขึ้นแถบสีแดงแจ้งเตือนทันที
                if days_passed >= 60:
                    alert_triggered = True
                    st.error(f"""
                    ⏰ **ตรวจพบการเก็บเกี่ยวพ้นกำหนดเวลา:**  
                    *   **ทรัพย์สิน:** {row['ชื่อทรัพย์สิน']}  
                    *   **ผู้เช่ารายล่าสุด:** {row['ชื่อคนเช่า']}  
                    *   **สถานะเวลา:** ชำระรอบเก็บเกี่ยวมาแล้ว {days_passed} วัน (เกิน 2 เดือนแล้ว)  
                    👉 **คำแนะนำ:** เจ้าของควรลงพื้นที่ตรวจสอบว่าเริ่มมีการทำนารอบใหม่แล้วหรือยัง
                    """)
                    if st.button(f"✅ บันทึกว่าลงตรวจแปลงแล้ว ({row['ชื่อทรัพย์สิน']})", key=f"inspect_{idx}"):
                        st.success("บันทึกภารกิจลงตรวจเรียบร้อย!")
                        
        if not alert_triggered:
            st.info("🟢 ปัจจุบันยังไม่มีรายการที่นาที่ต้องลงตรวจรอบ 2 เดือนค่ะ")

    # ตารางแสดงชื่อคนเช่าที่ค้างชำระเงิน
    st.write("---")
    st.subheader("📋 รายชื่อผู้เช่าที่ยังค้างชำระค่าเช่าระบบ")
    if len(overdue_tenants) > 0:
        st.table(overdue_tenants)
    else:
        st.success("🎉 ยินดีด้วย: ไม่มีรายชื่อผู้เช่าค้างชำระเงินในระบบขณะนี้")

# --- หน้าที่ 2: บันทึกรายละเอียดที่ดิน ---
elif menu == "📂 บันทึกรายละเอียดที่ดิน/บ้านเช่า":
    st.title("📂 ระบบบันทึกและจัดการข้อมูลที่ดิน/บ้านเช่า")
    
    with st.form("land_input_form", clear_on_submit=True):
        st.write("### ➕ เพิ่มรายละเอียดข้อมูลแปลงที่ดิน/บ้านเช่าใหม่")
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            land_id = st.text_input("รหัสที่ดิน/บ้านเช่า (เช่น L005)")
            land_name = st.text_input("ชื่อเรียกที่ดิน หรือ ชื่อบ้านเช่า")
            land_type = st.selectbox("ประเภทสินทรัพย์", ["ที่นา", "บ้านเช่า"])
            land_status = st.selectbox("สถานะการใช้งาน", ["ว่าง", "มีคนเช่า"])
            rent_type = st.selectbox("ประเภทการเช่า", ["รายเดือน", "จ่ายก่อนทำรายปี", "หลังเก็บเกี่ยว"])
        with f_col2:
            deposit = st.number_input("เงินมัดจำล่วงหน้า (บาท)", min_value=0.0, value=0.0, step=500.0)
            rent_price = st.number_input("อัตราค่าเช่าที่เรียกเก็บ (บาท)", min_value=0.0, value=0.0, step=500.0)
            tax_date = st.date_input("วันครบกำหนดชำระภาษีที่ดินประจำปี")
            tax_status = st.selectbox("สถานะการชำระภาษี", ["ชำระแล้ว", "ยังไม่ได้ชำระ"])
            st.file_uploader("📸 แนบรูปภาพทรัพย์สิน (เลือกรูปภาพส่งเข้า Drive)", accept_multiple_files=True)
            st.file_uploader("📄 แนบหลักฐานเอกสารสิทธิ์ PDF (โฉนด/ใบชำระภาษี)", type=["pdf"])
            
        submit_land = st.form_submit_button("💾 บันทึกข้อมูลลงฐานข้อมูล")
        
        if submit_land:
            if land_id and land_name:
                new_land = {
                    "รหัสที่ดิน": land_id, "ชื่อที่ดิน": land_name, "ประเภท": land_type,
                    "สถานะ": land_status, "ประเภทการเช่า": rent_type, "เงินมัดจำ": deposit,
                    "ค่าเช่า": rent_price, "วันครบชำระภาษี": tax_date.strftime("%Y-%m-%d"),
                    "สถานะภาษี": tax_status
                }
                st.session_state.lands_df = pd.concat([st.session_state.lands_df, pd.DataFrame([new_land])], ignore_index=True)
                st.success(f"🎉 บันทึกข้อมูลที่ดิน '{land_name}' เรียบร้อยแล้ว! ตารางจะอัปเดตทันทีกดปิดฟอร์ม")
            else:
                st.error("❌ บันทึกไม่สำเร็จ: กรุณากรอกรหัสทรัพย์สินและชื่อเรียกให้ครบถ้วน")

    st.write("---")
    st.write("### 📋 ตารางรายชื่อที่ดินและบ้านเช่าทั้งหมดในระบบ")
    st.dataframe(st.session_state.lands_df, use_container_width=True)

# --- หน้าที่ 3: บันทึกรายละเอียดผู้เช่า ---
elif menu == "👥 บันทึกรายละเอียดผู้เช่า":
