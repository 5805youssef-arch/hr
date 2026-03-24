import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import os
import json
import os
import json

# --- 1. إعدادات الإيميل ---
SENDER_EMAIL = st.secrets["EMAIL"]
SENDER_PASSWORD = st.secrets["PASSWORD"]
# --- إعدادات الإيميل ---
SENDER_EMAIL = st.secrets["EMAIL"]
SENDER_PASSWORD = st.secrets["PASSWORD"]

def send_email(employee_email, employee_name, infraction, penalty, comment):
    subject = f"إشعار إداري: {penalty.split('(')[0]}"
def send_email(employee_email, employee_name, incident, penalty, comment):
    subject = "Disciplinary Action Notice"
    body = f"""
    Dear {employee_name},
    
    Please be advised that the following note has been recorded:
    Incident: {incident}
    Disciplinary Action: {penalty}
    HR Comments: {comment}
    
    Please ensure compliance with company policies.
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
        st.error(f"Error sending email: {e}")

# --- 2. إدارة الملفات والبيانات ---
st.set_page_config(page_title="HR System", page_icon="🟨", layout="centered")
st.title("نظام إدارة إنذارات الموظفين 🟨⬛")
# --- إدارة الملفات ---
st.set_page_config(page_title="HR Disciplinary System", page_icon="⚖️", layout="centered")
st.title("نظام إدارة الإجراءات التأديبية ⚖️")

EXCEL_FILE = "penalties_log.xlsx"
MATRIX_FILE = "matrix.xlsx"
EMP_FILE = "employees.json"

EXCEL_FILE = "penalties_log.xlsx"
INFRACTIONS_FILE = "infractions.txt"
EMP_FILE = "employees.json"

# تحميل الإكسيل
if os.path.exists(EXCEL_FILE):
    log_df = pd.read_excel(EXCEL_FILE)
else:
    log_df = pd.DataFrame(columns=["Employee", "Email", "Infraction", "Penalty", "Comment", "Date"])
# تحميل مصفوفة العقوبات
try:
    matrix_df = pd.read_excel(MATRIX_FILE)
    categories = matrix_df['Category'].unique().tolist()
except FileNotFoundError:
    st.error("⚠️ ملف matrix.xlsx غير موجود. يرجى رفعه أولاً.")
    st.stop()

# تحميل سجل العقوبات (تم تغيير Infraction إلى Incident لتطابق الملف الجديد)
if os.path.exists(EXCEL_FILE):
    log_df = pd.read_excel(EXCEL_FILE)
else:
    log_df = pd.DataFrame(columns=["Employee", "Email", "Category", "Incident", "Penalty", "Comment", "Date"])

# تحميل الأخطاء
if os.path.exists(INFRACTIONS_FILE):
    with open(INFRACTIONS_FILE, "r", encoding="utf-8") as f:
        infractions_list = [line.strip() for line in f.readlines() if line.strip()]
else:
    infractions_list = ["تأخير في الرد", "عدم عمل فولو اب", "الوصول متأخراً لمقر العمل"]
    with open(INFRACTIONS_FILE, "w", encoding="utf-8") as f:
        for inf in infractions_list: f.write(inf + "\n")

# تحميل الموظفين
if os.path.exists(EMP_FILE):
    with open(EMP_FILE, "r", encoding="utf-8") as f:
        employees = json.load(f)
else:
    employees = {"yousef": "youssefeldakar5@gmail.com", "Sara": "sara@example.com"}
    with open(EMP_FILE, "w", encoding="utf-8") as f:
        json.dump(employees, f)

# --- 3. تقسيم الموقع لصفحتين (Tabs) ---
tab1, tab2 = st.tabs(["📝 تسجيل مخالفة", "⚙️ لوحة تحكم الإدارة (HR)"])

# ==========================================
# الصفحة الأولى: تسجيل المخالفات
# ==========================================
with tab1:
    # إظهار رسالة النجاح لو موجودة من العملية السابقة
    if "success_message" in st.session_state:
        st.success(st.session_state.success_message)
        del st.session_state.success_message

    with st.form("penalty_form"):
        # لو مفيش موظفين، نعرض رسالة تحذير
        if not employees:
            st.warning("برجاء إضافة موظفين (Agents) من لوحة التحكم أولاً.")
            emp_name = None
        else:
            emp_name = st.selectbox("اختر الموظف", list(employees.keys()))
            
        infraction = st.selectbox("نوع الخطأ", infractions_list)
        comment = st.text_area("تعليق / ملاحظات")
        
        submitted = st.form_submit_button("إرسال الإشعار (Submit)")

        if submitted and emp_name:
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

            # تحديد العقوبة والتحديث للإنذار الرابع
            if penalty_count == 0:
                final_penalty = "Yellow Card (إنذار أول)"
            elif penalty_count == 1:
                final_penalty = "Yellow Card (إنذار ثاني)"
            elif penalty_count == 2:
                final_penalty = "Black Card (خصم يومين + حرمان من الترقية 90 يوم)"
            else:
                final_penalty = "Black Card (إنذار متكرر: خصم يومين إضافيين + إعادة حساب 90 يوم حرمان من اليوم)"

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
            
            # حفظ رسالة النجاح في الذاكرة عشان تظهر بعد الـ Rerun
            st.session_state.success_message = f"✅ تم تسجيل الإجراء بنجاح: إرسال إيميل لـ ({emp_name}) بالعقوبة: {final_penalty}"
            st.rerun()

# ==========================================
# الصفحة الثانية: لوحة التحكم 
# ==========================================
with tab2:
    # 1. إدارة الموظفين
    st.subheader("👥 إدارة الموظفين (Agents)")
    col_emp1, col_emp2 = st.columns(2)
    with col_emp1:
        st.markdown("**إضافة موظف جديد**")
        new_emp_name = st.text_input("اسم الموظف:")
        new_emp_email = st.text_input("إيميل الموظف:")
        if st.button("➕ إضافة موظف"):
            if new_emp_name and new_emp_email:
                employees[new_emp_name] = new_emp_email
                with open(EMP_FILE, "w", encoding="utf-8") as f: json.dump(employees, f)
                st.success(f"تم إضافة {new_emp_name} بنجاح!")
                st.rerun()
                
    with col_emp2:
        st.markdown("**مسح موظف حالي**")
        if employees:
            emp_to_remove = st.selectbox("اختر الموظف المراد مسحه:", list(employees.keys()))
            if st.button("🗑️ مسح الموظف"):
                del employees[emp_to_remove]
                with open(EMP_FILE, "w", encoding="utf-8") as f: json.dump(employees, f)
                st.success("تم مسح الموظف بنجاح!")
                st.rerun()

    st.write("---")

    # 2. إدارة الأخطاء
    st.subheader("⚠️ إدارة أنواع الأخطاء")
    col_inf1, col_inf2 = st.columns(2)
    with col_inf1:
        new_infraction = st.text_input("اكتب اسم الخطأ الجديد هنا:")
        if st.button("➕ إضافة خطأ للقائمة"):
            if new_infraction and new_infraction not in infractions_list:
                infractions_list.append(new_infraction)
                with open(INFRACTIONS_FILE, "w", encoding="utf-8") as f:
                    for inf in infractions_list: f.write(inf + "\n")
                st.success("تمت الإضافة بنجاح!")
                st.rerun()
    with col_inf2:
        inf_to_remove = st.selectbox("اختر خطأ لمسحه من القائمة:", infractions_list)
        if st.button("🗑️ مسح الخطأ"):
            infractions_list.remove(inf_to_remove)
            with open(INFRACTIONS_FILE, "w", encoding="utf-8") as f:
                for inf in infractions_list: f.write(inf + "\n")
            st.success("تم مسح الخطأ!")
            st.rerun()

    st.write("---")
    
    # 3. إدارة العقوبات (الإكسيل)
    st.subheader("❌ إدارة وإلغاء العقوبات المسجلة")
    st.info("لحذف عقوبة مسجلة (لإلغاء تأثيرها)، اختر 'رقم الصف' الخاص بها من الجدول واضغط حذف.")
    
    if not log_df.empty:
        st.dataframe(log_df, use_container_width=True)
        record_to_delete = st.selectbox("اختر رقم الصف (Index) المراد حذفه:", log_df.index)
        if st.button("حذف العقوبة نهائياً 🗑️"):
            log_df = log_df.drop(index=record_to_delete)
            log_df.to_excel(EXCEL_FILE, index=False)
            st.success("تم حذف العقوبة بنجاح ولن تُحسب على الموظف!")
            st.rerun()
            
        st.write("---")
        with open(EXCEL_FILE, "rb") as file:
            st.download_button(label="📥 تحميل ملف الإكسيل كاملاً", data=file, file_name="penalties_log.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.warning("لا توجد أي عقوبات مسجلة حالياً.")

# تحميل الموظفين
if os.path.exists(EMP_FILE):
    with open(EMP_FILE, "r", encoding="utf-8") as f:
        employees = json.load(f)
else:
    employees = {"yousef": "youssefeldakar5@gmail.com"}
    with open(EMP_FILE, "w", encoding="utf-8") as f: json.dump(employees, f)

# --- دالة حساب مستوى الخطأ بناءً على عمود Within (Days) المخصص لكل خطأ ---
def calculate_infraction_level(emp_name, incident_name, reset_days):
    if log_df.empty:
        return 0
    
    # فلترة السجل لنفس الموظف ونفس الخطأ بالظبط
    history = log_df[(log_df['Employee'] == emp_name) & (log_df['Incident'] == incident_name)].copy()
    
    if history.empty:
        return 0
        
    history['Date'] = pd.to_datetime(history['Date'])
    history = history.sort_values(by='Date')
    dates = history['Date'].tolist()
    
    level = 1
    # حساب السلسلة: لو بين كل خطأ واللي قبله مدة أقل من أو تساوي الـ reset_days
    for i in range(1, len(dates)):
        if (dates[i] - dates[i-1]).days <= reset_days:
            level += 1
        else:
            level = 1 # تصفير
            
    # التحقق من المسافة بين آخر خطأ واليوم
    if (datetime.now() - dates[-1]).days > reset_days:
        level = 0 # تصفير لأن آخر خطأ عدى عليه المدة المحددة
        
    return level

# --- تقسيم الموقع لصفحتين ---
tab1, tab2 = st.tabs(["📝 تسجيل مخالفة", "⚙️ لوحة تحكم الإدارة (HR)"])

# ==========================================
# الصفحة الأولى: تسجيل المخالفات
# ==========================================
with tab1:
    if "success_message" in st.session_state:
        st.success(st.session_state.success_message)
        del st.session_state.success_message

    with st.form("penalty_form"):
        if not employees:
            st.warning("برجاء إضافة موظفين أولاً.")
            emp_name = None
        else:
            emp_name = st.selectbox("اختر الموظف", list(employees.keys()))
            
        selected_category = st.selectbox("القسم (Category)", categories)
        
        # فلترة الأخطاء بناءً على القسم المختار
        incidents_in_cat = matrix_df[matrix_df['Category'] == selected_category]['Incident'].tolist()
        incident = st.selectbox("نوع الخطأ (Incident)", incidents_in_cat)
        
        # سحب التفاصيل (Details) ومدة التصفير (Within Days) من المصفوفة
        incident_row = matrix_df[(matrix_df['Category'] == selected_category) & (matrix_df['Incident'] == incident)]
        details = incident_row['Details'].values[0]
        reset_days = int(incident_row['Within (Days)'].values[0])
        
        # عرض التفاصيل للموارد البشرية للتأكيد
        st.info(f"**Details:** {details}\n\n**Reset Period:** {reset_days} Days")
        
        comment = st.text_area("تعليق / ملاحظات")
        submitted = st.form_submit_button("إرسال الإشعار (Submit)")

        if submitted and emp_name:
            # تمرير رقم أيام التصفير للدالة
            current_level = calculate_infraction_level(emp_name, incident, reset_days)
            next_action_index = current_level + 1 
            
            # أسماء الأعمدة الجديدة حسب الملف الأصلي
            action_columns = ["1st time", "2nd time", "3rd time", "4th time", "5th time", "6th time", "7th time", "8th time"]
            
            if next_action_index > len(action_columns):
                st.error("❌ لا يمكن تسجيل هذه المخالفة! الموظف استنفذ جميع الإجراءات التأديبية لهذا الخطأ.")
            else:
                action_col_name = action_columns[next_action_index - 1]
                
                final_penalty = incident_row[action_col_name].values[0]
                
                if pd.isna(final_penalty) or str(final_penalty).strip() == "":
                    st.error("❌ لا يمكن إعطاء عقوبة إضافية. الموظف استنفذ الحد الأقصى للإجراءات في هذه المخالفة المحددة.")
                else:
                    emp_email = employees[emp_name]
                    current_date = datetime.now()
                    
                    new_record = pd.DataFrame({
                        "Employee": [emp_name],
                        "Email": [emp_email],
                        "Category": [selected_category],
                        "Incident": [incident],
                        "Penalty": [final_penalty],
                        "Comment": [comment],
                        "Date": [current_date.strftime("%Y-%m-%d")]
                    })
                    
                    log_df = pd.concat([log_df, new_record], ignore_index=True)
                    log_df.to_excel(EXCEL_FILE, index=False)
                    
                    send_email(emp_email, emp_name, incident, final_penalty, comment)
                    
                    st.session_state.success_message = f"✅ تم تسجيل المخالفة ({action_col_name}): {final_penalty}"
                    st.rerun()

# ==========================================
# الصفحة الثانية: لوحة التحكم 
# ==========================================
with tab2:
    st.subheader("👥 إدارة الموظفين")
    col_emp1, col_emp2 = st.columns(2)
    with col_emp1:
        new_emp_name = st.text_input("اسم الموظف:")
        new_emp_email = st.text_input("إيميل الموظف:")
        if st.button("➕ إضافة موظف"):
            if new_emp_name and new_emp_email:
                employees[new_emp_name] = new_emp_email
                with open(EMP_FILE, "w", encoding="utf-8") as f: json.dump(employees, f)
                st.success("تم الإضافة!")
                st.rerun()
                
    with col_emp2:
        if employees:
            emp_to_remove = st.selectbox("مسح موظف:", list(employees.keys()))
            if st.button("🗑️ مسح"):
                del employees[emp_to_remove]
                with open(EMP_FILE, "w", encoding="utf-8") as f: json.dump(employees, f)
                st.success("تم المسح!")
                st.rerun()

    st.write("---")
    st.subheader("❌ إدارة وإلغاء العقوبات المسجلة")
    st.info("لحذف عقوبة مسجلة (لإلغاء تأثيرها)، اختر 'رقم الصف' من الجدول واضغط حذف.")
    
    if not log_df.empty:
        st.dataframe(log_df, use_container_width=True)
        record_to_delete = st.selectbox("اختر رقم الصف (Index) للحذف:", log_df.index)
        if st.button("حذف العقوبة نهائياً 🗑️"):
            log_df = log_df.drop(index=record_to_delete)
            log_df.to_excel(EXCEL_FILE, index=False)
            st.success("تم الحذف بنجاح!")
            st.rerun()
            
        st.write("---")
        with open(EXCEL_FILE, "rb") as file:
            st.download_button(label="📥 تحميل السجل بالكامل (Excel)", data=file, file_name="penalties_log.xlsx")
    else:
        st.warning("لا توجد عقوبات مسجلة.")