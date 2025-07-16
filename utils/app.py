import streamlit as st
import streamlit.components.v1 as components
from utils.Process import get_formatted_array
import streamlit.components.v1 as components
import pandas as pd
from datetime import timedelta
from utils.Process import get_schedules
from datetime import datetime
import streamlit.components.v1 as components
import mysql.connector
import pdfkit


def render_html_table(data, column_widths=None):
    rows = len(data)
    val = (rows-1)*83+66    
    if val>=780:
        val=780
    """
    Renders an HTML table in Streamlit with scrollbars and sticky first row/column.
    Borders are white, and sticky cells remain bordered correctly.
    Font is Calibri.
    """
    html_table = """
    <style>
    .custom-table-wrapper {
        overflow: auto;
        max-width: 100%;
        max-height: 750px;
    }
    .custom-table {
        border-collapse: separate;
        border-spacing: 0;
        width: max-content;
        font-family: Calibri, sans-serif;
    }
    .custom-table th, .custom-table td {
        padding: 8px;
        border: 1px solid white;
        white-space: nowrap;
    }
    .custom-table th {
        background-color: #42A0D0;
        position: sticky;
        top: 0;
        z-index: 2;
    }
    .custom-table td:first-child {
        background-color: #42A0D0;
        position: sticky;
        left: 0;
        z-index: 1;
    }
    .custom-table th:first-child {
        left: 0;
        z-index: 3;
    }
    .custom-table td {
        background-color: #94D3F3;
    }
    </style>
    <div class="custom-table-wrapper">
    <table class="custom-table">
    """

    # Table headers
    html_table += "<thead><tr>"
    headers = data[0]
    for i, header in enumerate(headers):
        width = f"width: {column_widths[i]};" if column_widths and i < len(column_widths) else ""
        html_table += f"<th style='{width}'>{header}</th>"
    html_table += "</tr></thead>"

    # Table body
    html_table += "<tbody>"
    for row in data[1:]:
        html_table += "<tr>"
        for i, cell in enumerate(row):
            width = f"width: {column_widths[i]};" if column_widths and i < len(column_widths) else ""
            html_table += f"<td style='{width}'>{cell}</td>"
        html_table += "</tr>"
    html_table += "</tbody>"

    html_table += "</table></div>"

    components.html(html_table, height=val, scrolling=True)

    # with open("temp_table.html", "w", encoding="utf-8") as f:
    #     f.write(html_table)

    
