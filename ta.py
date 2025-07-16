import streamlit as st

st.title("Display Current Page URL")

# Using JavaScript via components to display the full URL
st.markdown("""
    <p><strong>Current URL:</strong></p>
    <input type="text" id="urlBox" style="width: 100%;" readonly />
    <script>
        document.getElementById("urlBox").value = window.location.href;
    </script>
""", unsafe_allow_html=True)
