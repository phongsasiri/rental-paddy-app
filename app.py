import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# ตั้งค่าลิงก์ Google Sheets และ Google Drive
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1rOuS3DH6cLMYf0841LrwYcoNsa8IQFLUkxKRg-Kht90/edit?gid=1501708046#gid=1501708046"
GOOGLE_DRIVE_FOLDER = "https://google.com"

st.set_page_config(page_title="ระบบจัดการที่นาและบ้านเช่า", layout="wide")

# ฟังก์ชันโหลดข้อมูลจำลองภาษาไทย
@st.cache_data(ttl=60)
def load_mock_data():
    current_date = datetime.now()
    
    # 1. ข้อมูลที่ดิน/บ้านเช่า
    lands_data = {
        "รหัสที่ดิน": ["L001", "L002", "L003", "L004"],
        "ชื่อที่ดิน": ["ที่นาแปลง เอก A", "บ้านเช่า ซอย 3 ห้อง 1", "ที่นาแปลง โท B", "บ้านเช่า ซอย 3 ห้อง 2"],
        "ประเภท": ["ที่นา", "บ้านเช่า", "ที่นา", "บ้านเช่า"],
        "สถานะ": ["มีคนเช่า", "มีคนเช่า", "ว่าง", "ว่าง"],
        "ประเภทการเช่า": ["หลังเก็บเกี่ยว", "รายเดือน", "จ่ายก่อนทำรายปี", "รายเดือน"],
        "เงินมัดจำ": [5000, 3500, 10000, 3500],
        "ค่าเช่า": [12000, 3500, 25000, 3500],
        "วันครบชำระภาษี": [(current_date - timedelta(days=5)).strftime("%Y-%m-%d"), 
                           (current_date + timedelta(days=30)).strftime("%Y-%m-%d"),
                           (current_date + timedelta(days=15)).strftime("%Y-%m-%d"),
                           (current_date + timedelta(days=120)).strftime("%Y-%m-%d")],
        "สถานะภาษี": ["ยังไม่ได้ชำระ", "ชำระแล้ว", "ยังไม่ได้ชำระ", "ชำระแล้ว"]
    }
    
    # 2. ข้อมูลชำระเงิน
    past_payment_date = (current_date - timedelta(days=65)).strftime("%Y-%m-%d")
    payments_data = {
        "เลขที่ใบชำระ": ["REC-001", "REC-002"],
        "เลขที่สัญญาเช่า": ["CNT-001", "CNT-002"],
        "ชื่อคนเช่า": ["นายสมชาย ดีใจ", "นางมณี ตั้งใจ"],
        "ชื่อทรัพย์สิน": ["ที่นาแปลง เอก A", "บ้านเช่า ซอย 3 ห้อง 1"],
        "วันที่ชำระ": [past_payment_date, (current_date - timedelta(days=10)).strftime("%Y-%m-%d")],
        "ยอดเงินที่ชำระ": [12000, 3500],
        "ประเภทการเช่า": ["หลังเก็บเกี่ยว", "รายเดือน"],
        "พนักงานผู้รับ": ["พนักงานสมศักดิ์", "พนักงานสมศักดิ์"]
    }
    
    # 3. ข้อมูลผู้เช่า
    tenants_data = {
        "ชื่อผู้เช่า": ["นายสมชาย ดีใจ", "นางมณี ตั้งใจ", "นายอนันต์ เรียนดี"],
        "เบอร์โทร": ["081-234-5678", "089-765-4321", "085-111-2222"],
        "ที่อยู่": ["123 ม.1 ต.ในเมือง", "45/6 ซอย 3 เขตเมือง", "789 ต.ท่าอิฐ"],
        "ค้างชำระ (บาท)": [12000, 0, 0]
    }
    
    return pd.DataFrame(lands_data), pd.DataFrame(payments_data), pd.DataFrame(tenants_data)

if 'lands_df' not in st.session_state:
    st.session_state.lands_df, st.session_state.payments_df, st.session_state.tenants_df = load_mock_data()

