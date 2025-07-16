import mysql.connector
import bcrypt
import streamlit as st
from utils.navbar import add_navbar
import datetime
st.set_page_config(page_title="HRBO Employee Onboarding", layout="wide")
 
def get_db_connection():
    return mysql.connector.connect(
            host='192.168.18.206',  
            user='root',
            password='mydb1234@XTI#2025',
            database='hrbo',
            port=3306,
            connect_timeout=10
    )
 
def create_user(user_data):
    hashed_pw = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode()
   
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (id, username, password, department, ismanager, PTO)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            user_data['id'],
            user_data['username'],
            hashed_pw,
            user_data['department'],
            user_data['ismanager'],
            user_data['PTO']
        ))
        conn.commit()
        st.success(f"✅ User '{user_data['username']}' created successfully.")
    except mysql.connector.Error as err:
        st.error(f"❌ Error: {err.msg}")
    finally:
        cursor.close()
        conn.close()
 
 
def create_employee(employee_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO employees (
                EMP_ID, FULL_NAME, FATHER_NAME, DEPARTMENT, DESIGNATION, REPORTING_MANAGER,
                DATE_OF_JOINING, PROBATION_END_DATE, MOBILE_NUMBER, EMAIL_OFFICIAL,
                CNIC_NUMBER, DATE_OF_BIRTH, RESIDENTIAL_ADDRESS, EMERGENCY_CONTACT_NUMBER,
                EMERGENCY_CONTACT_RELATION, BANK_NAME, ACCOUNT_TITLE, ACCOUNT_NUMBER,
                IBAN_NUMBER, EMP_IMAGE, SALARY
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            employee_data['EMP_ID'], employee_data['FULL_NAME'], employee_data['FATHER_NAME'],
            employee_data['DEPARTMENT'], employee_data['DESIGNATION'], employee_data['REPORTING_MANAGER'],
            employee_data['DATE_OF_JOINING'], employee_data['PROBATION_END_DATE'], employee_data['MOBILE_NUMBER'],
            employee_data['EMAIL_OFFICIAL'], employee_data['CNIC_NUMBER'], employee_data['DATE_OF_BIRTH'],
            employee_data['RESIDENTIAL_ADDRESS'], employee_data['EMERGENCY_CONTACT_NUMBER'],
            employee_data['EMERGENCY_CONTACT_RELATION'], employee_data['BANK_NAME'], employee_data['ACCOUNT_TITLE'],
            employee_data['ACCOUNT_NUMBER'], employee_data['IBAN_NUMBER'], employee_data['EMP_IMAGE'],
            employee_data['SALARY']
        ))
 
        conn.commit()
        st.success("✅ Employee data inserted successfully.")
    except mysql.connector.Error as err:
        st.error(f"❌ Database Error: {err.msg}")
    finally:
        cursor.close()
        conn.close()
 
