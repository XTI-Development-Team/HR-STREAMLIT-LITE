import streamlit as st
import mysql.connector
import pandas as pd
import datetime
from utils.navbar import add_navbar
from datetime import datetime, timedelta


# # values from user account
# employee_id = 91
# employee_name = "Shaz Shoaib"

# add_navbar("Requests")


def insert_halfday_request(df, employee_id):
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
        
        halfday_date = df["HALFDAY_DATE"].iloc[0]
        
        # Delete rows where EMPLOYEE_ID and OVERRIDE_DATE match, and OVERRIDE_STATUS is "PENDING"
        delete_sql = """
            DELETE FROM halfday_request 
            WHERE EMPLOYEE_ID = %s AND HALFDAY_DATE = %s AND HALFDAY_STATUS = 'PENDING'
        """
        cursor.execute(delete_sql, (employee_id, halfday_date))
    
        # Prepare SQL query for insertion
        insert_sql = """
            INSERT INTO halfday_request 
            (EMPLOYEE_ID, EMPLOYEE_NAME, HALFDAY_DATE, HALFDAY_STATUS, REASON)
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

def get_halfday_requests(emp_id):
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
            SELECT EMPLOYEE_ID, EMPLOYEE_NAME, HALFDAY_DATE, 
                HALFDAY_STATUS, REASON 
            FROM halfday_request WHERE EMPLOYEE_ID = %s
        """
        cursor.execute(select_sql, (emp_id,))

        # Fetch all results
        rows = cursor.fetchall()

        # Define column names
        columns = ["Employee ID", "Employee Name", "HalfDay Date", "HalfDay Status", "Reason"]

        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=columns)
        
        df["HalfDay Date"] = pd.to_datetime(df["HalfDay Date"], errors='coerce')

        today = datetime.today()

        # Calculate the 26th of the previous month
        if today.month == 1:
            start_date = datetime(today.year - 1, 12, 26)
        else:
            start_date = datetime(today.year, today.month - 1, 26)

        # Filter the DataFrame
        filtered_df = df[(df["HalfDay Date"] >= start_date) & (df["HalfDay Date"] <= today)]

        return filtered_df[["Employee ID", "Employee Name", "HalfDay Date", "Reason"]]

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
def halfday_req():
    employee_name = st.session_state["Name"]
    employee_id = st.session_state["EMPLOYEE_ID"]
    # Streamlit UI
    st.title("Half Day Request")
    st.write(f"Welcome {employee_name}")

    st.dataframe(get_halfday_requests(employee_id))


    # Input fields

    halfday_date = st.date_input("HalfDay Date")
    halfday_status = "Pending" #("Override Status", ["Approved", "Pending", "Rejected"])
    reason = st.text_area("Reason")
    # Create a button to submit and store the values
    if st.button("Request"):
        
        if not halfday_date or not reason:
            st.error("Please fill all fields")
            return
        
        # Create a DataFrame
        view_df = pd.DataFrame([{
            "Employee ID": employee_id,
            "Name": employee_name,
            "Date": halfday_date,
            "Status": halfday_status,
            "Reason": reason
        }])
        
        insert_df = pd.DataFrame([{
            "EMPLOYEE_ID": employee_id,
            "EMPLOYEE_NAME": employee_name,
            "HALFDAY_DATE": halfday_date,
            "HALFDAY_STATUS": halfday_status,
            "HALFDAY_REASON": reason
        }])
        
        insert_halfday_request(insert_df, employee_id)
        
        st.rerun()