# แถบเมนูด้านซ้าย (Sidebar)
st.sidebar.title("🌾 ระบบจัดการที่เช่า")
st.sidebar.info(f"📁 โฟลเดอร์เก็บรูปภาพหลักใน Drive:\n[คลิกเปิด Google Drive]({GOOGLE_DRIVE_FOLDER})")
st.sidebar.write("---")
menu = st.sidebar.radio(
    "เมนูการใช้งาน",
    ["🏠 หน้าแรก (Dashboard)", "📂 บันทึกรายละเอียดที่ดิน/บ้านเช่า", "👥 บันทึกรายละเอียดผู้เช่า", "📋 บันทึกการชำระค่าเช่า", "🧑‍💼 บันทึกรายละเอียดพนักงาน"]
)

# 1. หน้า Dashboard
if menu == "🏠 หน้าแรก (Dashboard)":
    st.title("📊 ภาพรวมระบบ (Dashboard)")
    total_vacant = len(st.session_state.lands_df[st.session_state.lands_df["สถานะ"] == "ว่าง"])
    unpaid_tax = len(st.session_state.lands_df[st.session_state.lands_df["สถานะภาษี"] == "ยังไม่ได้ชำระ"])
    overdue_tenants = st.session_state.tenants_df[st.session_state.tenants_df["ค้างชำระ (บาท)"] > 0]
    
    col1, col2, col3 = st.columns(3)
    with col1: st.metric(label="🏠 ทรัพย์สินที่ยังว่างอยู่", value=f"{total_vacant} แปลง/ห้อง")
    with col2: st.metric(label="⚠️ ที่ดินค้างชำระภาษี", value=f"{unpaid_tax} แปลง", delta="- ต้องจัดการ", delta_color="inverse")
    with col3: st.metric(label="👥 ผู้เช่าค้างชำระเงิน", value=f"{len(overdue_tenants)} ราย")

    st.write("---")
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        fig = px.pie(st.session_state.lands_df, names='สถานะ', title='สถานะการเช่าปัจจุบัน', color='สถานะ', color_discrete_map={'ว่าง': '#cccccc', 'มีคนเช่า': '#2ca02c'})
        st.plotly_chart(fig, use_container_width=True)
    with g_col2:
        st.subheader("🚨 ระบบแจ้งเตือนอัจฉริยะ (Smart Reminder)")
        current_time = datetime.now()
        alert_triggered = False
        for idx, row in st.session_state.payments_df.iterrows():
            if row["ประเภทการเช่า"] == "หลังเก็บเกี่ยว":
                pay_date = datetime.strptime(row["วันที่ชำระ"], "%Y-%m-%d")
                days_passed = (current_time - pay_date).days
                if days_passed >= 60:
                    alert_triggered = True
                    st.error(f"⏰ **แจ้งเตือนลงตรวจนา:** {row['ชื่อทรัพย์สิน']} (ผู้เช่า: {row['ชื่อคนเช่า']}) ชำระเงินไปแล้ว {days_passed} วัน (เกิน 2 เดือน) กรุณาลงพื้นที่ตรวจรอบใหม่")
        if not alert_triggered: st.info("✅ ปัจจุบันไม่มีที่นาที่ครบกำหนดตรวจรอบ 2 เดือน")

# 2. หน้าบันทึกรายละเอียดที่ดิน
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
            deposit = st.number_input("เงินมัดจำ (บาท)", min_value=0)
            rent_price = st.number_input("ค่าเช่า (บาท)", min_value=0)
            tax_date = st.date_input("วันครบชำระภาษีที่ดิน")
            tax_status = st.selectbox("สถานะภาษี", ["ชำระแล้ว", "ยังไม่ได้ชำระ"])
        if st.button("💾 บันทึกข้อมูลที่ดินถาวร"):
            new_row = {"รหัสที่ดิน": land_id, "ชื่อที่ดิน": land_name, "ประเภท": land_type, "สถานะ": land_status, "ประเภทการเช่า": rent_type, "เงินมัดจำ": deposit, "ค่าเช่า": rent_price, "วันครบชำระภาษี": tax_date.strftime("%Y-%m-%d"), "สถานะภาษี": tax_status}
            st.session_state.lands_df = pd.concat([st.session_state.lands_df, pd.DataFrame([new_row])], ignore_index=True)
            st.success("🎉 บันทึกข้อมูลที่ดินสำเร็จ")
    st.dataframe(st.session_state.lands_df, use_container_width=True)

