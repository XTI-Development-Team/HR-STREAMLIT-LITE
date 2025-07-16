import streamlit as st
from utils.navbar import add_navbar
from pages.late import late_req
from pages.halfday import halfday_req
from pages.missing import missing_req
from pages.override import override_req
import time
# from pages.halfday import 
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



add_navbar("Requests")


type = st.selectbox("Requset Type", ["Late", "Leaves or Missing Attendances", "Half Day", "Temporary Schedule Change"])

if type == "Late":
    late_req()
elif type == "Leaves or Missing Attendances":
    missing_req()
elif type == "Half Day":
    halfday_req()
elif type == "Temporary Schedule Change":
    override_req()
else:
    st.error("Please Select Request Type")