import streamlit as st
import mysql.connector
import bcrypt
import time
st.set_page_config(
    page_title="RSS HRMS",
    page_icon="assets\RSS_waifu2x_art_scale.png",
    initial_sidebar_state="collapsed",
    layout="wide"
)

col1, col2, col3 = st.columns([1, 1.5, 1])
with col2:
    with st.container():
        st.image("assets/Robust-Logo.png", use_container_width=True)

st.markdown(
    """
    <style>
#root > div:nth-child(1) > div.withScreencast > div > div > section > div.stMainBlockContainer.block-container > div > div > div > div.stHorizontalBlock > div.stColumn > div > div > div > div > div > div > div > div > div > div.stImage > div{
    background-color: #ffffff   !important;
    border-radius: 5px !important;
}
    </style>
    """,
    unsafe_allow_html=True
)
# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host='192.168.18.206',
        user='root',
        password='mydb1234@XTI#2025',
        database='hrbo',
        port=3306,
        connect_timeout=10
    )

# Verify user credentials and return user data
def check_credentials(username, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return user  # Return full user record
    return None

# Entry point
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    st.switch_page("pages/dashboard.py")

if not st.session_state['logged_in']:
    st.title("🔐 Login Page")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            user = check_credentials(username, password)
            if user:
                st.success(f"✅ Login successfull. Welcome, {username}!")
                st.session_state['Name'] = user['username']
                st.session_state['EMPLOYEE_ID'] = user['id']
                st.session_state['logged_in'] = True
                if user['ismanager'] == "Yes":
                    st.session_state['ismanager'] = True
                else:
                    st.session_state['ismanager'] = False   
                
                st.session_state['department'] = user['department']
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Invalid username or password")