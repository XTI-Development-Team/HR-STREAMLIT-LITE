import streamlit as st
import pandas as pd
from utils.get_data import get_missing_requests, get_late_requests, get_leave_requests, get_halfday_requests, get_schedule_requests
from utils.update_data import update_late_requests, update_leave_requests, update_missing_requests, update_halfday_requests, update_schedule_requests, update_individual_attendance_from_missing_request, update_individual_attendance_from_schedule_request
import mysql.connector
import os
from utils.navbar import add_navbar
from utils.app import visualizer_main, fetch_attendance_data, render_html_table
import time
import mysql.connector
from datetime import datetime

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


add_navbar("Manager")

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

st.markdown(
    """
    <h1 style="text-align: center;">Request Approvals</h1>
    """,
    unsafe_allow_html=True
)

if st.session_state['ismanager'] and st.session_state['department'] in ['HR', 'Admin']:
    ids = get_all_user_ids()
else:
    ids = get_user_ids_by_department(st.session_state['department'])

def get_pay_periods(reference_date=None):
    if reference_date is None:
        reference_date = datetime.today()

    year = reference_date.year
    month = reference_date.month
    day = reference_date.day

    # Determine if we're currently in the pay period for this month or the previous one
    if day >= 26:
        # Current pay period: 26th of this month to 25th of next month
        current_start = datetime(year, month, 26)
        if month == 12:
            current_end = datetime(year + 1, 1, 25)
        else:
            current_end = datetime(year, month + 1, 25)

        # Previous pay period
        if month == 1:
            prev_start = datetime(year - 1, 12, 26)
            prev_end = datetime(year, 1, 25)
        else:
            prev_start = datetime(year, month - 1, 26)
            prev_end = datetime(year, month, 25)

    else:
        # Current pay period: 26th of last month to 25th of this month
        if month == 1:
            current_start = datetime(year - 1, 12, 26)
        else:
            current_start = datetime(year, month - 1, 26)
        current_end = datetime(year, month, 25)

        # Previous pay period
        if month <= 2:
            prev_start = datetime(year - 1, 11, 26)
            prev_end = datetime(year - 1, 12, 25)
        else:
            prev_start = datetime(year, month - 2, 26)
            prev_end = datetime(year, month - 1, 25)

    return {
        "current": (current_start.date(), current_end.date()),
        "previous": (prev_start.date(), prev_end.date())
    }

pay_periods = get_pay_periods()
print("Current Pay Period:", pay_periods["current"])
print("Previous Pay Period:", pay_periods["previous"])
try:
    visualizer_main(pay_periods["previous"][0],pay_periods["current"][1],ids,ratio=False)
    columns, data, payroll_df = fetch_attendance_data(pay_periods["previous"][0],pay_periods["current"][1], ids)
except Exception as e:
    st.error(f"Select Complete Date Range")
    columns, data, payroll_df = [], [], pd.DataFrame()


# data =st.selectbox(
#         "Select an option",
#         ("Late Request", "Leave Request", "Halfday Request", "Schedule Request", "Missing Request"),
#         index=0,
#     )

# if data == 'Late Request':
#     filter1 = 'All'
# else:
#     filter1 = st.selectbox(
#         "Filter by",
#         ("Pending", "Approved", "Denied", "All"),
#         index=0,
#     )


# if data == "Missing Request":
#     st.markdown(
#         """
#         <style>
#         #root > div:nth-child(n) > div.withScreencast > div > div > section > 
#         div.stMainBlockContainer.block-container > 
#         div > div > div > div:nth-child(n) > div:nth-child(8) > div > div > div > div > div > button {
#             background-color: green !important;
#             color: white !important;
#             width: 8rem;
#             height: 2rem;
#             background-color: #0071AB;
#             color: white;
#             border: none;
#             border-radius: 0.25rem;
#             font-size: 1rem;
#             cursor: pointer;
#             text-align: center;
#         }
#         #root > div:nth-child(n) > div.withScreencast > div > div > section > 
#         div.stMainBlockContainer.block-container > 
#         div > div > div > div:nth-child(n) > div:nth-child(9) > div > div > div > div > div > button {
#             background-color: red !important;
#             color: white !important;
#             width: 8rem;
#             height: 2rem;
#             background-color: #0071AB;
#             color: white;
#             border: none;
#             border-radius: 0.25rem;
#             font-size: 1rem;
#             cursor: pointer;
#             text-align: center;
#         }

#         </style>
#         """,
#         unsafe_allow_html=True
#     )

