from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from transcribe import router as transcribe_router  # Remove 'app.' from import
from analyze_transcript import router as analyze_router  # Add analyze router import
import uvicorn
import boto3
import os
    
load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("Missing OPENAI_API_KEY in environment variables")

session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'), 
    region_name=os.getenv('AWS_DEFAULT_REGION')
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

# Include both routers
app.include_router(transcribe_router, prefix="/api")
app.include_router(analyze_router, prefix="/analyze")  # Add analyze router

@app.get('/health')
async def health():
    return {'status': 'healthy'}

if __name__ == '__main__':

    uvicorn.run(app, host='0.0.0.0', port=8000)