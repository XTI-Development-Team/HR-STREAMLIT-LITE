import streamlit as st
import pandas as pd
import mysql.connector
import base64
from streamlit_javascript import st_javascript
from user_agents import parse
from utils.navbar import add_navbar
from utils.app import visualizer_main , render_html_table, apply_filters, fetch_attendance_data
import time
from datetime import datetime, timedelta

st.set_page_config(
    page_title="RSS HRMS",
    page_icon="assets\RSS_waifu2x_art_scale.png",
    initial_sidebar_state="collapsed",
    layout="wide"
)

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    with st.spinner('You must log in first!'):
        st.cache_data.clear()
        time.sleep(1)
        st.switch_page("login.py")

add_navbar("Home")

# Correct way to store values in session state
if "Name" not in st.session_state:
    st.session_state["Name"] = "Shaz Shoaib"

if "EMPLOYEE_ID" not in st.session_state:
    st.session_state["EMPLOYEE_ID"] = "91"

# Retrieve values from session state
name = st.session_state["Name"]
employee_id = st.session_state["EMPLOYEE_ID"]

def styled_container(title, content, color="#336CAF", border_color="#336CAF", key=None):
    st.markdown(f"""<div style="background: {color}; padding: 16px 24px; border-radius: 12px; border: 1px solid {border_color}; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; color: white; font-family: 'Segoe UI', sans-serif;" id="{key}"><span style="font-size: 1.2rem; font-weight: 500;">{title}</span><span style="font-size: 1.5rem; font-weight: 700;">{content}</span></div>""", unsafe_allow_html=True)

cleaned = ""
for char in name:
    if (char >= 'a' and char <= 'z') or (char >= 'A' and char <= 'Z') or (char == ' '):
        cleaned += char


st.markdown(
    f"<h3 style='text-align: center; color: white;'>Welcome {cleaned}</h3>",
    unsafe_allow_html=True
)