#     all_dfs = [get_missing_requests(id) for id in ids]
#     df = pd.concat(all_dfs, ignore_index=True)
    
#     st.write("### Missing Request Table")
# elif data == "Late Request":
#     st.markdown(
#         """
#         <style>
#         #root > div:nth-child(n) > div.withScreencast > div > div > section > 
#         div.stMainBlockContainer.block-container > 
#         div > div > div > div:nth-child(n) > div:nth-child(6) > div > div > div > div > div > button {
#             background-color: green !important;
#             color: white !important;
#             width: 8rem;
#             height: 2rem;
#             background-color: #0071AB;
#             color: white;
#             border: none;
#             border-radius: 0.25rem;
#             font-size: 1rem;
#             cursor: pointer;
#             text-align: center;
#         }
#         #root > div:nth-child(n) > div.withScreencast > div > div > section > 
#         div.stMainBlockContainer.block-container > 
#         div > div > div > div:nth-child(n) > div:nth-child(7) > div > div > div > div > div > button {
#             background-color: red !important;
#             color: white !important;
#             width: 8rem;
#             height: 2rem;
#             background-color: #0071AB;
#             color: white;
#             border: none;
#             border-radius: 0.25rem;
#             font-size: 1rem;
#             cursor: pointer;
#             text-align: center;
#         }

#         </style>
#         """,
#         unsafe_allow_html=True
#     )
#     all_dfs = [get_late_requests(id) for id in ids]
#     df = pd.concat(all_dfs, ignore_index=True)
#     st.write("### Late Request Table")
# elif data == "Leave Request":
#     st.markdown(
#         """
#         <style>
#         #root > div:nth-child(n) > div.withScreencast > div > div > section > 
#         div.stMainBlockContainer.block-container > 
#         div > div > div > div:nth-child(n) > div:nth-child(6) > div > div > div > div > div > button {
#             background-color: green !important;
#             color: white !important;
#             width: 8rem;
#             height: 2rem;
#             background-color: #0071AB;
#             color: white;
#             border: none;
#             border-radius: 0.25rem;
#             font-size: 1rem;
#             cursor: pointer;
#             text-align: center;
#         }
#         #root > div:nth-child(n) > div.withScreencast > div > div > section > 
#         div.stMainBlockContainer.block-container > 
#         div > div > div > div:nth-child(n) > div:nth-child(7) > div > div > div > div > div > button {
#             background-color: red !important;
#             color: white !important;
#             width: 8rem;
#             height: 2rem;
#             background-color: #0071AB;
#             color: white;
#             border: none;
#             border-radius: 0.25rem;
#             font-size: 1rem;
#             cursor: pointer;
#             text-align: center;
#         }

#         </style>
#         """,
#         unsafe_allow_html=True
#     )
#     all_dfs = [get_leave_requests(id) for id in ids]
#     df = pd.concat(all_dfs, ignore_index=True)

#     st.write("### Leave Request Table")
# elif data == "Halfday Request":
#     st.markdown(
#         """
#         <style>
#         #root > div:nth-child(n) > div.withScreencast > div > div > section > 
#         div.stMainBlockContainer.block-container > 
#         div > div > div > div:nth-child(n) > div:nth-child(6) > div > div > div > div > div > button {
#             background-color: green !important;
#             color: white !important;
#             width: 8rem;
#             height: 2rem;
#             background-color: #0071AB;
#             color: white;
#             border: none;
#             border-radius: 0.25rem;
#             font-size: 1rem;
#             cursor: pointer;
#             text-align: center;
#         }
#         #root > div:nth-child(n) > div.withScreencast > div > div > section > 
#         div.stMainBlockContainer.block-container > 
#         div > div > div > div:nth-child(n) > div:nth-child(7) > div > div > div > div > div > button {
#             background-color: red !important;
#             color: white !important;
#             width: 8rem;
#             height: 2rem;
#             background-color: #0071AB;
#             color: white;
#             border: none;
#             border-radius: 0.25rem;
#             font-size: 1rem;
#             cursor: pointer;
#             text-align: center;
#         }

#         </style>
#         """,
#         unsafe_allow_html=True
#     )
#     all_dfs = [get_halfday_requests(id) for id in ids]
#     df = pd.concat(all_dfs, ignore_index=True)

