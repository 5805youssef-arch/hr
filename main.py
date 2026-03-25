import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import plotly.express as px

# ==========================================
# 1. إعدادات النظام وقاموس العقوبات 
# ==========================================
st.set_page_config(page_title="HR Disciplinary System", page_icon="⚖️", layout="wide")

PENALTY_MAP = {
    "Yellow": {"label": "إشعار أداء (Performance Notice)", "deduction_hours": 0, "deduction_days": 0, "freeze_months": 0},
    "Orange": {"label": "لفت نظر (Performance Flag)", "deduction_hours": 4.5, "deduction_days": 0, "freeze_months": 0},
    "Red": {"label": "إنذار أداء (Performance Alert)", "deduction_hours": 0, "deduction_days": 2, "freeze_months": 0},
    "Black": {"label": "تحذير نهائي (Performance Warning)", "deduction_hours": 0, "deduction_days": 4, "freeze_months": 3},
    "Investigation": {"label": "إيقاف للتحقيق (Suspended / Investigation)", "deduction_hours": 0, "deduction_days": 0, "freeze_months": 0},
}

SENDER_EMAIL = st.secrets.get("EMAIL", "")
SENDER_PASSWORD = st.secrets.get("PASSWORD", "")
HR_MANAGER_EMAIL = st.secrets.get("HR_MANAGER_EMAIL", SENDER_EMAIL)
HR_ADMIN_PASSWORD = st.secrets.get("HR_ADMIN_PASSWORD", "1234")