try:
    # Connect to MySQL database
    conn = mysql.connector.connect(
        host='192.168.18.206',  
        user='root',
        password='mydb1234@XTI#2025',
        database='hrbo',
        port=3306,
        connect_timeout=10
    )
    cursor = conn.cursor()
    
        
    curr_date = datetime.now().date()
    
    def get_pay_periods(reference_date=None):
        if reference_date is None:
            reference_date = datetime.today()

        year = reference_date.year
        month = reference_date.month
        day = reference_date.day

        # Determine if we're currently in the pay period for this month or the previous one
        if day >= 26:
            # Current pay period: 26th of this month to 25th of next month
            current_start = datetime(year, month, 26)
            if month == 12:
                current_end = datetime(year + 1, 1, 25)
            else:
                current_end = datetime(year, month + 1, 25)

            # Previous pay period
            if month == 1:
                prev_start = datetime(year - 1, 12, 26)
                prev_end = datetime(year, 1, 25)
            else:
                prev_start = datetime(year, month - 1, 26)
                prev_end = datetime(year, month, 25)

        else:
            # Current pay period: 26th of last month to 25th of this month
            if month == 1:
                current_start = datetime(year - 1, 12, 26)
            else:
                current_start = datetime(year, month - 1, 26)
            current_end = datetime(year, month, 25)

            # Previous pay period
            if month <= 2:
                prev_start = datetime(year - 1, 11, 26)
                prev_end = datetime(year - 1, 12, 25)
            else:
                prev_start = datetime(year, month - 2, 26)
                prev_end = datetime(year, month - 1, 25)

        return {
            "current": (current_start.date(), current_end.date()),
            "previous": (prev_start.date(), prev_end.date())
        }

    pay_periods = get_pay_periods()
    print("Current Pay Period:", pay_periods["current"])
    print("Previous Pay Period:", pay_periods["previous"])

    
    def get_user_pto():
        try:
            conn = mysql.connector.connect(
                host='192.168.18.206',  
                user='root',
                password='mydb1234@XTI#2025',
                database='hrbo'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT PTO FROM users WHERE id = %s", (st.session_state["EMPLOYEE_ID"],))
            result = cursor.fetchone()
            return result[0] if result else ""
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return ""
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()

    
    
    pto = get_user_pto()
    if pto is None or pto == "":
        pto = "N/A"
        
        
    columns, data, payroll_df = fetch_attendance_data(pay_periods["previous"][0],pay_periods["current"][1], [st.session_state["EMPLOYEE_ID"]])    
    columnscurr, datacurr, payroll_dfcurr = fetch_attendance_data(pay_periods["current"][0],pay_periods["current"][1], [st.session_state["EMPLOYEE_ID"]])
    columnsprev, dataprev, payroll_dfprev = fetch_attendance_data(pay_periods["previous"][0],pay_periods["previous"][1], [st.session_state["EMPLOYEE_ID"]])

    col1, col2, col3 = st.columns(3)
    with col1:
        styled_container(title="Remaining Leaves:", content=pto,key="container2")
        
    with col2:
        if payroll_dfcurr is not None and not payroll_dfcurr.empty:
            value = int(payroll_dfcurr["Absent"].iloc[0])
        else:
            value = "N/A"
        styled_container(title="Absences This Month:", content=value,key="container2")
        
    with col3:
        if payroll_dfcurr is not None and not payroll_dfcurr.empty:
            value = int(payroll_dfcurr["Late"].iloc[0])
        else:
            value = "N/A"
        styled_container(title="Lates This Month:", content=value,key="container2")
        
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div style='padding-left: 20px;'>
                <small><i>Note: PTOs are subtracted at the end of the month.</i></small>
            </div>
            """,
            unsafe_allow_html=True
        )  
         
    with col2:
        if payroll_dfprev is not None and not payroll_dfprev.empty:
            value = int(payroll_dfprev["Absent"].iloc[0])
        else:
            value = "N/A"
        styled_container(title="Absences Last Month:", content=value,key="container2")
        
    with col3:
        if payroll_dfprev is not None and not payroll_dfprev.empty:
            value = int(payroll_dfprev["Late"].iloc[0])
        else:
            value = "N/A"
        styled_container(title="Lates Last Month:", content=value,key="container2")

    st.markdown("---")
    
    if data:
        data = apply_filters(data)
        render_html_table(data)
    else:
        st.info("No data to display")
    # visualizer_main(pay_periods["previous"][0],pay_periods["current"][1],[st.session_state["EMPLOYEE_ID"]])

    st.markdown("---")


    # Fetch Pending Schedule Requests
    query1 = """SELECT override_date as Date, TIME_FORMAT(scheduled_in_time, '%H:%i') as 'Shift Start', TIME_FORMAT(scheduled_out_time, '%H:%i') as 'Shift End', OVERRIDE_STATUS as Status FROM override_schedule WHERE EMPLOYEE_ID = %s AND EMPLOYEE_NAME = %s AND OVERRIDE_STATUS = 'Pending'"""
    cursor.execute(query1, (employee_id, name)) 
    rows1 = cursor.fetchall()
    df1 = pd.DataFrame(rows1, columns=[desc[0] for desc in cursor.description])[::-1]  # Reverse order

    # Fetch Late Requests
    query2 = """SELECT late_date as Date, reason as Reason, late_status as Status FROM late_request WHERE EMPLOYEE_ID = %s AND EMPLOYEE_NAME = %s"""
    cursor.execute(query2, (employee_id, name)) 
    rows2 = cursor.fetchall()
    df2 = pd.DataFrame(rows2, columns=[desc[0] for desc in cursor.description])[::-1]

    # Fetch Approved Schedule Requests
    query3 = """SELECT override_date as Date, TIME_FORMAT(scheduled_in_time, '%H:%i') as 'Shift Start', TIME_FORMAT(scheduled_out_time, '%H:%i') as 'Shift End', OVERRIDE_STATUS as Status FROM override_schedule WHERE EMPLOYEE_ID = %s AND EMPLOYEE_NAME = %s AND OVERRIDE_STATUS = 'Approved'"""
    cursor.execute(query3, (employee_id, name)) 
    rows3 = cursor.fetchall()
    df3 = pd.DataFrame(rows3, columns=[desc[0] for desc in cursor.description])[::-1]

        # col1, col2 = st.columns(2)
        # with col1:
        #     with st.container(border=True):

        #         st.subheader("Schedule Adjustment Request")
        #         st.write("<div style='text-align: center; color: white;'>Pending Requests</div>", unsafe_allow_html=True)
        #         cols = ["Date","Shift Start", "Shift End"]
        #         st.dataframe(df1[cols], hide_index=True, use_container_width=True)
        #         st.write("<div style='text-align: center; color: white;'>Approved Requests</div>", unsafe_allow_html=True)
        #         st.dataframe(df3[cols], hide_index=True, use_container_width=True)
                
        # with col2:
        #     with st.container(border=True):

        #         st.subheader("Late Request")
        #         st.write("<div style='text-align: center; color: white;'>&#8203;</div>", unsafe_allow_html=True)
        #         cols = ["Date","Reason"]
        #         st.dataframe(df2[cols], hide_index=True, use_container_width=True)
        
except mysql.connector.Error as err: 
    st.error(f"Database error: {err}")

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
