import streamlit as st
import os
import datetime
from streamlit_mic_recorder import mic_recorder
import httpx
import asyncio
from dotenv import load_dotenv
from flask import Flask, request, jsonify


server_url = "http://localhost:8000"

load_dotenv()


transcription_api = os.getenv("OPENAI_API_KEY")

async def get_transcription(entry_id, audio_path):
    # Get API token from environment variable
    # transcription_api = os.getenv('TRANSCRIPTION_API_TOKEN')
    # if not transcription_api:
    #     st.error("Missing TRANSCRIPTION_API_TOKEN in environment variables")
    #     return None


    headers = {
        "Authorization": f"Bearer {transcription_api}",  # Add 'Bearer ' prefix if required
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{server_url}/api/transcribe",
                params={"filepath": audio_path},
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except httpx.ConnectError:
        st.error("Could not connect to the transcription server. Please make sure the FastAPI server is running.")
        return None
    except Exception as e:
        st.error(f"An error occurred during transcription: {str(e)}")
        return None
    

async def generate_analysis(transcript):
        """
        Generate the analysis for a given transcript
        """
        script = {
                "transcription": {
                        "text": transcript,
                        "metadata": {
                        "timestamp": "2024-03-14T12:00:00Z"
                        }
                }
        }
        
        prefix = "/analyze/"
        endpoints = {
                "title": server_url + prefix + "generate_title/",
                "summary": server_url + prefix + "generate_summary/",
                "keypoints": server_url + prefix + "generate_keypoints/"
        }
        
        results = {}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
                for name, endpoint in endpoints.items():
                        try:
                                response = await client.post(endpoint, json=script)
                                response.raise_for_status()  # Raise an exception for bad status codes
                                results[name] = response.json()
                                st.write(f"{name.capitalize()} Response:", results[name])
                        except httpx.TimeoutException:
                                st.write(f"Timeout while fetching {name}")
                                results[name] = None
                        except httpx.HTTPError as e:
                                st.write(f"HTTP error occurred while fetching {name}: {e}")
                                results[name] = None
                        except Exception as e:
                                st.write(f"Unexpected error while fetching {name}: {e}")
                                results[name] = None
                                
        
        return results

# Configure the page
st.set_page_config(
    page_title="Home",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,700&display=swap');
    
    .stApp {
        background-color: #f7f1eb;
        color: #2b1810;  /* Updated from #4a3524 */
    }
    /* Style for mic recorder button */
    button.MuiButtonBase-root {
        background-color: white !important;
        color: #2b1810 !important;
        border: 2px solid #2b1810 !important;
        padding: 10px 20px !important;
        text-align: center !important;
        text-decoration: none !important;
        display: inline-block !important;
        font-size: 3rem !important;
        font-family: 'Fraunces', serif !important;
        font-weight: bold !important;
        margin: 0 auto !important;
        cursor: pointer !important;
        border-radius: 50% !important;
        width: 160px !important;  /* Increased from 120px */
        height: 160px !important;  /* Increased from 120px */
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
        font-size: 3rem !important;
        font-family: 'Fraunces', serif !important;
        font-weight: bold;
        margin: 0;
        z-index: 1;
        color: #2b1810;  /* Updated from #4a3524 */
    }
    /* Right align the Entries title with padding */
    .title-text-right {
        font-size: 1.75rem !important;
        font-family: 'Fraunces', serif !important;
        font-weight: bold;
        margin: 0;
        margin-left: auto;
        padding-right: 100px;
        text-decoration: none;
        color: #2b1810;  /* Updated from #4a3524 */
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
        <a href="entryList" class="title-text-right">Entries</a>
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
        
        
        # st.write(os.getcwd() + "/fastapi-app/app/recordings") # correct path
        full_path = os.path.join(os.path.dirname(__file__))
        temp_dir = "fastapi-app/app/recordings/"
        path = os.path.join(full_path, temp_dir)
        os.makedirs(path, exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(path, "../", f"audio_{timestamp}.wav")
        # st.write(f"Filename: {filename}")
        
        # Save the audio file
        with open(filename, "wb") as f:
            f.write(audio['bytes'])

        # st.write("were here 2")
        file_path = os.path.join(os.getcwd(), "fastapi-app", "app", "recordings", f"audio_{timestamp}.wav")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write file
        try:
            with open(file_path, "wb") as f:
                f.write(audio['bytes'])
            # st.write(f"Successfully wrote to: {file_path}")
        except Exception as e:
            st.error(f"Error writing file: {str(e)}")
            
        # st.write("wrote to recordings")


        try:
            result = asyncio.run(get_transcription(1, audio_path=file_path))
            # if result:
                # st.success("Transcription completed successfully!")
                # st.write(result)
        except Exception as e:
            st.error(f"Error during transcription process: {str(e)}")
        

        # Process the audio file
        try:
            analysis_data = asyncio.run(generate_analysis(result))
            if analysis_data:
                # Send data to database
                try:
                    db_url = "http://localhost:8080/api/journal_entries/"
                    all_update_data = result | analysis_data
                    response = httpx.post(db_url, json=all_update_data)
                    response.raise_for_status()
                    
                    title = analysis_data.get('title', {}).get('title', 'your entry')
                    
                    # Clear any previous outputs
                    st.empty()
                    
                    # Display success message with the latest entry ID and no underline
                    st.markdown(
                        f'yap sesh finished. Check out your <a href="/entryList" style="text-decoration: none">{title}</a> entry',
                        unsafe_allow_html=True
                    )
                except Exception as e:
                    st.error(f"Error saving to database: {str(e)}")
        except Exception as e:
            st.error(f"Error during transcription process: {str(e)}")

    # Always show the last recording if it exists
    if st.session_state.audio_data:
        st.audio(st.session_state.audio_data)

st.markdown('</div>', unsafe_allow_html=True)



