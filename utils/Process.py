import pandas as pd
import mysql.connector
import time
import streamlit as st

def get_adj_schedules(start_date, end_date, emp_ids):
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

        # Build additional filter for EMPLOYEE_ID only if list is not empty
        emp_filter = ""
        if emp_ids:
            emp_ids_str = ",".join(f"'{emp_id}'" for emp_id in emp_ids)
            emp_filter = f"AND aa.EMPLOYEE_ID IN ({emp_ids_str})"

        # Final query
        select_sql = f"""
            SELECT 
                aa.EMPLOYEE_ID,
                aa.EMPLOYEE_NAME,
                aa.CLOCK_DATE,
                aa.IN_TIME,
                aa.OUT_TIME,
                aa.DAY_OF_WEEK,
                COALESCE(os.SCHEDULED_IN_TIME, aa.SCHEDULED_IN_TIME) AS SCHEDULED_IN_TIME,
                COALESCE(os.SCHEDULED_OUT_TIME, aa.SCHEDULED_OUT_TIME) AS SCHEDULED_OUT_TIME,
                aa.OVERRIDE_STATUS,
                hr.HALFDAY_STATUS,
                lr.LATE_STATUS,
                lv.LEAVE_STATUS,
                mr.MISSING_STATUS
            FROM adj_attendance aa
            LEFT JOIN override_schedule os 
                ON aa.EMPLOYEE_ID = os.EMPLOYEE_ID 
                AND aa.CLOCK_DATE = os.OVERRIDE_DATE 
                AND os.OVERRIDE_STATUS = 'Approved'
            LEFT JOIN halfday_request hr 
                ON aa.EMPLOYEE_ID = hr.EMPLOYEE_ID 
                AND aa.CLOCK_DATE = hr.HALFDAY_DATE
            LEFT JOIN late_request lr 
                ON aa.EMPLOYEE_ID = lr.EMPLOYEE_ID 
                AND aa.CLOCK_DATE = lr.LATE_DATE
            LEFT JOIN leave_request lv 
                ON aa.EMPLOYEE_ID = lv.EMPLOYEE_ID 
                AND aa.CLOCK_DATE = lv.LEAVE_DATE
            LEFT JOIN missing_request mr 
                ON aa.EMPLOYEE_ID = mr.EMPLOYEE_ID 
                AND aa.CLOCK_DATE = mr.MISSING_DATE
            WHERE aa.CLOCK_DATE BETWEEN '{start_date}' AND '{end_date}'
            {emp_filter} ORDER BY aa.CLOCK_DATE ASC;
        """
        cursor.execute(select_sql)

        rows = cursor.fetchall()

        columns = [
            "Emp Code", "Employee Name", "Access Date (dd-mm-yy)", 
            "First_In_time (hh:mm)", "Last_Out_time (hh:mm)", "Day of Week", 
            "Scheduled In Time", "Scheduled Out Time", "Override Status", 
            "Half Day Status", "Late Status", "Leave Status", "Missing Status"
        ]

        df = pd.DataFrame(rows, columns=columns)
        return df

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return pd.DataFrame()

