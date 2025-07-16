import streamlit as st
import mysql.connector
import pandas as pd
import datetime

# values from user account
def update_employee_image(emp_id, image_bytes):
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

        update_image_sql = """
            UPDATE employees
            SET EMP_IMAGE = %s
            WHERE EMP_ID = %s
        """
        cursor.execute(update_image_sql, (image_bytes, emp_id))
        conn.commit()

        st.success("✅ Profile picture updated successfully!")

    except mysql.connector.Error as err:
        st.error(f"❌ Error updating image: {err}")

    finally:
        cursor.close()
        conn.close()


def edit_employee_profile(emp_id, full_name, father_name, mobile_number, address,
            emergency_contact, emergency_relation, bank_name, 
            account_title, account_number, iban_number):
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

        # Update the employee data in the database
        update_sql = """
            UPDATE employees SET
                FULL_NAME = %s, 
                FATHER_NAME = %s, 
                MOBILE_NUMBER = %s, 
                RESIDENTIAL_ADDRESS = %s,
                EMERGENCY_CONTACT_NUMBER = %s, 
                EMERGENCY_CONTACT_RELATION = %s,
                BANK_NAME = %s, 
                ACCOUNT_TITLE = %s, 
                ACCOUNT_NUMBER = %s, 
                IBAN_NUMBER = %s
            WHERE EMP_ID = %s
        """
        cursor.execute(update_sql, (
            full_name, father_name, mobile_number, address,
            emergency_contact, emergency_relation, bank_name, 
            account_title, account_number, iban_number, emp_id
        ))
        conn.commit()

        st.success("✅ Profile updated successfully!")

    except mysql.connector.Error as err:
        st.error(f"Error updating profile: {err}")


