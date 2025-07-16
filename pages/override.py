import streamlit as st
import mysql.connector
import pandas as pd
import datetime
from utils.navbar import add_navbar


# # values from user account
# employee_id = 91
# employee_name = "Shaz Shoaib"


# add_navbar("Requests")
def insert_override_schedule(df):
    try:
        employee_id = st.session_state["EMPLOYEE_ID"]
        employee_name = st.session_state["Name"]
        conn = mysql.connector.connect(
            host='192.168.18.206',  
            user='root',
            password='mydb1234@XTI#2025',
            database='hrbo',
            port=3306,
            connect_timeout=10
        )
        cursor = conn.cursor()
        
        override_date = df["OVERRIDE_DATE"].iloc[0]
        print(override_date)
        
        # Delete rows where EMPLOYEE_ID and OVERRIDE_DATE match, and OVERRIDE_STATUS is "PENDING"
        delete_sql = """
            DELETE FROM override_schedule 
            WHERE EMPLOYEE_ID = %s AND OVERRIDE_DATE = %s AND OVERRIDE_STATUS = 'PENDING'
        """
        cursor.execute(delete_sql, (employee_id, override_date))
    
        # Prepare SQL query for insertion
        insert_sql = """
            INSERT INTO override_schedule 
            (EMPLOYEE_ID, EMPLOYEE_NAME, OVERRIDE_DATE, SCHEDULED_IN_TIME, SCHEDULED_OUT_TIME, OVERRIDE_STATUS, DAY_OF_WEEK)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
    
        # Convert DataFrame to list of tuples
        values = [tuple(row) for row in df.itertuples(index=False, name=None)]
    
        # Execute batch insert
        cursor.executemany(insert_sql, values)
    
        # Commit once for better performance
        conn.commit()
    
        print(f"{cursor.rowcount} rows inserted successfully!")
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_override_schedule(emp_id):
    try:
        conn = mysql.connector.connect(
            host='192.168.18.206',  
            user='root',
            password='mydb1234@XTI#2025',
            database='hrbo',
            port=3306,
            connect_timeout=10
        )
        cursor = conn.cursor()

        # Query to fetch data
        select_sql = """
            SELECT EMPLOYEE_ID, EMPLOYEE_NAME, OVERRIDE_DATE, 
                TIME_FORMAT(SCHEDULED_IN_TIME, '%H:%i') AS SCHEDULED_IN_TIME, 
                TIME_FORMAT(SCHEDULED_OUT_TIME, '%H:%i') AS SCHEDULED_OUT_TIME, 
                OVERRIDE_STATUS, DAY_OF_WEEK 
            FROM override_schedule WHERE EMPLOYEE_ID = %s
        """
        cursor.execute(select_sql, (emp_id,))

        # Fetch all results
        rows = cursor.fetchall()

        # Define column names
        columns = ["Employee ID", "Employee Name", "Date", "Scheduled In Time", "Scheduled Out Time", "Status", "Day of Week"]

        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=columns)
        from datetime import datetime, timedelta
        
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')

        today = datetime.today()

        # Calculate the 26th of the previous month
        if today.month == 1:
            start_date = datetime(today.year - 1, 12, 26)
        else:
            start_date = datetime(today.year, today.month - 1, 26)

        # Filter the DataFrame
        filtered_df = df[(df["Date"] >= start_date) & (df["Date"] <= today)]
        
        return filtered_df[["Employee ID", "Employee Name", "Date", "Scheduled In Time", "Scheduled Out Time", "Status", "Day of Week"]]

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
# Streamlit UI
def override_req():
    employee_name = st.session_state["Name"]
    employee_id = st.session_state["EMPLOYEE_ID"]
    # Streamlit UI
    st.title("Request Shift Adjustment")
    st.write(f"Welcome {employee_name}")


    if employee_id:
        df = get_override_schedule(employee_id)
        if not df.empty:
            st.table(df)
            # df = df.fillna("").astype(str)
            # st.dataframe(df)
        else:
            st.info("No Requests Made")
    else:
        st.error("Please enter a valid employee ID.")

    override_date = st.date_input("Override Date")
    day_type = st.selectbox("Day Type", ["Working Day", "Holiday"])

    if day_type == "Working Day":
        scheduled_in_time = st.time_input("Scheduled In Time")
        scheduled_out_time = (datetime.datetime.combine(datetime.date.today(), scheduled_in_time) + datetime.timedelta(hours=9)).time()
        scheduled_in_time = (datetime.datetime.combine(datetime.date.today(), scheduled_in_time) + datetime.timedelta(minutes=15)).time()
    else:
        scheduled_in_time = datetime.time(0, 0, 0)
        scheduled_out_time = datetime.time(0, 0, 0)

    override_status = "Pending"  # Default status
    day_of_week = override_date.strftime("%A") if override_date else None

    # Create a button to submit and store the values
    if st.button("Request"):
        # Create a DataFrame
        view_df = pd.DataFrame([{
            "Employee ID": employee_id,
            "Name": employee_name,
            "Day": day_of_week,
            "Date": override_date,
            "In Time": scheduled_in_time,
            "Out Time": scheduled_out_time,
            "Status": override_status
        }])
        
        insert_df = pd.DataFrame([{
            "EMPLOYEE_ID": employee_id,
            "EMPLOYEE_NAME": employee_name,
            "OVERRIDE_DATE": override_date,
            "SCHEDULED_IN_TIME": scheduled_in_time,
            "SCHEDULED_OUT_TIME": scheduled_out_time,
            "OVERRIDE_STATUS": override_status,
            "DAY_OF_WEEK": day_of_week
        }])
        
        insert_override_schedule(insert_df)
        
        st.rerun()