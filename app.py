import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

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
# REAL GOOGLE SHEETS DATABASE CONNECTION & INITIALIZATION
# --------------------------------------------------------------------------------
# สร้างการเชื่อมต่อไปยัง Google Sheets (รองรับการดึงและบันทึกข้อมูลแบบเรียลไทม์)
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        st.session_state.properties = conn.read(worksheet="Properties", ttl="0m")
        st.session_state.employees = conn.read(worksheet="Employees", ttl="0m")
        st.session_state.tenants = conn.read(worksheet="Tenants", ttl="0m")
        st.session_state.leases = conn.read(worksheet="Leases", ttl="0m")
        st.session_state.payments = conn.read(worksheet="Payments", ttl="0m")
        st.session_state.initialized = True
    except Exception as e:
        st.error(f"❌ ไม่สามารถดึงข้อมูลจาก Google Sheets ได้: {e}")
        st.info("กรุณาตรวจสอบการตั้งค่าไฟล์ .streamlit/secrets.toml หรือตรวจสอบชื่อแผ่นงาน (Worksheet Names)")

# โหลดข้อมูลเมื่อเปิดแอปพลิเคชัน
if 'initialized' not in st.session_state:
    load_data()

# ฟังก์ชันสำหรับส่งข้อมูลชุดใหม่กลับไปบันทึกบน Google Sheets
def update_sheets_data(worksheet_name, updated_df):
    try:
        conn.update(worksheet=worksheet_name, data=updated_df)
        st.toast(f"💾 บันทึกข้อมูลลง Google Sheets ({worksheet_name}) เรียบร้อย!", icon="✅")
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดในการบันทึกข้อมูลลง Sheets: {e}")

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
    f"📊 [Google Sheets Database](https://docs.google.com/spreadsheets/d/1rOuS3DH6cLMYf0841LrwYcoNsa8IQFLUkxKRg-Kht90/edit?gid=1501708046#gid=1501708046)\n"
    f"📁 [Google Drive Storage](https://drive.google.com/drive/folders/14i1bb-NlhXDm2ybnTnfIzQexsoLPttnA)"
)

# ปุ่มกดรีเฟรชข้อมูลดึงจากชีตใหม่สด ๆ
if st.sidebar.button("🔄 รีเฟรชดึงข้อมูลใหม่จาก Sheets"):
    load_data()
    st.rerun()

# --------------------------------------------------------------------------------
# 1. DASHBOARD PAGE
# --------------------------------------------------------------------------------
if menu == "🏠 หน้าแรก (Dashboard)":
    st.title("📊 หน้าแรก / แผงควบคุมระบบ (Dashboard)")
    
    if 'properties' in st.session_state:
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
            # Tax notification count
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
                        f'</div>', 
                        unsafe_allow_html=True
                    )
            if not alert_triggered:
                st.write("ไม่มีนัดหมายลงตรวจแปลงนาในระยะนี้")

        with col3:
            st.subheader("💡 รายชื่อผู้เช่าค้างชำระค่าเช่า")
            # Simple due date check
            st.session_state.leases["วันครบกำหนดชำระค่าเช่า"] = pd.to_datetime(st.session_state.leases["วันครบกำหนดชำระค่าเช่า"]).dt.date
            overdue_leases = st.session_state.leases[st.session_state.leases["วันครบกำหนดชำระค่าเช่า"] < datetime.now().date()]
            if not overdue_leases.empty:
                for idx, row in overdue_leases.iterrows():
                    st.error(f"❌ {row['ชื่อคนเช่า']} | ค้างชำระ: {row['ที่นาหรือบ้านเช่า']} | ยอด: {row['เงินค่าเช่า']:,} บาท (กำหนด: {row['วันครบกำหนดชำระค่าเช่า']})")
            else:
                st.success("🎉 ไม่มีผู้เช่าค้างชำระในระบบขณะนี้")

        # Row 2: Comprehensive Overdue Table
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
            
            st.file_uploader("🖼️ อัปโหลดรูปที่ดิน (ระบบจำลอง)", accept_multiple_files=True)
            st.file_uploader("📄 อัพเอกสารสัญญา/โฉนด (PDF) (ระบบจำลอง)")
            
            submitted = st.form_submit_button("💾 บันทึกข้อมูลทรัพย์สิน")
            if submitted:
                new_data = {
                    "id": f"P{len(st.session_state.properties)+1:03d}", "ชื่อที่ดิน": p_name, "ประเภท": p_type,
                    "สถานะ": p_status, "ผู้เช่าปัจจุบัน": p_tenant, "ประเภทการเช่า": p_rent_type,
                    "เงินมัดจำ": p_deposit, "ค่าเช่า": p_rent, "พิกัด": p_geo, "วันครบชำระภาษี": str(p_tax_date),
                    "สถานะภาษี": p_tax_status, "รูปภาพ": "", "เอกสาร": ""
                }
                st.session_state.properties = pd.concat([st.session_state.properties, pd.DataFrame([new_data])], ignore_index=True)
                
                # บันทึกลง Google Sheets จริง
                update_sheets_data("Properties", st.session_state.properties)
                st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")
                st.rerun()

