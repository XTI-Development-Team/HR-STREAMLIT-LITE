import streamlit as st
import pandas as pd
import mysql.connector
import base64
from streamlit_javascript import st_javascript
from user_agents import parse
from utils.navbar import add_navbar
import time
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

add_navbar("Home")


st.write("""
# Help Page
         
Not sure how to use the app? Here are some tips:
- **Login**: Use your credentials to access the app.
- **Navigation**: Use the sidebar to navigate through different sections.
- **Features**: Explore the various features available in the app.
- **Support**: If you encounter any issues, please contact support at devteam@xclusivetradinginc.com
         """)