import streamlit as st
import os
import datetime
from streamlit_mic_recorder import mic_recorder

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
    /* Style for mic recorder button */
    button.MuiButtonBase-root {
        background-color: white !important;
        color: black !important;
        border: 2px solid black !important;
        padding: 10px 20px !important;
        text-align: center !important;
        text-decoration: none !important;
        display: inline-block !important;
        font-size: 1.5rem !important;
        font-family: "Source Sans Pro", sans-serif !important;
        font-weight: 900 !important;
        margin: 0 auto !important;
        cursor: pointer !important;
        border-radius: 50% !important;
        width: 120px !important;
        height: 120px !important;
        min-width: unset !important;
        max-width: unset !important;
        transition: all 0.3s ease !important;
        box-shadow: none !important;
    }
    button.MuiButtonBase-root:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
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
    # Initialize session states
    if 'is_recording' not in st.session_state:
        st.session_state.is_recording = False
    if 'audio_data' not in st.session_state:
        st.session_state.audio_data = None
    
    # Use mic_recorder instead of audio_recorder
    audio = mic_recorder(
        start_prompt="Record",
        stop_prompt="Stop",
        key='recorder'
    )
    
    # Handle recorded audio
    if audio:
        # Store the audio data in session state
        st.session_state.audio_data = audio['bytes']
        
        # Save to root/s3/temp/
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "s3", "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(temp_dir, f"audio_{timestamp}.wav")
        
        # Save the audio file
        with open(filename, "wb") as f:
            f.write(audio['bytes'])

        
        
        # # Play back the recorded audio
        # st.audio(audio['bytes'])
        # st.success(f"Audio saved to: {filename}")

    # Always show the last recording if it exists
    elif st.session_state.audio_data:
        st.audio(st.session_state.audio_data)

st.markdown('</div>', unsafe_allow_html=True)