# ==========================================
# 2. إعداد قاعدة البيانات 
# ==========================================
DB_FILE = "hr_system.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS employees 
                 (id INTEGER PRIMARY KEY, name TEXT UNIQUE, email TEXT, department TEXT, manager_email TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS violations 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, employee_name TEXT, category TEXT, 
                 incident TEXT, penalty_color TEXT, penalty_label TEXT, deduction_hours REAL, 
                 deduction_days INTEGER, freeze_months INTEGER, comment TEXT, 
                 submitted_by TEXT, created_at DATETIME)''')
    conn.commit()
    conn.close()

init_db()

def get_db_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

# ==========================================
# 3. دوال مساعدة (Email)
# ==========================================
def send_email(emp_email, manager_email, emp_name, category, incident, penalty_color, comment):
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        st.error("⚠️ إعدادات الإيميل (Secrets) غير متوفرة.")
        return False
        
    p_info = PENALTY_MAP.get(penalty_color, PENALTY_MAP["Yellow"])
    
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = emp_email
    
    receivers = [emp_email]
    if manager_email:
        msg['Cc'] = manager_email
        receivers.append(manager_email)
        
    if penalty_color == "Investigation":
        msg['Subject'] = f"عاجل: إيقاف عن العمل للتحقيق - {emp_name}"
        msg['Cc'] = f"{manager_email},{HR_MANAGER_EMAIL}" if manager_email else HR_MANAGER_EMAIL
        receivers.append(HR_MANAGER_EMAIL)
        body = f"""مرحباً {emp_name}،\n\nيرجى العلم بأنه تم إيقافك مؤقتاً عن العمل وتحويلك للتحقيق بناءً على الملاحظة التالية:\nالنوع: {category}\nالخطأ: {incident}\nملاحظات الإدارة: {comment}\n\nسيتم التواصل معك من قبل الموارد البشرية قريباً."""
    else:
        msg['Subject'] = f"إشعار إداري: {p_info['label']}"
        body = f"""مرحباً {emp_name}،\n\nتم تسجيل الإجراء الإداري التالي في سجلك:\n- الخطأ: {incident} ({category})\n- القرار: {p_info['label']}\n- الخصم: {p_info['deduction_days']} أيام و {p_info['deduction_hours']} ساعات\n- تجميد الترقية: {p_info['freeze_months']} شهور\n- ملاحظات: {comment}\n\nبرجاء الالتزام بتعليمات العمل."""

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, receivers, msg.as_string())
        return True
    except Exception as e:
        st.error(f"حدث خطأ أثناء إرسال الإيميل: {e}")
        return False

# ==========================================
# 4. محاكاة مصفوفة العقوبات 
# ==========================================
CATEGORIES = ["الحضور والانصراف", "السلوك الشخصي", "إساءة الاستخدام", "سياسات العمل"]
INCIDENTS = ["تأخير في الرد", "عدم عمل فولو اب", "الوصول متأخراً لمقر العمل", "الغياب بدون إذن"]

def validate_reset_days(raw_days):
    try:
        days = int(float(str(raw_days).split('.')[0]))
        if 1 <= days <= 730:
            return days
    except:
        pass
    return 30 

# ==========================================
# 5. نظام الحماية للتبويبات
# ==========================================
def check_password(tab_id):
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        pwd = st.text_input("🔑 أدخل كلمة مرور الـ HR للوصول لهذه الصفحة:", type="password", key=f"pwd_input_{tab_id}")
        if st.button("تسجيل الدخول", key=f"login_btn_{tab_id}"):
            if pwd == HR_ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("كلمة المرور غير صحيحة.")
        return False
    return True

# ==========================================
# 6. واجهة المستخدم (UI & Tabs)
# ==========================================
st.title("نظام إدارة إنذارات الموظفين 🟨⬛")

tab1, tab2, tab3 = st.tabs(["📝 تسجيل مخالفة", "⚙️ لوحة الإدارة (مؤمنة)", "📊 التقارير (مؤمنة)"])

# ---------------- Tab 1: تسجيل المخالفة ----------------
with tab1:
    conn = get_db_connection()
    employees_df = pd.read_sql_query("SELECT * FROM employees", conn)
    
    if employees_df.empty:
        st.warning("برجاء إعداد بيانات الموظفين من لوحة الإدارة أولاً.")
    else:
        with st.form("penalty_form"):
            st.subheader("إدخال تفاصيل المخالفة")
            
            # تم إزالة required=True من هنا
            submitted_by = st.text_input("اسم المدخل (HR Rep Name):")
            
            col1, col2 = st.columns(2)
            with col1:
                emp_name = st.selectbox("اختر الموظف", employees_df['name'].tolist())
                category = st.selectbox("تصنيف المخالفة", CATEGORIES)
            with col2:
                incident = st.selectbox("نوع الخطأ", INCIDENTS)
                reset_days_input = st.number_input("فترة السماح (Reset Days)", min_value=1, max_value=730, value=30)
            
            is_investigation = st.checkbox("🔴 تحويل مباشر للتحقيق (Investigation Workflow)")
            comment = st.text_area("تعليق / ملاحظات (Alignment details)")
            
            submitted = st.form_submit_button("إرسال الإشعار وتسجيل العقوبة")

            if submitted:
                if not submitted_by:
                    st.error("⚠️ برجاء كتابة اسم المدخل (HR Rep Name) قبل الإرسال.")
                else:
                    emp_data = employees_df[employees_df['name'] == emp_name].iloc[0]
                    emp_email = emp_data['email']
                    manager_email = emp_data['manager_email']
                    current_date = datetime.now()
                    
                    reset_days = validate_reset_days(reset_days_input)
                    cutoff_date = current_date - timedelta(days=reset_days)
                    
                    if is_investigation:
                        final_color = "Investigation"
                    else:
                        c = conn.cursor()
                        c.execute('''SELECT COUNT(*) FROM violations 
                                     WHERE employee_name=? AND incident=? AND created_at >= ? AND penalty_color != 'Investigation' ''', 
                                  (emp_name, incident, cutoff_date.strftime("%Y-%m-%d %H:%M:%S")))
                        penalty_count = c.fetchone()[0]
                        
                        escalation_colors = ["Yellow", "Orange", "Red", "Black", "Black", "Black", "Black", "Black"]
                        if penalty_count >= 8:
                            st.error("⚠️ الموظف تجاوز الحد الأقصى للمخالفات (8 مرات). برجاء اتخاذ إجراء إداري علوي.")
                            st.stop()
                        else:
                            final_color = escalation_colors[penalty_count]

                    p_info = PENALTY_MAP[final_color]
                    c = conn.cursor()
                    c.execute('''INSERT INTO violations 
                                 (employee_name, category, incident, penalty_color, penalty_label, 
                                 deduction_hours, deduction_days, freeze_months, comment, submitted_by, created_at) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                              (emp_name, category, incident, final_color, p_info['label'], 
                               p_info['deduction_hours'], p_info['deduction_days'], p_info['freeze_months'], 
                               comment, submitted_by, current_date.strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    
                    email_sent = send_email(emp_email, manager_email, emp_name, category, incident, final_color, comment)
                    
                    if email_sent:
                        st.success(f"✅ تم تسجيل العقوبة ({p_info['label']}) بنجاح وإرسال الإشعارات.")
                    else:
                        st.warning(f"تم تسجيل العقوبة ({p_info['label']}) في السجل، لكن فشل إرسال الإيميل.")
    conn.close()

# ---------------- Tab 2: لوحة الإدارة ----------------
with tab2:
    if check_password("tab2"):
        conn = get_db_connection()
        st.subheader("👥 إدارة الموظفين")
        
        with st.form("add_emp_form"):
            e_name = st.text_input("اسم الموظف")
            e_email = st.text_input("إيميل الموظف")
            e_dept = st.text_input("القسم (Department)")
            e_manager = st.text_input("إيميل المدير المباشر (لإرسال الـ CC)")
            if st.form_submit_button("إضافة / تحديث الموظف"):
                c = conn.cursor()
                c.execute("INSERT OR REPLACE INTO employees (name, email, department, manager_email) VALUES (?, ?, ?, ?)", 
                          (e_name, e_email, e_dept, e_manager))
                conn.commit()
                st.success("تم تحديث بيانات الموظف.")
                st.rerun()
                
        st.write("---")
        st.subheader("❌ مسح العقوبات")
        v_df = pd.read_sql_query("SELECT id, employee_name, incident, penalty_label, created_at FROM violations", conn)
        if not v_df.empty:
            st.dataframe(v_df, use_container_width=True)
            v_id = st.selectbox("اختر رقم الـ ID للعقوبة المراد مسحها:", v_df['id'])
            if st.button("حذف العقوبة نهائياً"):
                conn.cursor().execute("DELETE FROM violations WHERE id=?", (v_id,))
                conn.commit()
                st.success("تم الحذف.")
                st.rerun()
        conn.close()
        
        if st.button("تسجيل الخروج", key="logout_tab2"):
            st.session_state.authenticated = False
            st.rerun()

# ---------------- Tab 3: التقارير والإحصائيات ----------------
with tab3:
    if check_password("tab3"):
        conn = get_db_connection()
        st.header("📊 لوحة تحكم التقارير")
        
        violations_df = pd.read_sql_query("SELECT * FROM violations", conn)
        
        if violations_df.empty:
            st.info("لا توجد بيانات كافية لعرض التقارير.")
        else:
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.subheader("المخالفات حسب التصنيف")
                fig1 = px.pie(violations_df, names='category', title='توزيع أنواع المخالفات')
                st.plotly_chart(fig1, use_container_width=True)
                
            with col_chart2:
                st.subheader("أكثر الموظفين مخالفة")
                emp_counts = violations_df['employee_name'].value_counts().reset_index()
                emp_counts.columns = ['employee_name', 'count']
                fig2 = px.bar(emp_counts, x='employee_name', y='count', title='عدد المخالفات لكل موظف')
                st.plotly_chart(fig2, use_container_width=True)
            
            st.write("---")
            st.subheader("⚠️ سجل الخصومات وتجميد الترقيات (للتصدير لشؤون العاملين)")
            
            violations_df['created_at'] = pd.to_datetime(violations_df['created_at'])
            violations_df['freeze_end_date'] = violations_df.apply(
                lambda row: (row['created_at'] + pd.DateOffset(months=int(row['freeze_months']))) if row['freeze_months'] > 0 else None, axis=1
            )
            violations_df['is_frozen'] = violations_df['freeze_end_date'].apply(
                lambda d: "نعم (مجمد)" if pd.notnull(d) and d > datetime.now() else "لا"
            )
            
            export_df = violations_df[['employee_name', 'incident', 'penalty_label', 'deduction_days', 'deduction_hours', 'freeze_end_date', 'is_frozen', 'created_at']]
            st.dataframe(export_df, use_container_width=True)
            
            csv = export_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(label="📥 تصدير التقرير المالي كـ CSV", data=csv, file_name="payroll_deductions_report.csv", mime="text/csv")
            
        if st.button("تسجيل الخروج", key="logout_tab3"):
            st.session_state.authenticated = False
            st.rerun()
            
        conn.close()
