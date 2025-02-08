import streamlit as st

# Configure the page
st.set_page_config(
    page_title="Home",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .stApp {
        background-color: #FFFDD0;  /* Light cream color */
        color: black;
    }
    .stButton>button {
        background-color: white;
        color: black;
        border: 2px solid black;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: block;
        font-size: 3rem !important;
        font-family: "Source Sans Pro", sans-serif;
        font-weight: 900 !important;
        -webkit-font-weight: 900 !important;
        -moz-font-weight: 900 !important;
        text-rendering: geometricPrecision;
        -webkit-font-smoothing: antialiased;
        margin: 0 auto;
        cursor: pointer;
        border-radius: 4px;
        width: auto;
        min-width: 200px;
    }
    /* Additional specific style for the button text */
    .stButton>button span {
        font-weight: 900 !important;
    }
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        position: relative;
    }
    /* Center align the Home title */
    .title-text-center {
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        font-size: 3rem !important;  /* Increased size and added !important */
        font-weight: bold;
        margin: 0;
        z-index: 1;
    }
    /* Right align the Entries title with padding */
    .title-text-right {
        font-size: 1.75rem !important;
        font-weight: bold;
        margin: 0;
        margin-left: auto;
        padding-right: 100px;  /* Increased from 60px to 100px to move it more to the left */
        text-decoration: none;
        color: black;
    }
    .title-text-right:hover {
        opacity: 0.7;
    }
    /* Center content vertically */
    .vertical-center {
        margin-top: 30vh;  /* Push content down by 30% of viewport height */
    }
    </style>
    """, unsafe_allow_html=True)

# Create a single container for both titles
st.markdown("""
    <div class="header-container">
        <div style="width: 33%"></div>
        <p class="title-text-center">yap!</p>
        <a href="/entryList" class="title-text-right" target="_self">Entries</a>
    </div>
    """, unsafe_allow_html=True)

# Add vertical centering container
st.markdown('<div class="vertical-center">', unsafe_allow_html=True)

# Center the record button using a single column
_, col, _ = st.columns([1, 1, 1])

with col:
    record_button = st.button("Record")
    if record_button:
        st.write("Recording functionality will be implemented here")

st.markdown('</div>', unsafe_allow_html=True)
