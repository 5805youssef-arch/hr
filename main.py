import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import os

# --- 1. إعدادات الإيميل ---
SENDER_EMAIL = "yahiazakaria412@gmail.com"
SENDER_PASSWORD = "hhvnrralywerawbb"

def send_email(employee_email, employee_name, infraction, penalty, comment):
    subject = f"إشعار إداري: {penalty}"
    body = f"""
    مرحباً {employee_name}،
    
    يرجى العلم بأنه تم تسجيل الملاحظة التالية:
    الخطأ: {infraction}
    القرار الإداري: {penalty}
    ملاحظات الـ HR: {comment}
    
    برجاء الالتزام بتعليمات العمل.
    """
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = employee_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        st.error(f"حدث خطأ أثناء إرسال الإيميل: {e}")

# --- 2. إدارة الملفات ---
st.set_page_config(page_title="HR System", page_icon="🟨", layout="centered")
st.title("نظام إدارة إنذارات الموظفين 🟨⬛")

EXCEL_FILE = "penalties_log.xlsx"
INFRACTIONS_FILE = "infractions.txt"

# تحميل ملف الإكسيل
if os.path.exists(EXCEL_FILE):
    log_df = pd.read_excel(EXCEL_FILE)
else:
    log_df = pd.DataFrame(columns=["Employee", "Email", "Infraction", "Penalty", "Comment", "Date"])

# تحميل قائمة الأخطاء القابلة للتعديل
if os.path.exists(INFRACTIONS_FILE):
    with open(INFRACTIONS_FILE, "r", encoding="utf-8") as f:
        infractions_list = [line.strip() for line in f.readlines() if line.strip()]
else:
    infractions_list = ["تأخير في الرد", "عدم عمل فولو اب", "الوصول متأخراً لمقر العمل"]
    with open(INFRACTIONS_FILE, "w", encoding="utf-8") as f:
        for inf in infractions_list:
            f.write(inf + "\n")

# بيانات الموظفين
employees = {"yousef": "youssefeldakar5@gmail.com", "Sara": "sara@example.com"}

# --- 3. تقسيم الموقع لصفحتين (Tabs) ---
tab1, tab2 = st.tabs(["📝 تسجيل مخالفة", "⚙️ لوحة تحكم الإدارة (HR)"])

# ==========================================
# الصفحة الأولى: تسجيل المخالفات
# ==========================================
with tab1:
    with st.form("penalty_form"):
        emp_name = st.selectbox("اختر الموظف", list(employees.keys()))
        infraction = st.selectbox("نوع الخطأ", infractions_list)
        comment = st.text_area("تعليق / ملاحظات")
        
        submitted = st.form_submit_button("إرسال الإشعار (Submit)")

        if submitted:
            emp_email = employees[emp_name]
            current_date = datetime.now()
            thirty_days_ago = current_date - timedelta(days=30)
            
            # تطبيق منطق الـ 30 يوم
            if not log_df.empty:
                log_df['Date'] = pd.to_datetime(log_df['Date'])
                recent_penalties = log_df[(log_df['Employee'] == emp_name) & (log_df['Date'] >= thirty_days_ago)]
                penalty_count = len(recent_penalties)
            else:
                penalty_count = 0

            if penalty_count == 0:
                final_penalty = "Yellow Card (إنذار أول)"
            elif penalty_count == 1:
                final_penalty = "Yellow Card (إنذار ثاني)"
            else:
                final_penalty = "Black Card (خصم يومين + حرمان من الترقية 90 يوم)"

            new_record = pd.DataFrame({
                "Employee": [emp_name],
                "Email": [emp_email],
                "Infraction": [infraction],
                "Penalty": [final_penalty],
                "Comment": [comment],
                "Date": [current_date.strftime("%Y-%m-%d")]
            })
            
            log_df = pd.concat([log_df, new_record], ignore_index=True)
            log_df.to_excel(EXCEL_FILE, index=False)
            
            send_email(emp_email, emp_name, infraction, final_penalty, comment)
            
            st.success(f"تم تسجيل الإجراء بنجاح كـ {final_penalty} وإرسال الإيميل للموظف وتحديث ملف الإكسيل.")
            st.rerun() # تحديث الصفحة أوتوماتيك لظهور البيانات الجديدة

# ==========================================
# الصفحة الثانية: لوحة التحكم (إضافة أخطاء / حذف عقوبات)
# ==========================================
with tab2:
    st.subheader("➕ إضافة نوع خطأ جديد")
    col1, col2 = st.columns([3, 1])
    with col1:
        new_infraction = st.text_input("اكتب اسم الخطأ الجديد هنا:")
    with col2:
        st.write("") # تظبيط المسافات
        st.write("")
        if st.button("إضافة للقائمة"):
            if new_infraction and new_infraction not in infractions_list:
                infractions_list.append(new_infraction)
                with open(INFRACTIONS_FILE, "w", encoding="utf-8") as f:
                    for inf in infractions_list:
                        f.write(inf + "\n")
                st.success("تمت الإضافة بنجاح!")
                st.rerun()
            elif new_infraction in infractions_list:
                st.warning("هذا الخطأ موجود بالفعل.")

    st.write("---")
    
    st.subheader("❌ إدارة وإلغاء العقوبات")
    st.info("لحذف عقوبة، انظر إلى 'رقم الصف' في الجدول أسفله، ثم اختر الرقم من القائمة واضغط حذف.")
    
    if not log_df.empty:
        st.dataframe(log_df, use_container_width=True)
        
        # قسم الحذف
        record_to_delete = st.selectbox("اختر رقم الصف (Index) المراد حذفه:", log_df.index)
        if st.button("حذف العقوبة نهائياً 🗑️"):
            log_df = log_df.drop(index=record_to_delete)
            log_df.to_excel(EXCEL_FILE, index=False)
            st.success("تم حذف العقوبة بنجاح ولن تُحسب على الموظف!")
            st.rerun()
            
        # قسم التحميل
        st.write("---")
        with open(EXCEL_FILE, "rb") as file:
            st.download_button(
                label="📥 تحميل ملف الإكسيل كاملاً",
                data=file,
                file_name="penalties_log.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.warning("لا توجد أي عقوبات مسجلة حالياً.")
