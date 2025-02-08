# Import libraries
import os
import requests
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv("./.env")

# Load the OpenAI client
client = OpenAI()

# Create an APIRouter instance
router = APIRouter()

# Function to download an audio file from a URL
# TODO: check this function--ChatGPT wrote it
def download_audio(url: str, save_path: str):
    """
    Download an audio file from a URL.

    Input:
    url: str: URL of the audio file
    save_path: str: Path to save the downloaded audio file

    Output:
    str: Path to the saved audio file
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return save_path
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error downloading file: {e}")

# Function to check file size
def check_acceptable_file_size(file_path):
    """
    Check if file size is less than 25 MB.

    Input:
    file_path: str: Path to the audio file

    Output:
    bool: True if file size is less than 25 MB, False otherwise
    """
    # https://help.openai.com/en/articles/7031512-whisper-audio-api-faq
    file_size = os.path.getsize(file_path) / (1024 * 1024)
    return file_size < 25

# Function to check file extension
def check_acceptable_file_extension(file_path):
    """
    Check if file has a supported audio extension.

    Input:
    file_path: str: Path to the audio file

    Output:
    bool: True if file extension is allowed, False otherwise
    """
    # https://help.openai.com/en/articles/7031512-whisper-audio-api-faq
    allowed_extensions = {".m4a", ".mp3", ".webm", ".mp4", ".mpga", ".wav", ".mpeg"}
    return os.path.splitext(file_path)[1].lower() in allowed_extensions

# Function to transcribe audio
def transcribe_audio(file_path):
    """
    Transcribe an audio file using OpenAI Whisper.

    Input:
    file_path: str: Path to the audio file

    Output:
    transcription: str: Transcription of the audio file
    """
    if not check_acceptable_file_size(file_path):
        raise HTTPException(status_code=400, detail="File size is too large. Must be under 25MB.")
    
    if not check_acceptable_file_extension(file_path):
        raise HTTPException(status_code=400, detail='Unsupported file type. Must be one of: ".m4a", ".mp3", ".webm", ".mp4", ".mpga", ".wav", ".mpeg"')
    
    with open(file_path, "rb") as audio_file:
        # https://platform.openai.com/docs/guides/speech-to-text
        transcription = client.audio.transcriptions.create(model="openai.whisper", file=audio_file)
    
    return transcription.text

# FastAPI Route to transcribe audio from URL
@router.get("/transcribe")
async def transcribe_audio_from_url(url: str, remove_temp_file: bool = True):
    """
    FastAPI endpoint to transcribe an audio file from a given URL.

    Input:
    url: str: URL of the audio file
    remove_temp_file: bool: Whether to remove the temporary audio file after transcription (default: True)

    Output:
    dict: Transcription result
    """
    try:
        temp_audio_path = "temp_audio_file"
        downloaded_file = download_audio(url, temp_audio_path)
        transcription = transcribe_audio(downloaded_file)
        
        # Only remove the file if remove_temp_file is True
        if remove_temp_file:
            os.remove(temp_audio_path)

        return {"transcription": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    print("Running transcribe.py standalone for testing...")

    temp_audio_path = "test_recordings/test.m4a"
    remove_temp_file = False  # Set to False to keep the file

    try:
        print("Checking file validation...")
        assert check_acceptable_file_size(temp_audio_path)
        assert check_acceptable_file_extension(temp_audio_path)

        print("Transcribing test file...")
        assert transcribe_audio(temp_audio_path) == "Hello, this is a test recording, this is a test recording, my name is Emilio, is this working?"

        print("All tests passed successfully!")

        # Only remove the file if remove_temp_file is True
        if remove_temp_file:
            os.remove(temp_audio_path)
    except Exception as e:
        print("Test failed:", e)