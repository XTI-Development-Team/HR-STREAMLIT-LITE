import streamlit as st
import pandas as pd
import mysql.connector
from datetime import time, timedelta, datetime, date
from utils.navbar import add_navbar

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

# --- MySQL connection setup (adjust this to match your environment) ---
@st.cache_resource
def get_connection():
    return mysql.connector.connect(
            host='192.168.18.206',  
            user='root',
            password='mydb1234@XTI#2025',
            database='hrbo',
    )

conn = get_connection()
cursor = conn.cursor(dictionary=True)


# --- Load data ---
def fetch_schedule(emp_ids):
    format_strings = ','.join(['%s'] * len(emp_ids))
    if len(emp_ids)>0:
        query = f"""
            SELECT * 
            FROM regular_schedule 
            WHERE EMPLOYEE_ID IN ({format_strings}) 
            ORDER BY 
            EMPLOYEE_ID ASC,
            CASE DAY_OF_WEEK
                WHEN 'Monday' THEN 1
                WHEN 'Tuesday' THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4
                WHEN 'Friday' THEN 5
                WHEN 'Saturday' THEN 6
                WHEN 'Sunday' THEN 7
            END ASC
            """
    else:
        query = """
            SELECT * 
            FROM regular_schedule 
            ORDER BY 
            EMPLOYEE_ID ASC,
            CASE DAY_OF_WEEK
                WHEN 'Monday' THEN 1
                WHEN 'Tuesday' THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4
                WHEN 'Friday' THEN 5
                WHEN 'Saturday' THEN 6
                WHEN 'Sunday' THEN 7
            END ASC
        """
    cursor.execute(query, tuple(emp_ids))
    rows = cursor.fetchall()
    df = pd.DataFrame(rows)

    if not df.empty:
        df["SCHEDULED_IN_TIME"] = df["SCHEDULED_IN_TIME"].apply(timedelta_to_str)
        df["SCHEDULED_OUT_TIME"] = df["SCHEDULED_OUT_TIME"].apply(timedelta_to_str)

        condition = (df["SCHEDULED_IN_TIME"] == '00:00:00') & (df["SCHEDULED_OUT_TIME"] == '00:00:00')
        df.loc[condition, ["SCHEDULED_IN_TIME", "SCHEDULED_OUT_TIME"]] = "Holiday"

    return df


def timedelta_to_str(t):
    if isinstance(t, timedelta):
        total_seconds = int(t.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return str(t)



# --- Update schedule ---
def update_schedule(employee_id, day_of_week, in_time, out_time):
    query = """
        UPDATE regular_schedule
        SET SCHEDULED_IN_TIME = %s, SCHEDULED_OUT_TIME = %s
        WHERE EMPLOYEE_ID = %s AND DAY_OF_WEEK = %s
    """
    cursor.execute(query, (in_time, out_time, employee_id, day_of_week))
    conn.commit()

def employee_regular_schedule_editor(ALLOWED_EMP_IDS = []):
# Allowed employees (filter only these)


    st.title("Employee Schedule Management")

    # View full schedule
    st.subheader("📋 Current Schedules")
    df = fetch_schedule(ALLOWED_EMP_IDS)
    
    df["SCHEDULE"] = df["SCHEDULED_IN_TIME"].astype(str) + " - " + df["SCHEDULED_OUT_TIME"].astype(str)

    # Replace "Holiday - Holiday" with "Holiday"
    df["SCHEDULE"] = df["SCHEDULE"].replace("Holiday - Holiday", "Holiday")

    # Pivot the table
    pivot_df = df.pivot_table(
        index=["EMPLOYEE_ID", "EMPLOYEE_NAME"],
        columns="DAY_OF_WEEK",
        values="SCHEDULE",
        aggfunc="first"
    ).reset_index()
    pivot_df.columns.name = None
    pivot_df.columns = [str(col) for col in pivot_df.columns]

    # Optional: reorder columns
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot_df = pivot_df[["EMPLOYEE_ID", "EMPLOYEE_NAME"] + days_order]
    pivot_df = pivot_df.fillna("")

    st.dataframe(pivot_df)

    # Update form
    with st.expander("✏️ Update Schedule",expanded=True):
        
        # Define outside form so changes update immediately
        employee_options = df[['EMPLOYEE_ID', 'EMPLOYEE_NAME']].drop_duplicates()
        selected_name = st.selectbox("Select Employee", employee_options['EMPLOYEE_NAME'])

        # Get EMPLOYEE_ID from name
        selected_row = employee_options[employee_options['EMPLOYEE_NAME'] == selected_name]
        employee_id = int(selected_row['EMPLOYEE_ID'].values[0])

        day_of_week = st.selectbox("Select Day", df['DAY_OF_WEEK'].unique())

        is_holiday = st.checkbox("Set as Holiday")

        # Reactive time input logic
        if is_holiday:
            in_time = time(0, 0)
            out_time = time(0, 0)
            st.markdown("**Holiday Set:** No Scheduled In/Out times")
        else:
            in_time = st.time_input("Scheduled In Time", value=time(9, 0))
            in_time = datetime.combine(date.today(), in_time)  # convert to datetime
            in_time += pd.Timedelta(minutes=15)  # add 15 minutes
            in_time = in_time.time()
            # Compute and show calculated out time live
            in_datetime = pd.to_datetime(in_time.strftime("%H:%M:%S"))
            out_datetime = in_datetime + pd.Timedelta(hours=8,minutes=45)
            in_datetime = in_datetime + pd.Timedelta(minutes=15)  # Add 15 minutes grace period
            out_time = out_datetime.time()

            st.text(f"Out Time: {out_time.strftime('%H:%M:%S')}")

        submitted = st.button("Update Schedule")
        st.write("Note: Scheduled In Time will be adjusted by 15 minutes automatically.")

        if submitted:

            update_schedule(
                employee_id,
                day_of_week,
                in_time.strftime('%H:%M:%S'),
                out_time.strftime('%H:%M:%S')
            )
            st.success(f"{'Holiday set' if is_holiday else 'Schedule updated'} for {selected_name} on {day_of_week}")
            st.rerun()
def get_user_ids_by_department(department):
    # Connect to your MySQL database
    conn = mysql.connector.connect(
            host='192.168.18.206',  
            user='root',
            password='mydb1234@XTI#2025',
            database='hrbo'
    )
    
    cursor = conn.cursor()

    # Parameterized query to prevent SQL injection
    query = "SELECT id FROM users WHERE department = %s and ismanager <> 'Yes' "
    cursor.execute(query, (department,))

    # Fetch and flatten the result into a list
    ids = [row[0] for row in cursor.fetchall()]

    # Clean up
    cursor.close()
    conn.close()

    return ids

def get_all_user_ids():
    # Connect to your MySQL database
    conn = mysql.connector.connect(
            host='192.168.18.206',  
            user='root',
            password='mydb1234@XTI#2025',
            database='hrbo'
    )
    
    cursor = conn.cursor()

    # Parameterized query to prevent SQL injection
    query = "SELECT id FROM users"
    cursor.execute(query)

    # Fetch and flatten the result into a list
    ids = [row[0] for row in cursor.fetchall()]

    # Clean up
    cursor.close()
    conn.close()

    return ids

add_navbar("Change Shifts")

if st.session_state['department'] == "Admin" and st.session_state['ismanager']:
    ids = get_all_user_ids()
else:
    ids = get_user_ids_by_department(st.session_state['department'])

# print("department:", st.session_state['department'])
# print(st.session_state["EMPLOYEE_ID"])

employee_regular_schedule_editor(ids)