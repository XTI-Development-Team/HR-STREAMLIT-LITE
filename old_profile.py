import streamlit as st
import pandas as pd
import mysql.connector
import os
from utils.navbar import add_navbar
from streamlit_card import card
from streamlit_extras.add_vertical_space import add_vertical_space 
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

# Default session values
if 'employee_id' not in st.session_state:
    st.session_state.employee_id = 91
if 'employee_name' not in st.session_state:
    st.session_state.employee_name = "Shaz Shoaib"

add_navbar("Profile")

def get_profile():

    col1, col2 = st.columns([1, 3])
    # Profile Card
    with col1:

        card(
            title=st.session_state.employee_name,
            text="Senior Account Executive",
            image="https://images.pexels.com/photos/614810/pexels-photo-614810.jpeg",
            styles={
                "card": {
                    "width": "40vh",
                    "height": "75vh",
                    "border-radius": "2vh",
                    "box-shadow": "0 1vh 4vh rgba(0,0,0,0.3)",
                    "padding": "2vh",
                    "background-color": "#1e1e2f"
                },
                "title": {
                    "font-size": "3vh",
                    "color": "#ffffff",
                    "text-align": "center",
                },
                "text": {
                    "font-size": "2vh",
                    "color": "#cccccc",
                    "text-align": "center",
                },
            }
        )
    with col2:
        add_vertical_space(5)
        # Editable Form
        with st.form("profile_form"):
            st.markdown("### ✏️ Edit Profile")

            name = st.text_input("Full Name", st.session_state.employee_name)
            email = st.text_input("Email", "shaz.shoaib@example.com")
            phone = st.text_input("Phone", "+1 555-123-4567")

            submitted = st.form_submit_button("Update Profile")

            if submitted:
                st.session_state.employee_name = name
                # You can also update this to a database here
                st.success("✅ Profile updated successfully!")

        st.markdown('</div>', unsafe_allow_html=True)

get_profile()