def create_schedule(schedule_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            if day in schedule_data['HOLIDAYS_OF_WEEK']:
                in_time = out_time = "00:00:00"
            else:
                in_time = schedule_data['SCHEDULED_IN_TIME']
                out_time = schedule_data['SCHEDULED_OUT_TIME']
 
            cursor.execute("""
                INSERT INTO regular_schedule (EMPLOYEE_ID, EMPLOYEE_NAME, DAY_OF_WEEK, SCHEDULED_IN_TIME, SCHEDULED_OUT_TIME)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                schedule_data['EMPLOYEE_ID'],
                schedule_data['EMPLOYEE_NAME'],
                day,
                in_time,
                out_time
            ))
 
        conn.commit()
        st.success("✅ Weekly schedule created successfully with selected holidays.")
    except mysql.connector.Error as err:
        st.error(f"❌ Error: {err.msg}")
    finally:
        cursor.close()
        conn.close()
 
# get list of department from users  table
def get_departments():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT department FROM users")
        departments = [row[0] for row in cursor.fetchall() if row[0] is not None]
        return departments
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

add_navbar("Add Employees") 

st.title("📝 HRBO Employee Onboarding Form")
 
# SECTION: Employee Basic Info (hrbo.employees)
st.header("👤 Employee Details")
 
with st.container(border=True):
    st.subheader("1. Personal & Job Information 👔")
 
    EMP_ID = st.number_input("Employee ID *", min_value=1, format="%d", step=1)
    FULL_NAME = st.text_input("Full Name *")
    FATHER_NAME = st.text_input("Father's Name")
 
    # Fetch departments from DB and add "Add Department"
    department_options = get_departments() + ["Add Department"]
    DEPARTMENT_SELECTION = st.selectbox("Department *", options=department_options)
 
    if DEPARTMENT_SELECTION == "Add Department":
        new_department = st.text_input("Enter New Department Name")
        DEPARTMENT = new_department if new_department else None
    else:
        DEPARTMENT = DEPARTMENT_SELECTION
 
    DESIGNATION = st.text_input("Designation")
    REPORTING_MANAGER = st.text_input("Reporting Manager *")
    DATE_OF_JOINING = st.date_input("Date of Joining *", value=datetime.date.today())
    PROBATION_END_DATE = st.date_input("Probation End Date *", value=datetime.date.today() + datetime.timedelta(days=90))
 
    st.subheader("Contact Information")
 
    MOBILE_NUMBER = st.text_input("Mobile Number")
    EMAIL_OFFICIAL = st.text_input("Official Email")
    CNIC_NUMBER = st.text_input("CNIC Number")
    DATE_OF_BIRTH = st.date_input("Date of Birth", value=datetime.date(1990, 1, 1))
    RESIDENTIAL_ADDRESS = st.text_area("Residential Address")
    EMERGENCY_CONTACT_NUMBER = st.text_input("Emergency Contact Number")
    EMERGENCY_CONTACT_RELATION = st.text_input("Emergency Contact Relation")
 
    st.subheader("Banking Details")
 
    BANK_NAME = st.text_input("Bank Name")
    ACCOUNT_TITLE = st.text_input("Account Title")
    ACCOUNT_NUMBER = st.text_input("Account Number")
    IBAN_NUMBER = st.text_input("IBAN Number")
 
    st.subheader("Profile Photo and Salary")
 
    uploaded_file = st.file_uploader("Upload Employee Image", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        EMP_IMAGE = uploaded_file.read()
    else:
        with open("assets/avatar.jpg", "rb") as f:
            EMP_IMAGE = f.read()
                
    SALARY = st.number_input("Salary", min_value=0.00, step=0.01, format="%.2f")
 
    st.header("2. Regular Schedule 🕑")
 
    WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    HOLIDAYS_OF_WEEK = st.multiselect(
        "Select Weekly Holiday(s) *", WEEKDAYS, default=["Sunday"]
    )
    SCHEDULED_IN_TIME = st.time_input("Scheduled In Time *", value=datetime.time(21, 0))
    SCHEDULED_OUT_TIME = st.time_input("Scheduled Out Time *", value=datetime.time(6, 0))
 
    st.header("3. User Credentials 👥")
 
    username = st.text_input("Username *")
    password = st.text_input("Password *", type="password")
    ismanager = st.selectbox("Is Manager? *", ["Yes", "No"], index=1)
 
    # Submit button
    if st.button("Submit"):
        required_fields = [
            ("Employee ID", EMP_ID),
            ("Full Name", FULL_NAME),
            ("Department", DEPARTMENT),
            ("Reporting Manager", REPORTING_MANAGER),
            ("Date of Joining", DATE_OF_JOINING),
            ("Probation End Date", PROBATION_END_DATE),
            ("Holiday of Week", HOLIDAYS_OF_WEEK),
            ("Scheduled In Time", SCHEDULED_IN_TIME),
            ("Scheduled Out Time", SCHEDULED_OUT_TIME),
            ("Username", username),
            ("Password", password),
            ("Is Manager", ismanager)
        ]
 
        missing = [name for name, value in required_fields if not value]
        if missing:
            st.error(f"Please fill in all required fields: {', '.join(missing)}")
        else:
            st.success("✅ Employee data submitted successfully!")
 
            employees = {
                "EMP_ID": EMP_ID,
                "FULL_NAME": FULL_NAME,
                "FATHER_NAME": FATHER_NAME,
                "DEPARTMENT": DEPARTMENT,
                "DESIGNATION": DESIGNATION,
                "REPORTING_MANAGER": REPORTING_MANAGER,
                "DATE_OF_JOINING": str(DATE_OF_JOINING),
                "PROBATION_END_DATE": str(PROBATION_END_DATE),
                "MOBILE_NUMBER": MOBILE_NUMBER,
                "EMAIL_OFFICIAL": EMAIL_OFFICIAL,
                "CNIC_NUMBER": CNIC_NUMBER,
                "DATE_OF_BIRTH": str(DATE_OF_BIRTH),
                "RESIDENTIAL_ADDRESS": RESIDENTIAL_ADDRESS,
                "EMERGENCY_CONTACT_NUMBER": EMERGENCY_CONTACT_NUMBER,
                "EMERGENCY_CONTACT_RELATION": EMERGENCY_CONTACT_RELATION,
                "BANK_NAME": BANK_NAME,
                "ACCOUNT_TITLE": ACCOUNT_TITLE,
                "ACCOUNT_NUMBER": ACCOUNT_NUMBER,
                "IBAN_NUMBER": IBAN_NUMBER,
                "EMP_IMAGE": EMP_IMAGE,
                "SALARY": SALARY
            }
 
            schedule_data = {
                "EMPLOYEE_ID": EMP_ID,
                "EMPLOYEE_NAME": FULL_NAME,
                "HOLIDAYS_OF_WEEK": HOLIDAYS_OF_WEEK,  # ✅ Make sure this key name is exactly this
                "SCHEDULED_IN_TIME": str(SCHEDULED_IN_TIME),
                "SCHEDULED_OUT_TIME": str(SCHEDULED_OUT_TIME)
            }
            user_data = {
                "id": EMP_ID,
                "username": username,
                "password": password,
                "department": DEPARTMENT,
                "ismanager": ismanager,
                "PTO": None
            }
 
            create_user(user_data)
            create_employee(employees)
            create_schedule(schedule_data)