# --------------------------------------------------------------------------------
# 3. TENANT MANAGEMENT PAGE
# --------------------------------------------------------------------------------
elif menu == "👥 ข้อมูลผู้เช่า":
    st.title("👥 ระบบจัดการข้อมูลผู้เช่า")
    
    st.subheader("รายชื่อผู้เช่าปัจจุบัน")
    st.dataframe(st.session_state.tenants, use_container_width=True)
    
    with st.expander("➕ เพิ่มรายชื่อผู้เช่าใหม่"):
        with st.form("tenant_form"):
            t_name = st.text_input("ชื่อ-นามสกุล")
            t_address = st.text_area("ที่อยู่ตามทะเบียนบ้าน/ติดต่อ")
            t_phone = st.text_input("เบอร์โทรศัพท์")
            st.file_uploader("📄 แนบเอกสารตรวจสอบสิทธิ์ (ระบบจำลอง)")
            
            t_submit = st.form_submit_button("💾 เพิ่มผู้เช่า")
            if t_submit:
                new_t = {"ชื่อ": t_name, "ที่อยู่": t_address, "เบอร์โทร": t_phone, "เอกสาร": "", "สัญญาผูกพัน": "-"}
                st.session_state.tenants = pd.concat([st.session_state.tenants, pd.DataFrame([new_t])], ignore_index=True)
                
                # บันทึกลง Google Sheets จริง
                update_sheets_data("Tenants", st.session_state.tenants)
                st.success("เพิ่มข้อมูลผู้เช่าสำเร็จ!")
                st.rerun()

# --------------------------------------------------------------------------------
# 4. LEASE AGREEMENT PAGE
# --------------------------------------------------------------------------------
elif menu == "📋 สัญญาเช่า":
    st.title("📋 ระบบลงบันทึกสัญญาเช่า")
    
    st.subheader("รายการสัญญาเช่าที่มีผลบังคับใช้")
    st.dataframe(st.session_state.leases, use_container_width=True)
    
    with st.expander("➕ ทำสัญญาเช่าฉบับใหม่"):
        with st.form("lease_form"):
            l_id = st.text_input("เลขที่สัญญาเช่า", value=f"CNT{len(st.session_state.leases)+1:03d}")
            
            l_tenant = st.selectbox("เลือกผู้เช่า", st.session_state.tenants["ชื่อ"].tolist())
            vacant_props = st.session_state.properties[st.session_state.properties["สถานะ"]=="ว่าง"]["ชื่อที่ดิน"].tolist()
            all_props = st.session_state.properties["ชื่อที่ดิน"].tolist()
            l_prop = st.selectbox("เลือกที่ดิน/บ้านเช่า", vacant_props if vacant_props else all_props)
            
            l_dep = st.number_input("เงินมัดจำตามสัญญา (บาท)")
            l_rent = st.number_input("เงินค่าเช่าต่อรอบ (บาท)")
            l_due = st.date_input("วันครบกำหนดชำระค่าเช่างวดแรก/ถัดไป")
            st.file_uploader("📄 อัพโหลดไฟล์เอกสารตัวสัญญาเต็ม (ระบบจำลอง)")
            
            l_submit = st.form_submit_button("บันทึกสัญญาเช่า")
            if l_submit:
                phone_series = st.session_state.tenants[st.session_state.tenants["ชื่อ"]==l_tenant]["เบอร์โทร"].values
                phone = phone_series[0] if len(phone_series) > 0 else "-"
                
                new_l = {
                    "เลขที่สัญญาเช่า": l_id, "ชื่อคนเช่า": l_tenant, "เบอร์โทร": phone, 
                    "ที่นาหรือบ้านเช่า": l_prop, "เงินมัดจำ": l_dep, "เงินค่าเช่า": l_rent, 
                    "วันครบกำหนดชำระค่าเช่า": str(l_due), "เอกสารสัญญา": ""
                }
                st.session_state.leases = pd.concat([st.session_state.leases, pd.DataFrame([new_l])], ignore_index=True)
                
                # อัปเดตสถานะทรัพย์สิน
                st.session_state.properties.loc[st.session_state.properties["ชื่อที่ดิน"] == l_prop, "สถานะ"] = "มีคนเช่า"
                st.session_state.properties.loc[st.session_state.properties["ชื่อที่ดิน"] == l_prop, "ผู้เช่าปัจจุบัน"] = l_tenant
                
                # ซิงค์ข้อมูลทั้ง 2 แผ่นงานขึ้นคลาวด์
                update_sheets_data("Leases", st.session_state.leases)
                update_sheets_data("Properties", st.session_state.properties)
                
                st.success("บันทึกข้อมูลสัญญาเช่าเรียบร้อยแล้ว!")
                st.rerun()