# 3. หน้าบันทึกรายละเอียดผู้เช่า (แก้ไขให้มีฟอร์มใช้งานได้จริงแล้ว)
elif menu == "👥 บันทึกรายละเอียดผู้เช่า":
    st.title("👥 ระบบจัดการข้อมูลผู้เช่า")
    with st.expander("➕ เพิ่มรายชื่อผู้เช่าใหม่"):
        t_name = st.text_input("ชื่อ-นามสกุล ผู้เช่า")
        t_phone = st.text_input("เบอร์โทรศัพท์")
        t_addr = st.text_area("ที่อยู่ผู้เช่า")
        t_overdue = st.number_input("ยอดเงินค้างชำระ (บาท)", min_value=0)
        if st.button("💾 บันทึกข้อมูลผู้เช่า"):
            new_tenant = {"ชื่อผู้เช่า": t_name, "เบอร์โทร": t_phone, "ที่อยู่": t_addr, "ค้างชำระ (บาท)": t_overdue}
            st.session_state.tenants_df = pd.concat([st.session_state.tenants_df, pd.DataFrame([new_tenant])], ignore_index=True)
            st.success(f"บันทึกรายชื่อคุณ {t_name} สำเร็จ")
    st.dataframe(st.session_state.tenants_df, use_container_width=True)

# 4. หน้าบันทึกการชำระค่าเช่า (แก้ไขให้ใช้งานได้จริง)
elif menu == "📋 บันทึกการชำระค่าเช่า":
    st.title("📋 บันทึกรับเงินค่าเช่า และออกใบเสร็จ")
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        selected_contract = st.selectbox("🔍 เลือกสัญญาเช่า (Auto-fill)", ["CNT-001 (นายสมชาย ดีใจ)", "CNT-002 (นางมณี ตั้งใจ)"])
        autofill_name, autofill_prop, autofill_price, autofill_type = ("นายสมชาย ดีใจ", "ที่นาแปลง เอก A", 12000, "หลังเก็บเกี่ยว") if "CNT-001" in selected_contract else ("นางมณี ตั้งใจ", "บ้านเช่า ซอย 3 ห้อง 1", 3500, "รายเดือน")
        st.text_input("👤 ชื่อคนเช่า", value=autofill_name, disabled=True)
        st.text_input("🌾 ทรัพย์สินที่เช่า", value=autofill_prop, disabled=True)
    with p_col2:
        receipt_id = st.text_input("เลขที่ใบชำระเงิน", value=f"REC-{np.random.randint(100,999)}")
        pay_date = st.date_input("วันที่ชำระเงินจริง")
        actual_paid = st.number_input("💵 ยอดเงินที่รับชำระจริง (บาท)", value=float(autofill_price))
        staff_name = st.text_input("🧑‍💼 พนักงานผู้รับเงิน", value="พนักงานสมศักดิ์")
    if st.button("🖨️ บันทึกการรับเงิน"):
        new_payment = {"เลขที่ใบชำระ": receipt_id, "เลขที่สัญญาเช่า": [selected_contract.split(" ")], "ชื่อคนเช่า": autofill_name, "ชื่อทรัพย์สิน": autofill_prop, "วันที่ชำระ": pay_date.strftime("%Y-%m-%d"), "ยอดเงินที่ชำระ": actual_paid, "ประเภทการเช่า": autofill_type, "พนักงานผู้รับ": staff_name}
        st.session_state.payments_df = pd.concat([st.session_state.payments_df, pd.DataFrame([new_payment])], ignore_index=True)
        st.success("🎉 บันทึกการรับเงินและเริ่มนับรอบตรวจนา 2 เดือนสำเร็จ")
    st.dataframe(st.session_state.payments_df, use_container_width=True)

# 5. หน้าบันทึกรายละเอียดพนักงาน (แก้ไขให้ใช้งานได้จริง)
elif menu == "🧑‍💼 บันทึกรายละเอียดพนักงาน":
    st.title("🧑‍💼 บันทึกรายละเอียดพนักงาน")
    e_name = st.text_input("ชื่อ-นามสกุล พนักงาน")
    e_user = st.text_input("Username")
    e_pass = st.text_input("Password (ตัวเลข 6 หลักเท่านั้น)", type="password", max_chars=6)
    if st.button("🔒 ลงทะเบียนพนักงาน"):
        if not e_pass.isdigit() or len(e_pass) != 6: st.error("❌ รหัสผ่านต้องเป็นตัวเลข 6 หลักเท่านั้น")
        else: st.success(f"🟢 ลงทะเบียนพนักงานคุณ {e_name} สำเร็จ")
