import streamlit as st
import mysql.connector
import pandas as pd
import datetime
from utils.navbar import add_navbar
from datetime import datetime, timedelta

# values from user account
# employee_id = 91
# employee_name = "Shaz Shoaib"

# add_navbar("Requests")

def insert_late_request(df,employee_id):
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
        
        late_date = df["late_DATE"].iloc[0]
        
        # Delete rows where EMPLOYEE_ID and OVERRIDE_DATE match, and OVERRIDE_STATUS is "PENDING"
        delete_sql = """
            DELETE FROM late_request 
            WHERE EMPLOYEE_ID = %s AND late_DATE = %s AND late_STATUS = 'PENDING'
        """
        cursor.execute(delete_sql, (employee_id, late_date))
    
        # Prepare SQL query for insertion
        insert_sql = """
            INSERT INTO late_request 
            (EMPLOYEE_ID, EMPLOYEE_NAME, late_DATE, late_STATUS, REASON)
            VALUES (%s, %s, %s, %s, %s)
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


def get_lates(emp_id):
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
            SELECT a.EMPLOYEE_ID, a.EMPLOYEE_NAME, a.CLOCK_DATE, a.OVERRIDE_STATUS 
            FROM adj_attendance a
            WHERE a.OVERRIDE_STATUS = 'Late' 
            AND a.EMPLOYEE_ID = %s
            AND NOT EXISTS (
                SELECT 1 
                FROM late_request lr 
                WHERE lr.EMPLOYEE_ID = a.EMPLOYEE_ID 
                AND lr.LATE_DATE = a.CLOCK_DATE
            )
            ORDER BY a.CLOCK_DATE DESC;
        """
        cursor.execute(select_sql, (emp_id,))

        # Fetch all results
        rows = cursor.fetchall()
        

        # Define column names
        columns = ["Employee ID", "Employee Name", "late Date", "Status"]

        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=columns)
        df["late Date"] = pd.to_datetime(df["late Date"], errors='coerce')

        today = datetime.today()

        # Calculate the 26th of the previous month
        if today.month == 1:
            start_date = datetime(today.year - 1, 12, 26)
        else:
            start_date = datetime(today.year, today.month - 1, 26)

        # Filter the DataFrame
        filtered_df = df[(df["late Date"] >= start_date) & (df["late Date"] <= today)]
        
        return filtered_df[["Employee ID", "Employee Name", "late Date"]]

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
            
def get_late_requests(emp_id):
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
            SELECT EMPLOYEE_ID, EMPLOYEE_NAME, late_DATE, 
                late_STATUS, REASON 
            FROM late_request WHERE EMPLOYEE_ID = %s
        """
        cursor.execute(select_sql, (emp_id,))

        # Fetch all results
        rows = cursor.fetchall()

        # Define column names
        columns = ["Employee ID", "Employee Name", "late Date", "late Status", "Reason"]

        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=columns)

        return df[ ["Employee ID", "Employee Name", "late Date", "Reason"]]

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
# Streamlit UI
# st.set_page_config(layout="wide")
def late_req():
    employee_id = st.session_state.get("EMPLOYEE_ID")
    employee_name = st.session_state.get("Name")

    st.title("Late Request")
    st.write(f"Welcome {employee_name}")
    
    late_df = get_lates(employee_id)
    st.dataframe(get_lates(employee_id))
    st.dataframe(get_late_requests(employee_id))


    # Input fields

    late_date = st.selectbox("late Date", late_df["late Date"].unique())
    late_status = "Pending" #("Override Status", ["Approved", "Pending", "Rejected"])
    reason = st.text_area("Reason")
    # Create a button to submit and store the values
    if st.button("Request"):
        if not late_date or not reason:
            st.error("Please fill all fields")
            return
        
        # Create a DataFrame
        view_df = pd.DataFrame([{
            "Employee ID": employee_id,
            "Name": employee_name,
            "Date": late_date,
            "Status": late_status,
            "Reason": reason
        }])
        
        insert_df = pd.DataFrame([{
            "EMPLOYEE_ID": employee_id,
            "EMPLOYEE_NAME": employee_name,
            "late_DATE": late_date,
            "late_STATUS": late_status,
            "late_REASON": reason
        }])
        
        insert_late_request(insert_df,employee_id)
        
        st.rerun()