def get_schedules():
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
            SELECT * FROM regular_schedule;
        """
        cursor.execute(select_sql)

        # Fetch all results
        rows = cursor.fetchall()

        # Define column names
        columns = ["Emp Code", "Employee Name", "Day of Week", "Scheduled In Time", "Scheduled Out Time"]

        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=columns)

        return df
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

def add_day_of_week(df):
    df['Day of Week'] = pd.to_datetime(df['Access Date (dd-mm-yy)'],format="%d-%m-%Y").dt.day_name()
    return df

def get_merged_df(start_date,end_date, emp_ids):
    
    return get_adj_schedules(start_date,end_date, emp_ids)

def format_status_line(status_label, status_value, override_status):
    """Return formatted title line with optional status and color based on logic."""
    status_color_map = {
        "Approved": "green",
        "Denied": "red",
        "Pending": "#FFFF00",
        "Filled": "green",
    }
    
    override_color_map_for_null_status = {
        "Present": "black",
        "Late": "#FFFF00",
        "Absent": "red",
        "Half Day": "orange",
        "Out Time Missing": "orange",
        "Incomplete Shift": "orange"
    }

    if pd.isna(status_value) or not status_value:
        color = override_color_map_for_null_status.get(override_status, "black")
        return f"<span style='color:{color};'>{status_label}</span>"
    else:
        color = status_color_map.get(status_value, "black")
        return f"<span>{status_label} - <span style='color:{color};'>{status_value}</span></span>"
       
def get_payroll_status(override_status, status_value):
    """Returns normalized payroll status based on override status and optional sub-status."""
    status = None if pd.isna(status_value) or status_value in ["", "N/A"] else status_value

    payroll_matrix = {
        "Present": {
            None: "Present"
        },
        "Late": {
            None: "Late",
            "Approved": "Late",
            "Denied": "Late",
            "Pending": "Late"
        },
        "Absent": {
            None: "Absent",
            "Approved": "Present",
            "Denied": "Absent",
            "Pending": "Absent"
        },
        "Half Day Pending": {
            None: "Present",
            "Approved": "Present",
            "Denied": "Half Day",
            "Pending": "Half Day"
        },
        "Out Time Missing": {
            None: "Present",
            "Approved": "Present",
            "Denied": "Absent",
            "Pending": "Absent"
        },
        "Incomplete Shift": {
            None: "Present",
            "Approved": "Present",
            "Denied": "Absent",
            "Pending": "Absent"
        },
        "Holiday": {
            None: "Holiday"
        }
    }

    return payroll_matrix.get(override_status, {}).get(status, "Absent")
                    
def safe_to_datetime(value, format_str):
    try:
        return pd.to_datetime(value, format=format_str)
    except (ValueError, TypeError):
        return pd.NaT
    
def get_formatted_array(start_date,end_date, emp_ids):
    merged_df = get_merged_df(start_date,end_date, emp_ids)
    
    if merged_df.empty:
        # get_formatted_array(start_date,end_date, emp_ids)
        return None, None, None

    merged_df["Access Date (dd-mm-yy)"] = pd.to_datetime(merged_df["Access Date (dd-mm-yy)"], format="%d-%m-%Y", errors='coerce').dt.strftime("%d-%m-%Y")
    merged_df["First_In_time (hh:mm)"] = merged_df["First_In_time (hh:mm)"].apply(
    lambda x: f"{int(x.components.hours):02}:{int(x.components.minutes):02}:{int(x.components.seconds):02}" if pd.notna(x) else None
)
    merged_df["Last_Out_time (hh:mm)"] = merged_df["Last_Out_time (hh:mm)"].apply(
    lambda x: f"{int(x.components.hours):02}:{int(x.components.minutes):02}:{int(x.components.seconds):02}" if pd.notna(x) else None
)


    # merged_df["Scheduled Out Time"] = pd.to_datetime(merged_df["Scheduled Out Time"], errors='coerce')

    merged_df["Scheduled Out Time"] = merged_df["Scheduled Out Time"].dt.components.apply(
    lambda x: f"{int(x['hours']):02}:{int(x['minutes']):02}", axis=1)
    merged_df["Scheduled In Time"] = merged_df["Scheduled In Time"].dt.components.apply(
    lambda x: f"{int(x['hours']):02}:{int(x['minutes']):02}", axis=1)    
    
    merged_df["Is First In Time Later"] = (merged_df["First_In_time (hh:mm)"] > merged_df["Scheduled Out Time"]) & merged_df["First_In_time (hh:mm)"].notna()

    
    # get dates as a list
    merged_df['Access Date (dd-mm-yy)'] = pd.to_datetime(merged_df['Access Date (dd-mm-yy)'],format='%d-%m-%Y', errors='coerce')
    merged_df['Access Date (dd-mm-yy)'] = merged_df['Access Date (dd-mm-yy)'].dt.strftime('%d-%m-%Y') + ' (' + merged_df['Access Date (dd-mm-yy)'].dt.strftime('%A') + ')'
    date_list = merged_df["Access Date (dd-mm-yy)"].unique().tolist()
    

    emp_code_list = merged_df["Emp Code"].unique().tolist()
    emp_code_list.sort()
    # create a new 2d array with emp code as index and dates as columns
    
    column_header = ["Employee Name"] + date_list
    new_array = []
    new_array.append(column_header)
    
    total_payroll_summary = []
    
    for emp_code in emp_code_list:
        
        payroll_summary = {
            "Present": 0,
            "Late": 0,
            "Absent": 0,
            "Half Day": 0,
            "Holiday":0
        }
        
        
        emp_row = []
        row = merged_df[(merged_df["Emp Code"] == emp_code)]
        if not row.empty:
            emp_row.append(f"{row["Employee Name"].values[0]} [{row["Emp Code"].values[0]}]")
            payroll_summary["Employee Code"] = emp_code
            payroll_summary["Employee Name"] = row["Employee Name"].values[0]
            
        for date in date_list:
            # get the row with emp code and date
            row = merged_df[(merged_df["Emp Code"] == emp_code) & (merged_df["Access Date (dd-mm-yy)"] == date)]
            if not row.empty:
                
                override = row["Override Status"].values[0]

                if override == "Holiday" or str(row['Scheduled In Time'].values[0]) == '00:00' and str(row['Scheduled Out Time'].values[0]) == '00:00':
                    if pd.isna(row["First_In_time (hh:mm)"].values[0]):
                        emp_row.append("<span style='color:white;'>Holiday</span><br>"
                                    "Actual Time: N/A<br>"
                                    f"Scheduled Time: {row['Scheduled In Time'].values[0]} - {row['Scheduled Out Time'].values[0]}")
                        payroll_status = "Holiday"
                        if payroll_status in payroll_summary:
                            payroll_summary[payroll_status] += 1

                    elif str(row['Scheduled In Time'].values[0]) == '00:00' and str(row['Scheduled Out Time'].values[0]) == '00:00':
                        emp_row.append("<span style='color:red;'>Unapproved Extra Shift</span><br>"
                                    f"Actual Time: {row['First_In_time (hh:mm)'].values[0]} - {row['Last_Out_time (hh:mm)'].values[0]}<br>"
                                    f"Scheduled Time: {row['Scheduled In Time'].values[0]} - {row['Scheduled Out Time'].values[0]}")
                        payroll_status = "Present"
                        if payroll_status in payroll_summary:
                            payroll_summary[payroll_status] += 1
                        payroll_status = "Absent"
                        if payroll_status in payroll_summary:
                            payroll_summary[payroll_status] -= 1
                        payroll_status = "Holiday"
                        if payroll_status in payroll_summary:
                            payroll_summary[payroll_status] += 1

                    else:
                        emp_row.append("<span style='color:black;'>Present</span><br>"
                                    f"Actual Time: {row['First_In_time (hh:mm)'].values[0]} - {row['Last_Out_time (hh:mm)'].values[0]}<br>"
                                    f"Scheduled Time: {row['Scheduled In Time'].values[0]} - {row['Scheduled Out Time'].values[0]}")
                        payroll_status = "Present"
                        if payroll_status in payroll_summary:
                            payroll_summary[payroll_status] += 1

                elif override == "Absent":
                    status_val = row["Leave Status"].values[0]
                    title_line = format_status_line("Absent", status_val, override)
                    emp_row.append(f"{title_line}<br>"
                                "Actual Time: N/A<br>"
                                f"Scheduled Time: {row['Scheduled In Time'].values[0]} - {row['Scheduled Out Time'].values[0]}")
                    payroll_status = get_payroll_status(override, status_val)
                    if payroll_status in payroll_summary:
                        payroll_summary[payroll_status] += 1
                        
                elif override == "Late":
                    status_val = row["Late Status"].values[0]
                    
                    # Not dealing with Approving/Denying the late form 
                    if status_val == 'Pending' or status_val == 'Approved' or status_val == 'Denied':
                        status_val = 'Filled'
                    title_line = format_status_line("Late", status_val, override)
                    emp_row.append(f"{title_line}<br>"
                                f"Actual Time: {row['First_In_time (hh:mm)'].values[0]} - {row['Last_Out_time (hh:mm)'].values[0]}<br>"
                                f"Scheduled Time: {row['Scheduled In Time'].values[0]} - {row['Scheduled Out Time'].values[0]}")
                    payroll_status = get_payroll_status(override, status_val)
                    if payroll_status in payroll_summary:
                        payroll_summary[payroll_status] += 1
                        
                elif override == "Present":
                    title_line = format_status_line("Present", None, override)
                    emp_row.append(f"{title_line}<br>"
                                f"Actual Time: {row['First_In_time (hh:mm)'].values[0]} - {row['Last_Out_time (hh:mm)'].values[0]}<br>"
                                f"Scheduled Time: {row['Scheduled In Time'].values[0]} - {row['Scheduled Out Time'].values[0]}")
                    payroll_status = get_payroll_status(override, None)
                    if payroll_status in payroll_summary:
                        payroll_summary[payroll_status] += 1
                        
                elif override == "Half Day Pending":
                    status_val = row["Half Day Status"].values[0]
                    title_line = format_status_line("Half Day Pending", status_val, override)
                    emp_row.append(f"{title_line}<br>"
                                f"Actual Time: {row['First_In_time (hh:mm)'].values[0]} - {row['Last_Out_time (hh:mm)'].values[0]}<br>"
                                f"Scheduled Time: {row['Scheduled In Time'].values[0]} - {row['Scheduled Out Time'].values[0]}")
                    payroll_status = get_payroll_status(override, status_val)
                    if payroll_status in payroll_summary:
                        payroll_summary[payroll_status] += 1
                        
                elif override == "Out Time Missing":
                    status_val = row["Missing Status"].values[0]
                    title_line = format_status_line("Out Time Missing", status_val, override)
                    emp_row.append(f"{title_line}<br>"
                                f"Actual Time: {row['First_In_time (hh:mm)'].values[0]} - N/A<br>"
                                f"Scheduled Time: {row['Scheduled In Time'].values[0]} - {row['Scheduled Out Time'].values[0]}")
                    payroll_status = get_payroll_status(override, status_val)
                    if payroll_status in payroll_summary:
                        payroll_summary[payroll_status] += 1
                        
                elif override == "Incomplete Shift":
                    status_val = row["Missing Status"].values[0]
                    title_line = format_status_line("Incomplete Shift", status_val, override)
                    emp_row.append(f"{title_line}<br>"
                                f"Actual Time: {row['First_In_time (hh:mm)'].values[0]} - {row['Last_Out_time (hh:mm)'].values[0]}<br>"
                                f"Scheduled Time: {row['Scheduled In Time'].values[0]} - {row['Scheduled Out Time'].values[0]}")
                    payroll_status = get_payroll_status(override, status_val)
                    if payroll_status in payroll_summary:
                        payroll_summary[payroll_status] += 1
                        
                else:
                    emp_row.append(f"<span style='color:purple;'>{override}</span><br>"
                                f"Actual Time: {row['First_In_time (hh:mm)'].values[0]} - {row['Last_Out_time (hh:mm)'].values[0]}<br>"
                                f"Scheduled Time: {row['Scheduled In Time'].values[0]} - {row['Scheduled Out Time'].values[0]}")
                    payroll_status = "Absent"  # Fallback for unrecognized status
                    if payroll_status in payroll_summary:
                        payroll_summary[payroll_status] += 1
                        
            else:
                emp_row.append("")
        
        # # EID ADJUSTMENT ------------------------------
        
        # payroll_status = "Absent"

        # if payroll_summary[payroll_status] > 0:

        #     payroll_summary[payroll_status] -= 1
        #     payroll_status = "Holiday"
        #     payroll_summary[payroll_status] += 1        
        # #------------------------------------------------
        
        
        new_array.append(emp_row)
        columns = column_header
        
        total_payroll_summary.append(payroll_summary)
    
    summary_df = pd.DataFrame(total_payroll_summary)
    
    # Ensure Absent is not negative
    summary_df['Absent'] = summary_df['Absent'].clip(lower=0)
    
    summary_df['Payroll Ratio'] = (
        (summary_df['Present'] + summary_df['Late'] + 0.5 * summary_df['Half Day'] - (summary_df['Late'] // 3))
        / (summary_df['Present'] + summary_df['Late']+ summary_df['Half Day']+ summary_df['Absent'])
        ).round(4)  # Optional: round to 4 decimal places

    
    return columns, new_array, summary_df
    
