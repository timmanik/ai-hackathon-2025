from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from app.transcribe import router as transcribe_router  # Import transcribe router

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

# Include the transcribe routes
app.include_router(transcribe_router, prefix="/api")

@app.get('/health')
async def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)