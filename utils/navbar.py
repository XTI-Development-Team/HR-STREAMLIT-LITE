import streamlit as st
import pandas as pd
import mysql.connector
import base64
from streamlit_javascript import st_javascript
from user_agents import parse
import time
from streamlit_extras.row import row 
from streamlit_extras.add_vertical_space import add_vertical_space

# Top Navbar with page redirects
# Function to convert image to base64

def add_navbar(default_page):

    
            
    if "curr_page" not in st.session_state or st.session_state.curr_page == None:
        st.session_state.curr_page = default_page
    else:
        st.session_state.selected_page = st.session_state.curr_page
        
    if "nav_clicked" not in st.session_state :
        st.session_state["nav_clicked"] = False
    

    # st.write(st.session_state.curr_page)
    
    def get_base64_image(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    try:
        st.session_state.is_session_pc
    except Exception:
        ua_string = st_javascript("""window.navigator.userAgent;""")
        time.sleep(2)  # Wait for the JavaScript to execute and return the value
        user_agent = parse(str(ua_string))
        st.session_state.is_session_pc = user_agent.is_pc

    # Convert the value into a boolean
    # if st.session_state.is_session_pc:
    
    st.markdown(
        """
        <style>
        #root > div:nth-child(1) > div.withScreencast > div > div > section > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > img {
            background-color : white !important;
        }  
        </style>
        """,
        unsafe_allow_html=True
    )
    def custom_divider(
        color="#cccccc",
        width="100%",
        thickness="1px",
        margin_top="1rem",
        margin_bottom="1rem",
        align="center"  # Options: "left", "center", "right"
    ):
        """
        Renders a customizable horizontal divider in Streamlit.

        Args:
            color (str): Hex color (e.g., "#FF5733")
            width (str): Width (e.g., "300px" or "60%")
            thickness (str): Line thickness (e.g., "2px")
            margin_top (str): Top margin (e.g., "1rem", "10px")
            margin_bottom (str): Bottom margin (e.g., "1rem", "10px")
            align (str): "left", "center", or "right"
        """

        align_map = {
            "left": "flex-start",
            "center": "center",
            "right": "flex-end"
        }
        alignment = align_map.get(align.lower(), "center")

        st.markdown(
            f"""
            
            <div style="
                display: flex;
                align-items: center;
                margin-top: {margin_top};
                margin-bottom: {margin_bottom};
            ">
                <hr style="
                    border: none;
                    border-top: {thickness} solid {color};
                    width: {width};
                    align-self: {alignment};
                    margin: 0;
                " />
            </div>
            """,
            unsafe_allow_html=True
        )

    page = ""

    def set_nav():
        
        if "selected_page" not in st.session_state or st.session_state.selected_page == None:
            print(f"This is the default page {default_page}")
            st.session_state.selected_page = default_page
            
        st.session_state["nav_clicked"] = True
        
        if st.session_state.selected_page == "Home":
            st.session_state["curr_page"] = "Home"
        elif st.session_state.selected_page == "Profile":
            st.session_state["curr_page"] = "Profile"
        elif st.session_state.selected_page == "Requests":
            st.session_state["curr_page"] = "Requests"
        elif st.session_state.selected_page == "HR":
            st.session_state["curr_page"] = "HR"
        elif st.session_state.selected_page == "Help":
            st.session_state["curr_page"] = "Help"
        elif st.session_state.selected_page == "Manager":
            st.session_state["curr_page"] = "Manager"
        elif st.session_state.selected_page == "Add Employees":
            st.session_state["curr_page"] = "Add Employees"
        elif st.session_state.selected_page == "Change Shifts":
            st.session_state["curr_page"] = "Change Shifts"
        elif st.session_state.selected_page == "Logout":
            st.session_state["curr_page"] = "Logout"
        
        print(f"This is the curr page {st.session_state.curr_page}")
        

    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container():
            st.image("assets/Robust-Logo.png", use_container_width=True)
        
    add_vertical_space(1)
    print(st.session_state['ismanager'])
    if st.session_state['ismanager'] and st.session_state['department'] in ['HR', 'Admin']:

        col1, col2, col3 = st.columns([1, 4, 1])
        with col2:
            page = st.segmented_control(
                " ", 
                #["Home", "Profile", "Requests", "HR", "Add Employees", "Change Shifts","Help", "Logout"],
                ["Home", "Profile","Manager", "Help", "Logout"],
                on_change=set_nav,
                key="selected_page"
            )
    elif st.session_state['ismanager']:
        col1, col2, col3 = st.columns([1, 4, 1])
        with col2:
            page = st.segmented_control(
                " ", 
                #["Home", "Profile", "Requests", "Manager", "Change Shifts", "Help", "Logout"],
                ["Home", "Profile", "Manager", "Help", "Logout"],
                on_change=set_nav,
                key="selected_page"
            )        
    else:
        col1, col2, col3 = st.columns([1, 4, 1])
        with col2:
            page = st.segmented_control(
                " ", 
                #["Home", "Profile", "Requests", "Help", "Logout"],
                ["Home", "Profile", "Help", "Logout"],
                on_change=set_nav,
                key="selected_page"
            )

    # CSS to center and scale the segmented control
    st.markdown(
        """
        <style>
        /* Enlarge and center segmented control */
        div:has(> div[role="radiogroup"]) {
            transform: scale(1.6);
            transform-origin: center;
            display: flex;
            justify-content: center;
        }
        
        /* Optional: Reduce top margin if needed */
        section.main > div {
            padding-top: 40px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    custom_divider(color="#afafaf", width="130%", thickness="2px", margin_top="0.5rem", margin_bottom="0rem", align="top")

    if st.session_state["nav_clicked"]:
        st.session_state["nav_clicked"] = False
        if st.session_state.curr_page == "Home":
            st.switch_page("pages/dashboard.py")
        elif st.session_state.curr_page == "Profile":
            st.switch_page("pages/profile.py")
        elif st.session_state.curr_page == "Requests":
            st.switch_page("pages/requests.py")
        elif st.session_state.curr_page == "HR":
            st.switch_page("pages/hr.py")
        elif st.session_state.curr_page == "Help":
            st.switch_page("pages/help.py")
        elif st.session_state.curr_page == "Manager":
            st.switch_page("pages/manager.py")
        elif st.session_state.curr_page == "Add Employees":
            st.switch_page('pages/addemployee.py')
        elif st.session_state.curr_page == "Change Shifts":
            st.switch_page('pages/permanentshift.py')
        elif st.session_state.curr_page == "Logout":
            for key in st.session_state.keys():
                del st.session_state[key]
            st.switch_page("login.py")
            st.rerun()
                    
    # else:
    #     st.markdown(
    #         """
    #         <style>
    #             .block-container { padding-top: 0rem !important; }
    #             #MainMenu, footer, header { visibility: hidden; }
    #         </style>
    #         """,
    #         unsafe_allow_html=True
    #     )
        
    #     # Load and display the logo in the sidebar
    #     img_base64 = get_base64_image("assets/Robust-Logo.png")
        
    #     image_code = f"""
    #         <div style="text-align: center;">
    #             <img src='data:image/png;base64,{img_base64}' width='200' style='margin-bottom: 20px;' />
    #         </div>
    #     """
    #     st.sidebar.markdown(image_code, unsafe_allow_html=True)
        

    #     # Custom CSS to style buttons uniformly
    #     st.markdown(
    #         """
    #         <style>
    #         /* Ensure all buttons have the same width and darkened background */
    #         div.stButton > button {
    #             width: 100% !important;
    #             border-radius: 5px !important;
    #             background-color: #0071AB !important; /* Dark Gray */
    #             color: white !important;
    #             border: 1px solid #666 !important; /* Slightly lighter border */
    #         }

    #         /* Change background color on hover */
    #         div.stButton > button:hover {
    #             background-color: #002031 !important; /* Lighter Gray */
    #             border: 1px solid #888 !important;
    #         }

    #         /* Center buttons in sidebar */
    #         .stSidebar .block-container {
    #             display: flex;
    #             flex-direction: column;
    #             align-items: center;
    #         }
    #         </style>
    #         """,
    #         unsafe_allow_html=True
    #     )

    #     # Sidebar buttons centered
    #     # st.sidebar.title("Navigation")
    #     #nav heading
    #     st.sidebar.markdown(
    #         """
    #         <h3 style="text-align: center;">Navigation</h3>
    #         """,
    #         unsafe_allow_html=True
    #     )
        
        
    #     if st.session_state['ismanager'] and st.session_state['department'] in ['HR', 'Admin']:
    #         if st.sidebar.button("Home"):
    #             st.switch_page("pages/dashboard.py")
    #         elif st.sidebar.button("Profile"):
    #             st.switch_page("pages/profile.py")
    #         # elif st.sidebar.button("Requests"):
    #         #     st.switch_page("pages/requests.py")
    #         # elif st.sidebar.button("HR"):
    #         #     st.switch_page("pages/hr.py")
    #         # elif st.sidebar.button("Add Employees"):
    #         #     st.switch_page("pages/addemployee.py")
    #         elif st.sidebar.button("Help"):
    #             st.switch_page("pages/help.py")
    #         elif st.sidebar.button("Logout"):
    #             for key in st.session_state.keys():
    #                 del st.session_state[key]
    #             st.switch_page("login.py")
    #             st.rerun()
    #     elif st.session_state['ismanager']:
    #         if st.sidebar.button("Home"):
    #             st.switch_page("pages/dashboard.py")
    #         elif st.sidebar.button("Profile"):
    #             st.switch_page("pages/profile.py")
    #         # elif st.sidebar.button("Requests"):
    #         #     st.switch_page("pages/requests.py")
    #         # elif st.sidebar.button("Manager"):
    #         #     st.switch_page("pages/manager.py")
    #         # elif st.sidebar.button("Change Shifts"):
    #         #     st.switch_page("pages/permanentshift.py")
    #         elif st.sidebar.button("Help"):
    #             st.switch_page("pages/help.py")
    #         elif st.sidebar.button("Logout"):
    #             for key in st.session_state.keys():
    #                 del st.session_state[key]
    #             st.switch_page("login.py")
    #             st.rerun()
    #     else:
    #         if st.sidebar.button("Home"):
    #             st.switch_page("pages/dashboard.py")
    #         elif st.sidebar.button("Profile"):
    #             st.switch_page("pages/profile.py")
    #         # elif st.sidebar.button("Requests"):
    #         #     st.switch_page("pages/requests.py")
    #         elif st.sidebar.button("Help"):
    #             st.switch_page("pages/help.py")
    #         elif st.sidebar.button("Logout"):
    #             for key in st.session_state.keys():
    #                 del st.session_state[key]
    #             st.switch_page("login.py")
    #             st.rerun()


# add_navbar()