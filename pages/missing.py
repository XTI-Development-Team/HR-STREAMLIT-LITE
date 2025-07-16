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


def insert_missing_request(df):
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
        
        emp_id = int(df["EMPLOYEE_ID"].iloc[0])
        missing_date = df["CLOCK_DATE"].iloc[0]
        
        # Delete rows where EMPLOYEE_ID and OVERRIDE_DATE match, and OVERRIDE_STATUS is "PENDING"
        delete_sql = """
            DELETE FROM missing_request
            WHERE EMPLOYEE_ID = %s AND MISSING_DATE = %s AND MISSING_STATUS = 'PENDING';
        """
        cursor.execute(delete_sql, (emp_id, missing_date,))
        
        delete_sql = """
            DELETE FROM leave_request
            WHERE EMPLOYEE_ID = %s AND LEAVE_DATE = %s AND LEAVE_STATUS = 'PENDING';
        """
        cursor.execute(delete_sql, (emp_id, missing_date,))
    
    
        # Prepare SQL query for insertion
        insert_sql = """
            INSERT INTO missing_request 
            (EMPLOYEE_ID, EMPLOYEE_NAME, MISSING_DATE, IN_TIME, OUT_TIME, MISSING_STATUS)
            VALUES (%s, %s, %s, %s, %s, %s)
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

def insert_leave_request(df):
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
        
        emp_id = int(df["EMPLOYEE_ID"].iloc[0])
        leave_date = df["LEAVE_DATE"].iloc[0]
        
        # Delete rows where EMPLOYEE_ID and OVERRIDE_DATE match, and OVERRIDE_STATUS is "PENDING"
        delete_sql = """
            DELETE FROM missing_request
            WHERE EMPLOYEE_ID = %s AND MISSING_DATE = %s AND MISSING_STATUS = 'PENDING';
        """
        cursor.execute(delete_sql, (emp_id, leave_date,))
        
        delete_sql = """
            DELETE FROM leave_request
            WHERE EMPLOYEE_ID = %s AND LEAVE_DATE = %s AND LEAVE_STATUS = 'PENDING';
        """
        cursor.execute(delete_sql, (emp_id, leave_date,))
    
        # Prepare SQL query for insertion
        insert_sql = """
            INSERT INTO leave_request 
            (EMPLOYEE_ID, EMPLOYEE_NAME, LEAVE_DATE, REASON, LEAVE_STATUS)
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

