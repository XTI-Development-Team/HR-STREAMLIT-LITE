import streamlit as st
import pandas as pd
from utils.get_data import get_missing_requests, get_late_requests, get_leave_requests, get_halfday_requests, get_schedule_requests
from utils.update_data import update_late_requests, update_leave_requests, update_missing_requests, update_halfday_requests, update_schedule_requests
import mysql.connector
import os
from utils.navbar import add_navbar
import time
from datetime import datetime
from utils.app import visualizer_main

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


add_navbar("HR")


st.markdown(
    """
    <h1 style="text-align: center;">Request Approvals</h1>
    """,
    unsafe_allow_html=True
)



if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()



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

pay_periods = get_pay_periods()
print("Current Pay Period:", pay_periods["current"])
print("Previous Pay Period:", pay_periods["previous"])

visualizer_main(pay_periods["previous"][0],pay_periods["current"][1], emp_ids = get_all_user_ids())



data =st.selectbox(
        "Select an option",
        ("Late Request", "Leave Request", "Halfday Request", "Schedule Request", "Missing Request"),
        index=0,
    )

filter1 = st.selectbox(
    "Filter by",
    ("Pending", "Approved", "Denied", "All"),
    index=0,
)

if data == "Missing Request":
    st.markdown(
        """
        <style>
        #root > div:nth-child(n) > div.withScreencast > div > div > section > 
        div.stMainBlockContainer.block-container > 
        div > div > div > div:nth-child(n) > div:nth-child(8) > div > div > div > div > div > button {
            background-color: green !important;
            color: white !important;
            width: 8rem;
            height: 2rem;
            background-color: #0071AB;
            color: white;
            border: none;
            border-radius: 0.25rem;
            font-size: 1rem;
            cursor: pointer;
            text-align: center;
        }
        #root > div:nth-child(n) > div.withScreencast > div > div > section > 
        div.stMainBlockContainer.block-container > 
        div > div > div > div:nth-child(n) > div:nth-child(9) > div > div > div > div > div > button {
            background-color: red !important;
            color: white !important;
            width: 8rem;
            height: 2rem;
            background-color: #0071AB;
            color: white;
            border: none;
            border-radius: 0.25rem;
            font-size: 1rem;
            cursor: pointer;
            text-align: center;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


    df = get_missing_requests()
    st.write("### Missing Request Table")
elif data == "Late Request":
    st.markdown(
        """
        <style>
        #root > div:nth-child(n) > div.withScreencast > div > div > section > 
        div.stMainBlockContainer.block-container > 
        div > div > div > div:nth-child(n) > div:nth-child(6) > div > div > div > div > div > button {
            background-color: green !important;
            color: white !important;
            width: 8rem;
            height: 2rem;
            background-color: #0071AB;
            color: white;
            border: none;
            border-radius: 0.25rem;
            font-size: 1rem;
            cursor: pointer;
            text-align: center;
        }
        #root > div:nth-child(n) > div.withScreencast > div > div > section > 
        div.stMainBlockContainer.block-container > 
        div > div > div > div:nth-child(n) > div:nth-child(7) > div > div > div > div > div > button {
            background-color: red !important;
            color: white !important;
            width: 8rem;
            height: 2rem;
            background-color: #0071AB;
            color: white;
            border: none;
            border-radius: 0.25rem;
            font-size: 1rem;
            cursor: pointer;
            text-align: center;
        }

        </style>
        """,
        unsafe_allow_html=True
    )
    df = get_late_requests()
    st.write("### Late Request Table")
elif data == "Leave Request":
    st.markdown(
        """
        <style>
        #root > div:nth-child(n) > div.withScreencast > div > div > section > 
        div.stMainBlockContainer.block-container > 
        div > div > div > div:nth-child(n) > div:nth-child(6) > div > div > div > div > div > button {
            background-color: green !important;
            color: white !important;
            width: 8rem;
            height: 2rem;
            background-color: #0071AB;
            color: white;
            border: none;
            border-radius: 0.25rem;
            font-size: 1rem;
            cursor: pointer;
            text-align: center;
        }
        #root > div:nth-child(n) > div.withScreencast > div > div > section > 
        div.stMainBlockContainer.block-container > 
        div > div > div > div:nth-child(n) > div:nth-child(7) > div > div > div > div > div > button {
            background-color: red !important;
            color: white !important;
            width: 8rem;
            height: 2rem;
            background-color: #0071AB;
            color: white;
            border: none;
            border-radius: 0.25rem;
            font-size: 1rem;
            cursor: pointer;
            text-align: center;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    df = get_leave_requests()
    st.write("### Leave Request Table")
elif data == "Halfday Request":
    st.markdown(
        """
        <style>
        #root > div:nth-child(n) > div.withScreencast > div > div > section > 
        div.stMainBlockContainer.block-container > 
        div > div > div > div:nth-child(n) > div:nth-child(6) > div > div > div > div > div > button {
            background-color: green !important;
            color: white !important;
            width: 8rem;
            height: 2rem;
            background-color: #0071AB;
            color: white;
            border: none;
            border-radius: 0.25rem;
            font-size: 1rem;
            cursor: pointer;
            text-align: center;
        }
        #root > div:nth-child(n) > div.withScreencast > div > div > section > 
        div.stMainBlockContainer.block-container > 
        div > div > div > div:nth-child(n) > div:nth-child(7) > div > div > div > div > div > button {
            background-color: red !important;
            color: white !important;
            width: 8rem;
            height: 2rem;
            background-color: #0071AB;
            color: white;
            border: none;
            border-radius: 0.25rem;
            font-size: 1rem;
            cursor: pointer;
            text-align: center;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    df = get_halfday_requests()
    st.write("### Halfday Request Table")
elif data == "Schedule Request":
    st.markdown(
        """
        <style>
        #root > div:nth-child(n) > div.withScreencast > div > div > section > 
        div.stMainBlockContainer.block-container > 
        div > div > div > div:nth-child(n) > div:nth-child(8) > div > div > div > div > div > button {
            background-color: green !important;
            color: white !important;
            width: 8rem;
            height: 2rem;
            background-color: #0071AB;
            color: white;
            border: none;
            border-radius: 0.25rem;
            font-size: 1rem;
            cursor: pointer;
            text-align: center;
        }
        #root > div:nth-child(n) > div.withScreencast > div > div > section > 
        div.stMainBlockContainer.block-container > 
        div > div > div > div:nth-child(n) > div:nth-child(9) > div > div > div > div > div > button {
            background-color: red !important;
            color: white !important;
            width: 8rem;
            height: 2rem;
            background-color: #0071AB;
            color: white;
            border: none;
            border-radius: 0.25rem;
            font-size: 1rem;
            cursor: pointer;
            text-align: center;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    df = get_schedule_requests()
    st.write("### Schedule Request Table")
    
# Display DataFrame in Streamlit
if filter1 == "All":
    pass
else:
    df = df[df['Status'] == filter1]
empty_row = pd.DataFrame([[None] * len(df.columns)], columns=df.columns)
df = pd.concat([empty_row, df], ignore_index=True)


# df = df[df['status'] == 'pending']
# Display DataFrame as a table with scrollable columnss


check = True
# Custom CSS to reduce padding and space between rows
st.markdown(
    """
    <style>
    .streamlit-expanderHeader {
        padding: 0;
    }
    .stDataFrame {
    .stMarkdown {
        margin: 0;
        padding: 0;
    }
    .stSelectbox {
        margin: 0;s
        padding: 0;
    }
    </style>
    """, unsafe_allow_html=True
)
# Create action buttons for each row
# Map data types to their respective update functions
update_functions = {
    "Missing Request": update_missing_requests,
    "Late Request": update_late_requests,
    "Leave Request": update_leave_requests,
    "Halfday Request": update_halfday_requests,
    "Schedule Request": update_schedule_requests
}


# Removes rows where all values are NaN
df = df.dropna(how='all')  

# for recent insertions first
df = df.iloc[::-1].reset_index(drop=True)

# add Nan row again to the top
empty_row = pd.DataFrame([[""] * len(df.columns)], columns=df.columns)
df = pd.concat([empty_row, df], ignore_index=True)

# Display rows
for index, row in df.iterrows():
    cols = st.columns(len(df.columns) + 2)  # Extra columns for buttons

    # Display header only once
    for i, col_name in enumerate(df.columns):
        if check:
            cols[i].markdown(f"<div style='text-align: center;'><b>{col_name}</b></div>", unsafe_allow_html=True)
        else:
            cols[i].markdown(f"<div style='text-align: center; line-height: 4vh'>{str(row[col_name])}</div>", unsafe_allow_html=True)

    # Show buttons only if status is not Approved or Denied
    if not check and row['Status'] not in ['Approved', 'Denied']:
        approve_button = cols[-2].button("Approve", key=f"approve_{index}")
        deny_button = cols[-1].button("Deny", key=f"deny_{index}")

        if approve_button or deny_button:
            new_status = "Approved" if approve_button else "Denied"
            if data in update_functions:
                update_functions[data](row, new_status)
                st.rerun()

    # Add a horizontal separator
    st.markdown("<hr style='margin: 0; padding: 0;'>", unsafe_allow_html=True)
    
    check = False  # Turn off header after first row

    
    