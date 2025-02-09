import os
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client with API key
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

client = OpenAI(api_key=api_key)
router = APIRouter()

def check_acceptable_file_size(file_path):
    # Must be < 25 MB
    return os.path.getsize(file_path) / (1024 * 1024) < 25

def check_acceptable_file_extension(file_path):
    allowed = {".m4a", ".mp3", ".webm", ".mp4", ".mpga", ".wav", ".mpeg"}
    ext = os.path.splitext(file_path)[1].lower()
    return ext in allowed

def transcribe_audio(file_path):
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404, 
            detail=f"File not found: {file_path}"
        )
    if not check_acceptable_file_size(file_path):
        raise HTTPException(
            status_code=400, 
            detail="File size is too large. Must be under 25MB."
        )
    if not check_acceptable_file_extension(file_path):
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file type."
        )
    
    with open(file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="openai.whisper",
            file=audio_file
        )
    return transcription.text

@router.get("/transcribe")
async def transcribe_local_file(filepath: str):
    """
    Transcribe a local file (e.g. test.m4a).
    
    Parameters:
        filepath: str - Path to the audio file relative to the app directory
    """
    from pathlib import Path

    current_dir = Path(__file__).parent
    try:
        # Clean up the filepath by removing any quotes
        clean_filepath = filepath.strip("'")
        transcription = transcribe_audio(current_dir / clean_filepath)
        return {"transcription": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    from pathlib import Path

    current_dir = Path(__file__).parent

    # Simple standalone test
    test_file_path = current_dir / "recordings" / "test.m4a"

    try:
        # Check
        assert check_acceptable_file_size(test_file_path), "File too large!"
        assert check_acceptable_file_extension(test_file_path), "Bad extension!"

        # Transcribe
        text = transcribe_audio(test_file_path)
        print("Transcription:", text)

    except Exception as e:
        print("Error during transcription test:", e)