#     st.write("### Halfday Request Table")
# elif data == "Schedule Request":
#     st.markdown(
#         """
#         <style>
#         #root > div:nth-child(n) > div.withScreencast > div > div > section > 
#         div.stMainBlockContainer.block-container > 
#         div > div > div > div:nth-child(n) > div:nth-child(8) > div > div > div > div > div > button {
#             background-color: green !important;
#             color: white !important;
#             width: 8rem;
#             height: 2rem;
#             background-color: #0071AB;
#             color: white;
#             border: none;
#             border-radius: 0.25rem;
#             font-size: 1rem;
#             cursor: pointer;
#             text-align: center;
#         }
#         #root > div:nth-child(n) > div.withScreencast > div > div > section > 
#         div.stMainBlockContainer.block-container > 
#         div > div > div > div:nth-child(n) > div:nth-child(9) > div > div > div > div > div > button {
#             background-color: red !important;
#             color: white !important;
#             width: 8rem;
#             height: 2rem;
#             background-color: #0071AB;
#             color: white;
#             border: none;
#             border-radius: 0.25rem;
#             font-size: 1rem;
#             cursor: pointer;
#             text-align: center;
#         }

#         </style>
#         """,
#         unsafe_allow_html=True
#     )
#     all_dfs = [get_schedule_requests(id) for id in ids]
#     df = pd.concat(all_dfs, ignore_index=True)

#     st.write("### Schedule Request Table")
    
# # Display DataFrame in Streamlit
# if filter1 == "All":
#     pass
# else:
#     df = df[df['Status'] == filter1]

# empty_row = pd.DataFrame([[None] * len(df.columns)], columns=df.columns)
# df = pd.concat([empty_row, df], ignore_index=True)


# # df = df[df['status'] == 'pending']
# # Display DataFrame as a table with scrollable columnss


# check = True
# # Custom CSS to reduce padding and space between rows
# st.markdown(
#     """
#     <style>
#     .streamlit-expanderHeader {
#         padding: 0;
#     }
#     .stDataFrame {
#     .stMarkdown {
#         margin: 0;
#         padding: 0;
#     }
#     .stSelectbox {
#         margin: 0;s
#         padding: 0;
#     }
#     </style>
#     """, unsafe_allow_html=True
# )

# # Removes rows where all values are NaN
# df = df.dropna(how='all')  

# # for recent insertions first
# df = df.iloc[::-1].reset_index(drop=True)

# # add Nan row again to the top
# empty_row = pd.DataFrame([[""] * len(df.columns)], columns=df.columns)
# df = pd.concat([empty_row, df], ignore_index=True)


# for index, row in df.iterrows():
#     cols = st.columns(len(df.columns) + 2)  # Extra column for button

#     # Display column names in bold and add lines
#     for i, col_name in enumerate(df.columns):
#         if check:
#             cols[i].markdown(f"<div style='text-align: center;'><b>{col_name}</b></div>", unsafe_allow_html=True)
#         else:
#             cols[i].markdown(f"<div style='text-align: center; line-height: 4vh'>{str(row[col_name])}</div>", unsafe_allow_html=True)

#     # Show buttons only if status is not Approved or Denied
#     if (not check and row['Status'] not in ['Approved', 'Denied']) and not data == 'Late Request':
#         approve_button = cols[-2].button("Approve", key=f"approve_{index}")
#         if approve_button:
#             if data == "Missing Request":
#                 update_individual_attendance_from_missing_request(row['Employee ID'], row['Missing Date'])
#                 update_missing_requests(row, "Approved")
#             elif data == "Late Request":
#                 update_late_requests(row, "Approved")
#             elif data == "Leave Request":
#                 update_leave_requests(row, "Approved")
#             elif data == "Halfday Request":
#                 update_halfday_requests(row, "Approved")
#             elif data == "Schedule Request":
#                 update_schedule_requests(row, "Approved")
#                 update_individual_attendance_from_schedule_request(row['Employee ID'], row['Adjustment Date'])

#             st.cache_resource.clear()
#             st.cache_data.clear()
#             st.rerun()

#         deny_button = cols[-1].button("Deny", key=f"deny_{index}")
#         if deny_button:
#             if data == "Missing Request":
#                 update_missing_requests(row, "Denied")
#             elif data == "Late Request":
#                 update_late_requests(row, "Denied")
#             elif data == "Leave Request":
#                 update_leave_requests(row, "Denied")
#             elif data == "Halfday Request":
#                 update_halfday_requests(row, "Denied")
#             elif data == "Schedule Request":
#                 update_schedule_requests(row, "Denied")

#             st.rerun()

#     # Add horizontal line between rows
#     st.markdown("<hr style='margin: 0; padding: 0;'>", unsafe_allow_html=True)

#     check = False

    
    