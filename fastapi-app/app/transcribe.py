# import os
# import boto3
# from fastapi import APIRouter, HTTPException
# from openai import OpenAI
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv("./.env")

# client = OpenAI()
# router = APIRouter()

# s3 = boto3.client("s3")
# BUCKET_NAME = "yap.data"

# def download_audio_from_s3(s3_key: str, save_path: str):
#     try:
#         s3.download_file(BUCKET_NAME, s3_key, save_path)
#     except Exception as e:
#         raise HTTPException(
#             status_code=400, 
#             detail=f"Error downloading file from S3: {e}"
#         )

# def check_acceptable_file_size(file_path):
#     # Must be < 25 MB
#     return os.path.getsize(file_path) / (1024 * 1024) < 25

# def check_acceptable_file_extension(file_path):
#     allowed = {".m4a", ".mp3", ".webm", ".mp4", ".mpga", ".wav", ".mpeg"}
#     ext = os.path.splitext(file_path)[1].lower()
#     return ext in allowed

# def transcribe_audio(file_path):
#     if not check_acceptable_file_size(file_path):
#         raise HTTPException(
#             status_code=400, 
#             detail="File size is too large. Must be under 25MB."
#         )
#     if not check_acceptable_file_extension(file_path):
#         raise HTTPException(
#             status_code=400, 
#             detail="Unsupported file type."
#         )
    
#     with open(file_path, "rb") as audio_file:
#         transcription = client.audio.transcriptions.create(
#             model="openai.whisper", 
#             file=audio_file
#         )
#     return transcription.text

# @router.get("/transcribe")
# async def transcribe_audio_from_s3(filename: str):
#     """
#     Transcribe a file from S3's recordings/ folder (e.g. test.m4a).
#     Always removes local file afterward.
#     """
#     s3_key = f"recordings/{filename}"
#     try:
#         # Download and keep the same local filename
#         download_audio_from_s3(s3_key, filename)
        
#         # Transcribe and clean up
#         transcription = transcribe_audio(filename)
#         os.remove(filename)  # Always remove local file
        
#         return {"transcription": transcription}
#     except Exception as e:
#         # If something goes wrong, ensure we clean up anyway
#         if os.path.exists(filename):
#             os.remove(filename)
#         raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     # Simple standalone test
#     test_filename = "test.m4a"
#     s3_key = f"recordings/{test_filename}"

#     try:
#         # Download to local test.m4a
#         download_audio_from_s3(s3_key, test_filename)

#         # Check
#         assert check_acceptable_file_size(test_filename), "File too large!"
#         assert check_acceptable_file_extension(test_filename), "Bad extension!"

#         # Transcribe
#         text = transcribe_audio(test_filename)
#         print("Transcription:", text)

#     finally:
#         # Clean up local file
#         if os.path.exists(test_filename):
#             os.remove(test_filename)

import os
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv("./.env")

client = OpenAI()
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
    """
    from pathlib import Path

    current_dir = Path(__file__).parent
    try:
        transcription = transcribe_audio(current_dir / filepath)
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
