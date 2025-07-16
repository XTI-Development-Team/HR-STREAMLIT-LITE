import streamlit as st
from streamlit_card import card
import pandas as pd
from utils.get_data import get_employee_data
from utils.update_data import edit_employee_profile, update_employee_image
from utils.navbar import add_navbar
import time
import io
import uuid
from PIL import Image
# from utils.navbar import add_navbar, add_border

st.set_page_config(
    page_title="RSS HRMS",
    page_icon="assets\RSS_waifu2x_art_scale.png",
    initial_sidebar_state="collapsed",
    layout="wide"
)
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False


if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    with st.spinner('You must log in first!'):
        st.cache_data.clear()
        time.sleep(1)
        st.switch_page("login.py")
        
add_navbar("Profile")

def get_profile():
    emp_id = st.session_state.get("EMPLOYEE_ID")  
    df = get_employee_data(emp_id)

    if df.empty:
        st.error("❌ No employee data found.")
        return

    emp = df.iloc[0]

    # Extract data
    full_name = emp["Full Name"]
    father_name = emp["Father Name"]
    department = emp["Department"]
    designation = emp["Designation"]
    reporting_manager = emp["Reporting Manager"]
    date_of_joining = emp["Date of Joining"]
    probation_end_date = emp["Probation End Date"]
    mobile_number = emp["Mobile Number"]
    email_official = emp["Official Email"]
    cnic_number = emp["CNIC"]
    dob = emp["Date of Birth"]
    address = emp["Address"]
    emergency_contact = emp["Emergency Contact"]
    emergency_relation = emp["Emergency Relation"]
    bank_name = emp["Bank Name"]
    account_title = emp["Account Title"]
    account_number = emp["Account Number"]
    iban_number = emp["IBAN"]
    salary = emp["Salary"]
    image = emp["Image"]

    # Layout
    col1, col2 = st.columns([1, 3])

    # Profile Card
        
    with col2:


        with st.container(border=True):
            a,b,c = st.columns([1,1,1])
            with a:
                st.markdown("### ✏️ Edit Profile")
            with c:
                if st.button("Edit Mode"):
                    st.session_state.edit_mode = not st.session_state.edit_mode

                y = not st.session_state.edit_mode

            st.markdown("""<style>
                        #root > div:nth-child(1) > div.withScreencast > div > div > section > div.stMainBlockContainer.block-container.st-emotion-cache-t1wise.eht7o1d4 > div > div > div > div:nth-child(7) > div.stColumn.st-emotion-cache-1a3efx5.eu6p4el2 > div > div > div > div > div > div > div.stHorizontalBlock.st-emotion-cache-ocqkz7.eu6p4el0 > div:nth-child(3) > div > div > div > div > div
                        {
                            display: flex !important;
                            justify-content: flex-end !important;  /* Aligns content to the right */
                            }
                            </style>""", unsafe_allow_html=True)

            full_name = st.text_input("Full Name", full_name,disabled=y)
            father_name = st.text_input("Father Name", father_name,disabled=y)
            # department = st.text_input("Department", department)
            # designation = st.text_input("Designation", designation)
            # reporting_manager = st.text_input("Reporting Manager", reporting_manager)
            # date_of_joining = st.date_input("Date of Joining", pd.to_datetime(date_of_joining))
            # probation_end_date = st.date_input("Probation End Date", pd.to_datetime(probation_end_date))
            mobile_number = st.text_input("Mobile Number", mobile_number,disabled=y)
            # email_official = st.text_input("Email (Official)", email_official)
            # cnic_number = st.text_input("CNIC", cnic_number)
            # dob = st.date_input("Date of Birth", pd.to_datetime(dob))
            address = st.text_area("Residential Address", address,disabled=y)
            emergency_contact = st.text_input("Emergency Contact Number", emergency_contact,disabled=y)
            emergency_relation = st.text_input("Emergency Contact Relation", emergency_relation,disabled=y)
            bank_name = st.text_input("Bank Name", bank_name,disabled=y)
            account_title = st.text_input("Account Title", account_title,disabled=y)
            account_number = st.text_input("Account Number", account_number,disabled=y)
            iban_number = st.text_input("IBAN", iban_number,disabled=y)
            # salary = st.number_input("Salary", value=float(salary), step=100.0)

            submitted = st.button("Update Profile",disabled=y)

            if submitted:
                edit_employee_profile(
                    emp_id, full_name, father_name, mobile_number, address,
                    emergency_contact, emergency_relation, bank_name, 
                    account_title, account_number, iban_number
                )
                # You can also include a database update call here
    with col1:
        image_code = Image.open(io.BytesIO(image))

        # Persistent key in session_state
        if "uploader_key" not in st.session_state:
            st.session_state.uploader_key = str(uuid.uuid4())

        with st.container(border=True):
            st.image(image_code, use_container_width=True)
            if st.session_state.edit_mode:
                uploaded_file = st.file_uploader(
                    "Upload Picture",
                    key=st.session_state.uploader_key,
                    type=["jpg", "jpeg", "png"],
                    accept_multiple_files=False
                )
                if uploaded_file is not None:
                    image_bytes = uploaded_file.read()
                    update_employee_image(emp_id, image_bytes)

                    # Refresh uploader by resetting key
                    st.session_state.uploader_key = str(uuid.uuid4())

                    # st.success("✅ Profile picture updated!")
                    time.sleep(0.5)
                    st.rerun()
                    
get_profile()