import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px

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
# FUNCTION TO LOAD DATA FROM PUBLIC GOOGLE SHEETS
# --------------------------------------------------------------------------------
@st.cache_data(ttl=60)
def load_sheet_data(sheet_url, worksheet_name):
    try:
        # แปลงลิงก์ Edit ปกติให้กลายเป็นลิงก์ดาวน์โหลด CSV สำหรับอ่านข้อมูล
        base_url = sheet_url.split('/edit')[0]
        csv_url = f"{base_url}/gviz/tq?tqx=out:csv&sheet={worksheet_name}"
        df = pd.read_csv(csv_url)
        return df
    except Exception as e:
        st.error(f"ไม่สามารถโหลดแผ่นงาน {worksheet_name} ได้: {e}")
        return pd.DataFrame()

# ดึง URL สเปรดชีตจาก Secrets ของ Streamlit
try:
    SHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]
except Exception:
    st.error("🚨 ไม่พบลิงก์ Google Sheets ในหน้า Settings -> Secrets กรุณาตั้งค่าความลับก่อนใช้งาน")
    st.stop()

# โหลดข้อมูลจริงเข้าแอปพลิเคชัน
df_properties = load_sheet_data(SHEET_URL, "Properties")
df_employees = load_sheet_data(SHEET_URL, "Employees")
df_tenants = load_sheet_data(SHEET_URL, "Tenants")
df_leases = load_sheet_data(SHEET_URL, "Leases")
df_payments = load_sheet_data(SHEET_URL, "Payments")

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

# ปุ่มรีเฟรชล้างแคชดึงข้อมูลสดใหม่
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
            st.markdown(f"<div style='text-align:center; font-weight:bold;'>ทรัพย์สินว่างอยู่ {vacant_count} รายการ</div>", unsafe_allow_html=True)
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
        
        # ตรวจสอบนาหลังเก็บเกี่ยว 2 เดือน
        st.markdown("🚨 **ระบบตรวจจับการทำนารอบใหม่ (หลังชำระเงิน 2 เดือน)**")
        if not df_payments.empty and not df_properties.empty:
            harvest_props = df_properties[df_properties["ประเภทการเช่า"] == "หลังเก็บเกี่ยว"]["ชื่อที่ดิน"].tolist()
            harvest_payments = df_payments[df_payments["ชื่อบ้านเช่า_ที่นา"].isin(harvest_props)]
            
            alert_triggered = False
            for idx, row in harvest_payments.iterrows():
                if pd.notna(row["วันที่ชำระ"]):
                    pay_date = pd.to_datetime(row["วันที่ชำระ"]).date()
                    days_passed = (datetime.now().date() - pay_date).days
                    if days_passed >= 60:
                        alert_triggered = True
                        st.markdown(
                            f'<div class="inspection-alert">'
                            f'⏰ <b>แจ้งลงพื้นที่ตรวจนา:</b> {row["ชื่อบ้านเช่า_ที่นา"]} (ผู้เช่า: {row["ชื่อคนเช่า"]})<br>'
                            f'ชำระค่าเช่าไปแล้ว {days_passed} วัน (> 2 เดือน) กรุณาลงตรวจการเริ่มทำนารอบใหม่'
                            f'</div>', 
                            unsafe_allow_html=True
                        )
            if not alert_triggered:
                st.write("ไม่มีนัดหมายลงตรวจแปลงนาในระยะนี้")

    with col3:
        st.subheader("💡 รายชื่อผู้เช่าค้างชำระค่าเช่า")
        if not df_leases.empty and "วันครบกำหนดชำระค่าเช่า" in df_leases.columns:
            overdue_leases = df_leases[df_leases["วันครบกำหนดชำระค่าเช่า"] < datetime.now().date()]
            if not overdue_leases.empty:
                for idx, row in overdue_leases.iterrows():
                    st.error(f"❌ {row['ชื่อคนเช่า']} | ค้าง: {row['ที่นาหรือบ้านเช่า']} | ยอด: {row['เงินค่าเช่า']:,} บาท")
            else:
                st.success("🎉 ไม่มีผู้เช่าค้างชำระในระบบขณะนี้")
        else:
            st.write("ไม่มีข้อมูลการค้างชำระ")

    st.subheader("📋 รายการสัญญาเช่าและทรัพย์สินทั้งหมด")
    st.dataframe(df_properties, use_container_width=True)

# --------------------------------------------------------------------------------
# OTHER PAGES (VIEW ONLY MODE FOR STABILITY ON FREE SERVER)
# --------------------------------------------------------------------------------
elif menu == "🌾 ข้อมูลที่ดิน/บ้านเช่า":
    st.title("🌾 รายละเอียดที่ดินและบ้านเช่า")
    st.dataframe(df_properties, use_container_width=True)
    st.info("💡 เวอร์ชันนี้เปิดระบบดึงข้อมูลแบบเสถียรเพื่อรองรับเซิร์ฟเวอร์หลักแล้ว หากต้องการแก้ไขข้อมูล สามารถเข้าไปแก้ไขโดยตรงบน Google Sheets ได้ทันที!")

elif menu == "👥 ข้อมูลผู้เช่า":
    st.title("👥 ระบบข้อมูลผู้เช่า")
    st.dataframe(df_tenants, use_container_width=True)

elif menu == "📋 สัญญาเช่า":
    st.title("📋 ระบบตรวจสอบข้อมูลสัญญาเช่า")
    st.dataframe(df_leases, use_container_width=True)

elif menu == "💰 ประวัติการชำระเงิน":
    st.title("💰 ประวัติบันทึกการรับชำระเงินค่างวด")
    st.dataframe(df_payments, use_container_width=True)

elif menu == "🧑‍💼 ข้อมูลพนักงาน":
    st.title("🧑‍💼 ข้อมูลพนักงานและสิทธิ์ผู้ใช้งาน")
    st.dataframe(df_employees, use_container_width=True)