# --------------------------------------------------------------------------------
# 5. PAYMENT ENTRY PAGE
# --------------------------------------------------------------------------------
elif menu == "💰 บันทึกการชำระเงิน":
    st.title("💰 ระบบบันทึกการชำระเงินค่างวดและออกใบเสร็จ")
    
    st.subheader("ประวัติบันทึกการรับชำระเงิน")
    st.dataframe(st.session_state.payments, use_container_width=True)
    
    st.write("---")
    st.subheader("✍️ บันทึกการรับชำระเงินใบใหม่ (Auto-fill Connected)")
    
    lease_ids = st.session_state.leases["เลขที่สัญญาเช่า"].tolist()
    selected_lease = st.selectbox("เลือกเลขที่สัญญาเช่าเชื่อมโยงข้อมูล", ["-- เลือกใบสัญญา --"] + lease_ids)
    
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
            pay_actual = st.number_input("ยอดเงินที่ชำระจริง", value=float(lease_row["เงินค่าเช่า"]))
            pay_date = st.date_input("วันที่ชำระเงินจริง")
            emp_receiver = st.selectbox("พนักงานผู้รับเงิน", st.session_state.employees["ชื่อ"].tolist() if 'employees' in st.session_state and not st.session_state.employees.empty else ["คีย์ข้อมูลเริ่มต้น"])
            st.file_uploader("📸 แนบหลักฐานการโอนเงิน/สลิปธนาคาร (ระบบจำลอง)")
            
            pay_submit = st.form_submit_button("💾 ยืนยันบันทึกการรับชำระและออกใบเสร็จ")
            if pay_submit:
                new_p = {
                    "เลขที่ใบชำระ": rec_id, "เลขที่สัญญาเช่า": selected_lease, "ชื่อคนเช่า": lease_row["ชื่อคนเช่า"], 
                    "เบอร์โทร": lease_row["เบอร์โทร"], "ชื่อบ้านเช่า_ที่นา": lease_row["ที่นาหรือบ้านเช่า"], 
                    "วันที่ครบกำหนด": str(lease_row["วันครบกำหนดชำระค่าเช่า"]), "ยอดเงินค่าเช่าที่ต้องชำระ": lease_row["เงินค่าเช่า"],
                    "วันที่ชำระ": str(pay_date), "ยอดเงินทีชำระ": pay_actual, "พนักงานที่รับเงิน": emp_receiver, "หลักฐานการชำระเงิน": ""
                }
                st.session_state.payments = pd.concat([st.session_state.payments, pd.DataFrame([new_p])], ignore_index=True)
                
                # เลื่อนดีลงวดถัดไปไปอีก 30 วัน
                current_due = pd.to_datetime(lease_row["วันครบกำหนดชำระค่าเช่า"]).date()
                st.session_state.leases.loc[st.session_state.leases["เลขที่สัญญาเช่า"] == selected_lease, "วันครบกำหนดชำระค่าเช่า"] = str(current_due + timedelta(days=30))
                
                # ซิงค์ข้อมูลขึ้น Google Sheets
                update_sheets_data("Payments", st.session_state.payments)
                update_sheets_data("Leases", st.session_state.leases)
                
                st.success("👍 บันทึกรับเงินเข้าคลังสำเร็จและซิงค์ข้อมูลลงระบบคลาวด์แล้ว!")
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
                    st.error("❌ บันทึกไม่สำเร็จ: รหัสผ่านของคุณต้องประกอบด้วย 'ตัวเลขเท่านั้นความยาว 6 หลัก' ตัวอย่างเช่น 123456")
                else:
                    new_e = {"ชื่อ": e_name, "username": e_user, "password": e_pass, "เบอร์โทร": e_phone, "ที่อยู่": e_addr}
                    st.session_state.employees = pd.concat([st.session_state.employees, pd.DataFrame([new_e])], ignore_index=True)
                    
                    # บันทึกลง Google Sheets จริง
                    update_sheets_data("Employees", st.session_state.employees)
                    st.success("บันทึกประวัติพนักงานรายใหม่สำเร็จ!")
                    st.rerun()