def update_late_requests(data, val):
    conn = None
    cursor = None
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

        # Query to update the late request
        update_sql = """
        UPDATE late_request 
        SET late_STATUS = %s
        WHERE EMPLOYEE_ID = %s AND 
              EMPLOYEE_NAME = %s AND 
              late_DATE = %s AND 
              REASON = %s;
        """
        cursor.execute(update_sql, (val, data['Employee ID'], data['Employee Name'], data['late Date'], data['Reason']))

        # Commit the transaction
        conn.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def update_leave_requests(data, val):
    conn = None
    cursor = None
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

        # Query to update the leave request
        update_sql = """
        UPDATE leave_request
        SET LEAVE_STATUS = %s
        WHERE EMPLOYEE_ID = %s AND 
              EMPLOYEE_NAME = %s AND 
              LEAVE_DATE = %s AND 
              REASON = %s;
        """
        cursor.execute(update_sql, (val, data['Employee ID'], data['Employee Name'], data['Leave Date'], data['Reason']))

        # Commit the transaction
        conn.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def update_missing_requests(data, val):
    conn = None
    cursor = None
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

        # Query to update the missing request
        update_sql = """
        UPDATE missing_request
        SET MISSING_STATUS = %s
        WHERE EMPLOYEE_ID = %s AND 
              EMPLOYEE_NAME = %s AND 
              MISSING_DATE = %s  
        """
        cursor.execute(update_sql, (val, data['Employee ID'], data['Employee Name'], data['Missing Date']))
        # Commit the transaction
        conn.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def update_halfday_requests(data, val):
    conn = None
    cursor = None
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

        # Query to update the halfday request
        update_sql = """
        UPDATE halfday_request
        SET HALFDAY_STATUS = %s
        WHERE EMPLOYEE_ID = %s AND 
              EMPLOYEE_NAME = %s AND 
              HALFDAY_DATE = %s AND 
              REASON = %s;
        """
        cursor.execute(update_sql, (val, data['Employee ID'], data['Employee Name'], data['Halfday Date'], data['Reason']))

        # Commit the transaction
        conn.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def update_individual_attendance_from_missing_request(employee_id, clock_date):
    conn = None
    cursor = None

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

        update_sql = """
        UPDATE hrbo.adj_attendance aa
JOIN (
    SELECT mr1.*
    FROM hrbo.missing_request mr1
    WHERE mr1.EMPLOYEE_ID = %s 
      AND mr1.MISSING_DATE = %s
      AND mr1.MISSING_STATUS = 'Pending'
    ORDER BY mr1.ID DESC
    LIMIT 1
) mr ON aa.EMPLOYEE_ID = mr.EMPLOYEE_ID AND aa.CLOCK_DATE = mr.MISSING_DATE
SET 
    aa.IN_TIME = mr.IN_TIME,
    aa.OUT_TIME = mr.OUT_TIME,
    aa.OVERRIDE_STATUS = 
        CASE 
            WHEN mr.IN_TIME IS NULL AND mr.OUT_TIME IS NULL 
                THEN 'Absent'
            WHEN mr.OUT_TIME IS NULL
                THEN 'Out Time Missing'
            WHEN (
                (TIMESTAMPDIFF(MINUTE, mr.IN_TIME, mr.OUT_TIME) BETWEEN 330 AND 480 AND mr.OUT_TIME > mr.IN_TIME) 
                OR (TIMESTAMPDIFF(MINUTE, mr.IN_TIME, mr.OUT_TIME) + 1440 BETWEEN 330 AND 480 AND mr.OUT_TIME < mr.IN_TIME)
            )
                THEN 'Half Day Pending'
            WHEN (
                (TIMESTAMPDIFF(MINUTE, mr.IN_TIME, mr.OUT_TIME) < 330 AND mr.OUT_TIME > mr.IN_TIME) 
                OR (TIMESTAMPDIFF(MINUTE, mr.IN_TIME, mr.OUT_TIME) + 1440 < 330 AND mr.OUT_TIME < mr.IN_TIME)
            )
                THEN 'Incomplete Shift'
            WHEN (
                (TIME_TO_SEC(TIMEDIFF(mr.OUT_TIME, mr.IN_TIME)) / 60 >= 480 AND mr.OUT_TIME > mr.IN_TIME) 
                OR (TIME_TO_SEC(TIMEDIFF(mr.OUT_TIME, mr.IN_TIME)) / 60 + 1440 >= 480 AND mr.OUT_TIME < mr.IN_TIME)
            )
                THEN 'Present'
            ELSE 'Error'
        END;
                """

        cursor.execute(update_sql, (employee_id, clock_date))
        conn.commit()

        print("Update successful for employee ID %s on %s" % (employee_id, clock_date))
        return True

    except Exception as e:
        print("Error:", str(e))
        return False

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def update_individual_attendance_from_schedule_request(employee_id, clock_date):
    conn = None
    cursor = None

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

        # SQL UPDATE with JOIN based on employee ID and date
        update_sql = """
        UPDATE hrbo.adj_attendance aa
        JOIN hrbo.override_schedule os 
            ON aa.EMPLOYEE_ID = os.EMPLOYEE_ID 
            AND aa.CLOCK_DATE = os.OVERRIDE_DATE
        SET 
            aa.SCHEDULED_IN_TIME = os.SCHEDULED_IN_TIME,
            aa.SCHEDULED_OUT_TIME = os.SCHEDULED_OUT_TIME,
            aa.OVERRIDE_STATUS = 
                CASE 
                    WHEN os.SCHEDULED_IN_TIME = '00:00:00' AND os.SCHEDULED_OUT_TIME = '00:00:00' 
                        THEN 'Holiday'
                    WHEN os.SCHEDULED_IN_TIME IS NULL OR os.SCHEDULED_OUT_TIME IS NULL 
                        THEN 'Scheduled Time Missing'
                    WHEN aa.IN_TIME IS NULL AND aa.OUT_TIME IS NULL 
                        THEN 'Absent'
                    WHEN aa.IN_TIME > os.SCHEDULED_IN_TIME 
                        AND (
                            (TIME_TO_SEC(TIMEDIFF(aa.OUT_TIME, aa.IN_TIME)) / 60 >= 480 AND aa.OUT_TIME > aa.IN_TIME) 
                            OR (TIME_TO_SEC(TIMEDIFF(aa.OUT_TIME, aa.IN_TIME)) / 60 + 1440 >= 480 AND aa.OUT_TIME < aa.IN_TIME)
                        )
                        THEN 'Late'
                    WHEN aa.IN_TIME <= os.SCHEDULED_IN_TIME 
                        AND (
                            (TIME_TO_SEC(TIMEDIFF(aa.OUT_TIME, aa.IN_TIME)) / 60 >= 480 AND aa.OUT_TIME > aa.IN_TIME) 
                            OR (TIME_TO_SEC(TIMEDIFF(aa.OUT_TIME, aa.IN_TIME)) / 60 + 1440 >= 480 AND aa.OUT_TIME < aa.IN_TIME)
                        )
                        THEN 'Present'
                    WHEN aa.OUT_TIME IS NULL
                        THEN 'Out Time Missing'
                    WHEN (
                        (TIMESTAMPDIFF(MINUTE, aa.IN_TIME, aa.OUT_TIME) BETWEEN 330 AND 480 AND aa.OUT_TIME > aa.IN_TIME) 
                        OR (TIMESTAMPDIFF(MINUTE, aa.IN_TIME, aa.OUT_TIME) + 1440 BETWEEN 330 AND 480 AND aa.OUT_TIME < aa.IN_TIME)
                    )
                        THEN 'Half Day Pending'
                    WHEN (
                        (TIMESTAMPDIFF(MINUTE, aa.IN_TIME, aa.OUT_TIME) < 330 AND aa.OUT_TIME > aa.IN_TIME) 
                        OR (TIMESTAMPDIFF(MINUTE, aa.IN_TIME, aa.OUT_TIME) + 1440 < 330 AND aa.OUT_TIME < aa.IN_TIME)
                    )
                        THEN 'Incomplete Shift'
                    ELSE 'Error'
                END
        WHERE 
            aa.EMPLOYEE_ID = %s
            AND aa.CLOCK_DATE = %s;
        """

        # Execute with parameters
        cursor.execute(update_sql, (employee_id, clock_date))
        conn.commit()

        print("Update successful for employee ID %s on %s", employee_id, clock_date)
        return True

    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        return False

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def update_schedule_requests(data, val):
    conn = None
    cursor = None
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

        # Query to update the schedule request
        update_sql = """
        UPDATE override_schedule
        SET OVERRIDE_STATUS = %s
        WHERE EMPLOYEE_ID = %s AND 
              EMPLOYEE_NAME = %s AND 
              OVERRIDE_DATE = %s AND 
              DAY_OF_WEEK = %s;
        """
        cursor.execute(update_sql, (val, data['Employee ID'], data['Employee Name'], data['Adjustment Date'], data['Day']))

        # Commit the transaction
        conn.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def update_all_requests(data, val):
    st.title("Update Late Request")
    update_late_requests(data, val)
    st.title("Update Leave Request")
    update_leave_requests(data, val)
    st.title("Update Missing Request")
    update_missing_requests(data, val)
    st.title("Update Halfday Request")
    update_halfday_requests(data, val)
    st.title("Update Schedule Request")
    update_schedule_requests(data, val)

if __name__ == "__main__":
    # Streamlit UI
    employee_id = 91
    employee_name = "Shaz Shoaib"

    st.write(f"Welcome {employee_name}")

    # Example data to update, this should be passed based on the user's input
    example_data = {
        'Employee ID': employee_id,
        'Employee Name': employee_name,
        'Leave Date': datetime.date(2025, 4, 4),
        'Reason': 'Personal',
        'Late Date': datetime.date(2025, 4, 4),
        'Missing Date': datetime.date(2025, 4, 4),
        'Halfday Date': datetime.date(2025, 4, 4),
        'Override Date': datetime.date(2025, 4, 4),
        'Day of Week': 'Monday',
        'Comments': 'Late due to traffic'
    }
    
    # For example, passing 'Approved' as the update value for all requests
    update_all_requests(example_data, 'Approved')