def get_adj_missing_leave_schedule(emp_id):
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
            SELECT EMPLOYEE_ID, EMPLOYEE_NAME, CLOCK_DATE, 
                TIME_FORMAT(IN_TIME, '%H:%i') AS IN_TIME, 
                TIME_FORMAT(OUT_TIME, '%H:%i') AS OUT_TIME, 
                OVERRIDE_STATUS 
            FROM adj_attendance 
            WHERE OUT_TIME IS NULL AND EMPLOYEE_ID = %s AND OVERRIDE_STATUS != 'Holiday'
        """
        
        select_sql = """
            SELECT EMPLOYEE_ID, EMPLOYEE_NAME, CLOCK_DATE, 
            TIME_FORMAT(IN_TIME, '%H:%i') AS IN_TIME, 
            TIME_FORMAT(OUT_TIME, '%H:%i') AS OUT_TIME, 
            OVERRIDE_STATUS 
            FROM adj_attendance 
            WHERE OUT_TIME IS NULL 
            AND EMPLOYEE_ID = %s 
            AND OVERRIDE_STATUS != 'Holiday' 
            AND CLOCK_DATE NOT IN (
            SELECT DISTINCT MISSING_DATE 
            FROM missing_request 
            WHERE EMPLOYEE_ID = %s 
            AND MISSING_STATUS = 'Pending'
    );
        """
        
        select_sql = """SELECT EMPLOYEE_ID, EMPLOYEE_NAME, CLOCK_DATE, 
       TIME_FORMAT(IN_TIME, '%H:%i') AS IN_TIME, 
       TIME_FORMAT(OUT_TIME, '%H:%i') AS OUT_TIME, 
       OVERRIDE_STATUS 
    FROM adj_attendance 
    WHERE OUT_TIME IS NULL 
    AND EMPLOYEE_ID = %s 
    AND OVERRIDE_STATUS != 'Holiday' 
    AND CLOCK_DATE NOT IN (
    SELECT DISTINCT MISSING_DATE 
    FROM missing_request 
    WHERE EMPLOYEE_ID = %s 
    AND (MISSING_STATUS = 'Pending' or MISSING_STATUS = 'Approved')
)
AND NOT EXISTS (
    SELECT 1 
    FROM leave_request 
    WHERE leave_request.EMPLOYEE_ID = adj_attendance.EMPLOYEE_ID 
    AND leave_request.LEAVE_DATE = adj_attendance.CLOCK_DATE 
    AND (leave_request.LEAVE_STATUS = 'Pending' or leave_request.LEAVE_STATUS = 'Approved')
);"""
        cursor.execute(select_sql, (emp_id,emp_id,))

        # Fetch all results
        rows = cursor.fetchall()

        # Define column names
        columns = ["Employee ID", "Employee Name", "Date", "In Time", "Out Time", "Status"]

        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=columns)
        
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')

        today = datetime.today()

        # Calculate the 26th of the previous month
        if today.month == 1:
            start_date = datetime(today.year - 1, 12, 26)
        else:
            start_date = datetime(today.year, today.month - 1, 26)

        # Filter the DataFrame
        filtered_df = df[(df["Date"] >= start_date) & (df["Date"] <= today)]

        return filtered_df

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
def get_missing_requests(emp_id):
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
            SELECT 
            EMPLOYEE_ID, EMPLOYEE_NAME, MISSING_DATE, 
            TIME_FORMAT(IN_TIME, '%H:%i') AS IN_TIME, 
            TIME_FORMAT(OUT_TIME, '%H:%i') AS OUT_TIME, 
            COMMENTS, MISSING_STATUS 
            FROM missing_request 
            WHERE EMPLOYEE_ID = %s AND (MISSING_STATUS = 'Pending' or MISSING_STATUS = 'Approved');
        """
        cursor.execute(select_sql,(emp_id,))

        # Fetch all results
        rows = cursor.fetchall()

        # Define column names
        columns = ["Employee ID", "Employee Name", "Date", "In Time", "Out Time", "Comments", "Status"]

        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=columns)

        return df

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_leave_requests(emp_id):
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
            SELECT 
            EMPLOYEE_ID, EMPLOYEE_NAME, LEAVE_DATE, 
            REASON, LEAVE_STATUS 
            FROM leave_request 
            WHERE EMPLOYEE_ID = %s AND (LEAVE_STATUS = 'Pending' or LEAVE_STATUS = 'Approved');
        """
        cursor.execute(select_sql,(emp_id,))

        # Fetch all results
        rows = cursor.fetchall()

        # Define column names
        columns = ["Employee ID", "Employee Name", "Date", "Reason", "Status"]

        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=columns)

        return df

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def missing_req():
    employee_id = st.session_state["EMPLOYEE_ID"]
    employee_name = st.session_state["Name"]
    adj_df = get_adj_missing_leave_schedule(employee_id)
    missing_df = get_missing_requests(employee_id)
    leave_df = get_leave_requests(employee_id)


    # Streamlit UI
    # st.set_page_config(layout="wide")
    st.title("Resolve Attendance")
    with st.expander("Missing Attendances",expanded=True):
        st.dataframe(adj_df,hide_index=True)
    with st.expander("Pending Requests"):
        col1, col2 = st.columns(2)
        with col1:
            st.write("Missing Attendance Request")
            st.dataframe(missing_df,hide_index=True)
        with col2:
            st.write("Leave Requests")
            st.dataframe(leave_df,hide_index=True)


    # Convert to datetime format
    missing_df["Date"] = pd.to_datetime(missing_df["Date"])
    adj_df["Date"] = pd.to_datetime(adj_df["Date"])
    missing_date_choices = pd.concat([missing_df["Date"], adj_df["Date"]]).drop_duplicates().sort_values()
    missing_date_list = missing_date_choices.dt.strftime("%Y-%m-%d").tolist()

    leave_df["Date"] = pd.to_datetime(leave_df["Date"])
    leave_date_choices = pd.concat([leave_df["Date"], adj_df["Date"]]).drop_duplicates().sort_values()
    leave_date_list = leave_date_choices.dt.strftime("%Y-%m-%d").tolist()

    combined_date_list = sorted(set(missing_date_list + leave_date_list))

    # Input fields

    request_toggle = st.selectbox("Issue",["Leave","Attendance Missing","Remove a Request"])

    if request_toggle == "Leave":
        leave_date = st.selectbox("Select a Date", combined_date_list)
        leave_reason = st.text_area("Leave Reason")
        
        if st.button("Request"):
            if not leave_date or not leave_reason:
                st.error("Please fill all fields")
                return

            
            insert_df = pd.DataFrame([{
                "EMPLOYEE_ID": employee_id,
                "EMPLOYEE_NAME": employee_name,
                "LEAVE_DATE": leave_date,
                "LEAVE_REASON": leave_reason,
                "LEAVE_STATUS": "Pending",
            }])
            
            insert_leave_request(insert_df)
            
            st.rerun()
        
    elif request_toggle == "Attendance Missing":

        missing_date = st.selectbox("Select a Date", combined_date_list)
        in_time = st.time_input("In Time")
        out_time = st.time_input("Out Time")
        override_status = "Pending" #("Override Status", ["Approved", "Pending", "Rejected"])


        # Create a button to submit and store the values
        if st.button("Request"):
            if not missing_date or not in_time or not out_time  or not override_status:
                st.error("Please fill all fields")
                return

            
            # Create a DataFrame
            view_df = pd.DataFrame([{
                "Employee ID": employee_id,
                "Name": employee_name,
                "Date": missing_date,
                "In Time": in_time,
                "Out Time": out_time,
                "Status": override_status
            }])
            
            insert_df = pd.DataFrame([{
                "EMPLOYEE_ID": employee_id,
                "EMPLOYEE_NAME": employee_name,
                "CLOCK_DATE": missing_date,
                "IN_TIME": in_time,
                "OUT_TIME": out_time,
                "OVERRIDE_STATUS": override_status,
            }])
            
            insert_missing_request(insert_df)
                        
            st.rerun()
            
        elif request_toggle == "Remove a Request":
            pass
