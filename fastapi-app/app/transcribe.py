# Import libraries
import os
import requests
import boto3
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv("./.env")

# Load the OpenAI client
client = OpenAI()

# Create an APIRouter instance
router = APIRouter()

# Initialize S3 client
s3 = boto3.client('s3')

# Function to download an audio file from a URL or S3
def download_audio(source: str, save_path: str, is_s3: bool = False, bucket_name: str = None):
    """
    Download an audio file from a URL or an S3 bucket.

    Input:
    source: str: URL of the audio file OR S3 key if downloading from S3
    save_path: str: Path to save the downloaded audio file
    is_s3: bool: Flag to indicate if the source is from S3 (default: False)
    bucket_name: str: Required if downloading from S3

    Output:
    str: Path to the saved audio file
    """
    try:
        if is_s3:
            if not bucket_name:
                raise HTTPException(status_code=400, detail="Bucket name is required for S3 downloads.")
            s3.download_file(bucket_name, source, save_path)
        else:
            response = requests.get(source, stream=True)
            response.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        return save_path

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error downloading file from URL: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error downloading file from S3: {e}")

# Function to check file size
def check_acceptable_file_size(file_path):
    """
    Check if file size is less than 25 MB.

    Input:
    file_path: str: Path to the audio file

    Output:
    bool: True if file size is less than 25 MB, False otherwise
    """
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
        transcription = client.audio.transcriptions.create(model="openai.whisper", file=audio_file)
    
    return transcription.text

# FastAPI Route to transcribe audio from a URL or S3
@router.get("/transcribe")
async def transcribe_audio_from_source(source: str, is_s3: bool = False, bucket_name: str = None, remove_temp_file: bool = True):
    """
    FastAPI endpoint to transcribe an audio file from a given URL or S3 bucket.

    Input:
    source: str: URL of the audio file OR S3 key if downloading from S3
    is_s3: bool: Flag to indicate if the source is from S3 (default: False)
    bucket_name: str: Required if downloading from S3
    remove_temp_file: bool: Whether to remove the temporary audio file after transcription (default: True)

    Output:
    dict: Transcription result
    """
    try:
        temp_audio_path = "temp_audio_file"
        downloaded_file = download_audio(source, temp_audio_path, is_s3, bucket_name)
        transcription = transcribe_audio(downloaded_file)
        
        # Only remove the file if remove_temp_file is True
        if remove_temp_file:
            os.remove(temp_audio_path)

        return {"transcription": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    print("Running transcribe.py standalone for testing...")

    # Local file test
    temp_audio_path = "test_recordings/test.m4a"
    remove_temp_file = False  # Set to False to keep the file

    try:
        print("Checking file validation for local file...")
        assert check_acceptable_file_size(temp_audio_path)
        assert check_acceptable_file_extension(temp_audio_path)

        print("Transcribing test local file...")
        assert transcribe_audio(temp_audio_path) == "Hello, this is a test recording, this is a test recording, my name is Emilio, is this working?"

        print("Local file test passed successfully!")

        if remove_temp_file:
            os.remove(temp_audio_path)
    except Exception as e:
        print("Local file test failed:", e)

    # S3 test case
    print("\nTesting S3 file download and transcription...")

    bucket_name = "yap.data"
    file_key = "recordings/test.m4a"
    local_filename = "test_from_s3.m4a"

    try:
        print(f"Downloading {file_key} from bucket {bucket_name}...")
        download_audio(file_key, local_filename, is_s3=True, bucket_name=bucket_name)

        print("Checking file validation for S3 file...")
        assert check_acceptable_file_size(local_filename)
        assert check_acceptable_file_extension(local_filename)

        print("Transcribing test S3 file...")
        transcription_result = transcribe_audio(local_filename)
        print(f"Transcription: {transcription_result}")

        print("S3 file test passed successfully!")

        if remove_temp_file:
            os.remove(local_filename)
    except Exception as e:
        print("S3 file test failed:", e)