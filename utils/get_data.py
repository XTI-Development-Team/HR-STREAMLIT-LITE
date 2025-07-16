import streamlit as st
import mysql.connector
import pandas as pd
import datetime

# values from user account

def get_employee_data(emp_id=0):
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

        # Common select fields including image
        select_fields = """
            EMP_ID, FULL_NAME, FATHER_NAME, DEPARTMENT, DESIGNATION, 
            REPORTING_MANAGER, DATE_OF_JOINING, PROBATION_END_DATE, 
            MOBILE_NUMBER, EMAIL_OFFICIAL, CNIC_NUMBER, DATE_OF_BIRTH, 
            RESIDENTIAL_ADDRESS, EMERGENCY_CONTACT_NUMBER, 
            EMERGENCY_CONTACT_RELATION, BANK_NAME, ACCOUNT_TITLE, 
            ACCOUNT_NUMBER, IBAN_NUMBER, SALARY, EMP_IMAGE
        """

        if emp_id == 0:
            select_sql = f"SELECT {select_fields} FROM employees"
            cursor.execute(select_sql)
        else:
            select_sql = f"SELECT {select_fields} FROM employees WHERE EMP_ID = %s"
            cursor.execute(select_sql, (emp_id,))

        rows = cursor.fetchall()

        # Column names including the image
        columns = [
            "Employee ID", "Full Name", "Father Name", "Department", "Designation",
            "Reporting Manager", "Date of Joining", "Probation End Date", 
            "Mobile Number", "Official Email", "CNIC", "Date of Birth", 
            "Address", "Emergency Contact", "Emergency Relation", "Bank Name", 
            "Account Title", "Account Number", "IBAN", "Salary", "Image"
        ]

        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=columns)
        print(df)

        return df

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return pd.DataFrame()

def get_late_requests(emp_id=0):
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

        if emp_id == 0:
            # Query to fetch data for all employees
            select_sql = """
                SELECT EMPLOYEE_ID, EMPLOYEE_NAME, late_DATE, 
                    late_STATUS, REASON 
                FROM late_request
            """
            cursor.execute(select_sql)
        else:
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
        columns = ["Employee ID", "Employee Name", "late Date", "Status", "Reason"]

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
            

def get_leave_requests(emp_id=0):
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

        if emp_id == 0:
            # Query to fetch data for all employees
            select_sql = """
                SELECT EMPLOYEE_ID, EMPLOYEE_NAME, LEAVE_DATE, 
                    LEAVE_STATUS, REASON 
                FROM leave_request
            """
            cursor.execute(select_sql)
        else:
            # Query to fetch data
            select_sql = """
                SELECT EMPLOYEE_ID, EMPLOYEE_NAME, LEAVE_DATE, 
                    LEAVE_STATUS, REASON
                FROM leave_request WHERE EMPLOYEE_ID = %s
            """
            cursor.execute(select_sql, (emp_id,))

        # Fetch all results
        rows = cursor.fetchall()

        # Define column names
        columns = ["Employee ID", "Employee Name", "Leave Date", "Status", "Reason"]

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
            
def get_missing_requests(emp_id=0):
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

        if emp_id == 0:
            # query to fetch data for all employees
            select_sql = """
                SELECT EMPLOYEE_ID, EMPLOYEE_NAME, MISSING_DATE, TIME_FORMAT(IN_TIME, '%H:%i') AS IN_TIME, TIME_FORMAT(OUT_TIME, '%H:%i') AS OUT_TIME,
                    MISSING_STATUS, COMMENTS 
                FROM missing_request
            """
            cursor.execute(select_sql)
        else:
        # Query to fetch data
            select_sql = """
                SELECT EMPLOYEE_ID, EMPLOYEE_NAME, MISSING_DATE, TIME_FORMAT(IN_TIME, '%H:%i') AS IN_TIME, TIME_FORMAT(OUT_TIME, '%H:%i') AS OUT_TIME,
                    MISSING_STATUS, COMMENTS 
                FROM missing_request WHERE EMPLOYEE_ID = %s
            """
            cursor.execute(select_sql, (emp_id,))

        # Fetch all results
        rows = cursor.fetchall()

        # Define column names
        columns = ["Employee ID", "Employee Name", "Missing Date", "In Time", "Out Time", "Status", "Comments"]

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
            
def get_halfday_requests(emp_id=0):
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

        if emp_id == 0:
            # Query to fetch data for all employees
            select_sql = """
                SELECT EMPLOYEE_ID, EMPLOYEE_NAME, HALFDAY_DATE, 
                    HALFDAY_STATUS, REASON 
                FROM halfday_request
            """
            cursor.execute(select_sql)
        
        else:
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
        columns = ["Employee ID", "Employee Name", "Halfday Date", "Status", "Reason"]

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
            
def get_schedule_requests(emp_id=0):
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

        if emp_id == 0:
            # Query to fetch data for all employees
            select_sql = """
                SELECT EMPLOYEE_ID, EMPLOYEE_NAME, OVERRIDE_DATE, TIME_FORMAT(SCHEDULED_IN_TIME, '%H:%i') AS SCHEDULED_IN_TIME , TIME_FORMAT(SCHEDULED_OUT_TIME, '%H:%i') AS SCHEDULED_OUT_TIME,
                    OVERRIDE_STATUS, DAY_OF_WEEK 
                FROM override_schedule
            """
            cursor.execute(select_sql)
        else:
            # Query to fetch data for emp_id
            select_sql = """
                SELECT EMPLOYEE_ID, EMPLOYEE_NAME, OVERRIDE_DATE, TIME_FORMAT(SCHEDULED_IN_TIME, '%H:%i') AS SCHEDULED_IN_TIME , TIME_FORMAT(SCHEDULED_OUT_TIME, '%H:%i') AS SCHEDULED_OUT_TIME,
                    OVERRIDE_STATUS, DAY_OF_WEEK 
                FROM override_schedule WHERE EMPLOYEE_ID = %s
            """
            cursor.execute(select_sql, (emp_id,))

        # Fetch all results
        rows = cursor.fetchall()

        # Define column names
        columns = ["Employee ID", "Employee Name", "Adjustment Date", "Adjusted In Time", "Adjusted Out Time", "Status", "Day"]

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
            
def get_all_requests(emp_id=0):
    st.title("Late Request")
    st.dataframe(get_late_requests(emp_id))
    st.title("Leave Request")
    st.dataframe(get_leave_requests(emp_id))
    st.title("Missing Request")
    st.dataframe(get_missing_requests(emp_id))
    st.title("Halfday Request")
    st.dataframe(get_halfday_requests(emp_id))
    st.title("Schedule Request")
    st.dataframe(get_schedule_requests(emp_id))

if __name__ == "__main__":
    # Streamlit UI
    employee_id = 91
    employee_name = "Shaz Shoaib"

    st.set_page_config(layout="wide")
    st.write(f"Welcome {employee_name}")

    get_all_requests()