def get_employees_by_ids(emp_list):
    conn = None
    cursor = None
    try:
        # Ensure emp_list is not empty
        if not emp_list:
            return pd.DataFrame(columns=['FULL_NAME', 'EMP_ID'])

        # Convert list of EMP_IDs into a comma-separated string
        formatted_ids = ','.join(['%s'] * len(emp_list))

        conn = mysql.connector.connect(
            host='192.168.18.206',
            user='root',
            password='mydb1234@XTI#2025',
            database='hrbo',
            port=3306,
            connect_timeout=10
        )
        cursor = conn.cursor()

        query = f"""
        SELECT FULL_NAME, EMP_ID 
        FROM hrbo.employees 
        WHERE EMP_ID IN ({formatted_ids})
        """

        cursor.execute(query, emp_list)
        rows = cursor.fetchall()

        # Get column names from cursor
        col_names = [desc[0] for desc in cursor.description]
        return pd.DataFrame(rows, columns=col_names)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return pd.DataFrame()  # Return empty DataFrame on error

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def apply_filters(data):

    # 1. Extract employee names
    employee_names = [row[0] for row in data[1:]]

    # 2. Parse dates from header (first 10 chars only)
    date_headers = data[0][1:]
    date_formats = [datetime.strptime(d[:10], "%d-%m-%Y").date() for d in date_headers]

    # 3. Setup min/max dates
    min_date = min(date_formats)
    max_date = max(date_formats)

    # 4. Filters
    col1, col2, col3 = st.columns([5,5,1])

    if st.session_state["curr_page"] == "Home":
        with col1:
            selected_employees = st.multiselect("Select Employees", employee_names, default=employee_names, disabled=True)
    else:
        with col1:
            selected_employees = st.multiselect("Select Employees", employee_names)

    with col2:
        date_range = st.date_input(
            "Select date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    
    with col3:
        st.markdown("")
        st.markdown("")
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.rerun()



    # Check if user selected a range
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        if start_date is None or end_date is None:
            st.warning("Please select a valid date range.")
            st.stop()
    else:
        st.warning("Please select a start and end date.")
        st.stop()
        
    # 5. Filter date indices based on date range
    selected_date_indices = [
        i for i, d in enumerate(date_formats)
        if start_date <= d <= end_date
    ]

    # 6. Build filtered header
    filtered_header = ["Employee Name"] + [data[0][i + 1] for i in selected_date_indices]

    # 7. Filter employee rows
    filtered_rows = []
    for row in data[1:]:
        if len(selected_employees) == 0 or row[0] in selected_employees:
            filtered_row = [row[0]] + [row[i + 1] for i in selected_date_indices]
            filtered_rows.append(filtered_row)

    # 8. Final filtered data
    filtered_data = [filtered_header] + filtered_rows
    
    return filtered_data

@st.cache_data
def fetch_attendance_data(start_date,end_date, emp_ids):
    return get_formatted_array(start_date,end_date, emp_ids)

def visualizer_main(start_date, end_date, emp_ids=[], ratio=True):
    # Convert incoming string dates to datetime objects
    col1, col2, col3 = st.columns([5,5,1])

    # Get employee dataframe from database
    employee_df = get_employees_by_ids(emp_ids)

    # Build mapping between name and ID
    name_to_id = dict(zip(employee_df['FULL_NAME'], employee_df['EMP_ID']))
    id_to_name = dict(zip(employee_df['EMP_ID'], employee_df['FULL_NAME']))

    with col1:
        selected_names = st.multiselect("Select Employees", employee_df['FULL_NAME'].tolist())
    
    with col2:
        date_range = st.date_input(
            "Select date range",
            value=(start_date, end_date),
            min_value=start_date,
            max_value=end_date
        )

    with col3:
        st.markdown("")
        st.markdown("")
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.rerun()
        
        # Check if user selected a range
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        if start_date is None or end_date is None:
            st.warning("Please select a valid date range.")
            st.stop()
    else:
        st.warning("Please select a start and end date.")
        st.stop()

    # Get start and end from date_range
    selected_start = date_range[0]
    selected_end = date_range[1]

    # If nothing is selected, use all EMP_IDs
    if not selected_names:
        selected_ids = emp_ids
    else:
        selected_ids = [name_to_id[name] for name in selected_names]

    # Convert selected dates back to string format
    start_str = selected_start.strftime("%Y-%m-%d")
    end_str = selected_end.strftime("%Y-%m-%d")

    with st.expander("Attendance Data", expanded=True):
        columns, data, payroll_df = fetch_attendance_data(start_str, end_str, selected_ids)
        # Optional: you can map EMP_IDs back to names if needed in payroll_df
        if 'EMP_ID' in payroll_df.columns:
            payroll_df['FULL_NAME'] = payroll_df['EMP_ID'].map(id_to_name)
        # data = apply_filters(data)

        render_html_table(data)
    if ratio:
        new_order = ['Employee Code', 'Employee Name','Present', 'Late', 'Absent', 'Half Day', 'Holiday','Payroll Ratio']
    else:
        new_order = ['Employee Code', 'Employee Name','Present', 'Late', 'Absent', 'Half Day', 'Holiday']
    payroll_df = payroll_df[new_order]

    with st.expander("Payroll Calculation" ,expanded=False):
        st.dataframe(payroll_df,hide_index=True)

# visualizer_main('2025-04-25','2025-05-25')
