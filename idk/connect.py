import mysql.connector
import pandas as pd
import datetime


def try_to_connect():
    emp_id = 91
    try:
        conn = mysql.connector.connect(
            host='sage.xclusivetradinginc.cloud',  
            user='sage',
            password='hcu7zYHRuaP9uXhvEAvZsRTtkTn9jjyvnac',
            database='hrbo',
            port=3306,
            connect_timeout=10
        )
        cursor = conn.cursor()

        # Query to fetch data
        select_sql = """
            CREATE TABLE devtest3 (
            employee_id INT PRIMARY KEY AUTO_INCREMENT);
        """
        cursor.execute(select_sql)

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
                        

def conn2(emp_id):
    try:
        conn = mysql.connector.connect(
            host='sage.xclusivetradinginc.cloud',  
            user='sage',
            password='hcu7zYHRuaP9uXhvEAvZsRTtkTn9jjyvnac',
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
            SHOW TABLES;

        """
        cursor.execute(select_sql)

        # Fetch all results
        rows = cursor.fetchall()

        # Define column names
        columns = ["DBs"]

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
            
try_to_connect()

print(conn2(2))