import streamlit as st
import pandas as pd
import mysql.connector
import base64
from streamlit_javascript import st_javascript
from user_agents import parse
import time
from streamlit_extras.row import row 

# Top Navbar with page redirects
# Function to convert image to base64


def add_border(width="1px"):
    st.markdown("---")
    st.markdown(
        f"""
        <style>
        #root > div:nth-child(1) > div.withScreencast > div > div > section > div.stMainBlockContainer.block-container > div > div > div > div:nth-child(4) > div > div > hr {{
            border-bottom: {width} solid rgba(255, 255, 255, 0.2);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def add_navbar(default_page):

    
            
    if "curr_page" not in st.session_state or st.session_state.curr_page == None:
        st.session_state.curr_page = default_page
    else:
        st.session_state.selected_page = st.session_state.curr_page
        
    if "nav_clicked" not in st.session_state :
        st.session_state["nav_clicked"] = False
    

    def get_base64_image(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    try:
        st.session_state.is_session_pc
    except Exception:
        ua_string = st_javascript("""window.navigator.userAgent;""")
        time.sleep(0.5)  # Wait for the JavaScript to execute and return the value
        user_agent = parse(str(ua_string))
        st.session_state.is_session_pc = user_agent.is_pc

    # Convert the value into a boolean
    if st.session_state.is_session_pc:
        

        
        st.markdown(
            """
            <style>
                /* img center in div*/
                
                #root > div:nth-child(1) > div.withScreencast > div > div > section > div.stMainBlockContainer.block-container.st-emotion-cache-t1wise.eht7o1d4 > div > div > div > div:nth-child(3) > div:nth-child(2) > div > div > div > div > div {
                    
                    display: flex !important;
                    flex-direction: row !important;
                    justify-content: center !important;
                    align-items: center !important;
                }

                /* img size*/
                #root > div:nth-child(1) > div.withScreencast > div > div > section > div.stMainBlockContainer.block-container.st-emotion-cache-t1wise.eht7o1d4 > div > div > div > div:nth-child(3) > div:nth-child(2) > div > div > div > div > div > div > div.stImage.st-emotion-cache-1dvmtd8.evl31sl0 > div > img {
                    width: 100% !important;
                    height: auto !important;
                }
                /* navbar center*/
                #root > div:nth-child(1) > div.withScreencast > div > div > section > div.stMainBlockContainer.block-container > div > div > div > div:nth-child(4) > div.stColumn > div > div > div > div > div {
                    display: flex !important;
                    justify-content: center !important;  /* Centers horizontally */
                    align-items: center !important;    /* Centers vertically */
                    transform: scale(1.5) !important;
                }
            </style>
            """,
            unsafe_allow_html=True
        )
        
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
            
            print(f"This is the curr page {st.session_state.curr_page}")

        a1,b1,c1 = st.columns([1,1,1])
        with b1:
            st.image("assets\Robust-Logo.png", use_container_width=True)

        a,b,c = st.columns([1,4,1])

        with b:
            page = st.segmented_control(
                " ", 
                ["Home", "Profile", "Requests", "HR", "Help", "Logout"],
                on_change=set_nav,
                key="selected_page"
            )

        if st.session_state["nav_clicked"]:
            st.session_state["nav_clicked"] = False
            if st.session_state.curr_page == "Home":
                st.switch_page("pages/dashboard.py")
            elif st.session_state.curr_page == "Profile":
                st.switch_page("pages/profile.py")
            elif st.session_state.curr_page == "Requests":
                st.switch_page("pages/missing.py")
            elif st.session_state.curr_page == "HR":
                st.switch_page("pages/hr.py")
            elif st.session_state.curr_page == "Help":
                st.switch_page("pages/late.py")
        
    else:
        st.markdown(
            """
            <style>
                .block-container { padding-top: 0rem !important; }
                #MainMenu, footer, header { visibility: hidden; }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # Load and display the logo in the sidebar
        img_base64 = get_base64_image("assets/Robust-Logo.png")
        
        image_code = f"""
            <div style="text-align: center;">
                <img src='data:image/png;base64,{img_base64}' width='200' style='margin-bottom: 20px;' />
            </div>
        """
        st.sidebar.markdown(image_code, unsafe_allow_html=True)
        

        # Custom CSS to style buttons uniformly
        st.markdown(
            """
            <style>
            /* Ensure all buttons have the same width and darkened background */
            div.stButton > button {
                width: 100% !important;
                border-radius: 5px !important;
                background-color: #0071AB !important; /* Dark Gray */
                color: white !important;
                border: 1px solid #666 !important; /* Slightly lighter border */
            }

            /* Change background color on hover */
            div.stButton > button:hover {
                background-color: #002031 !important; /* Lighter Gray */
                border: 1px solid #888 !important;
            }

            /* Center buttons in sidebar */
            .stSidebar .block-container {
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Sidebar buttons centered
        # st.sidebar.title("Navigation")
        #nav heading
        st.sidebar.markdown(
            """
            <h3 style="text-align: center;">Navigation</h3>
            """,
            unsafe_allow_html=True
        )



        if st.sidebar.button("Dashboard"):
            st.switch_page("pages/dashboard.py")
        elif st.sidebar.button("Requests"):
            st.switch_page("pages/request.py")
        elif st.sidebar.button("Profile"):
            st.switch_page("pages/profile.py")  

# add_navbar()