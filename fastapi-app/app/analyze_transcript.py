import boto3
import json
from datetime import datetime
from botocore.exceptions import ClientError
from fastapi import APIRouter
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import Union
import os

# Add AWS credentials
session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'), 
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

region = 'us-west-2'
modelId = 'anthropic.claude-3-5-sonnet-20241022-v2:0'
bedrock_client = session.client(
    service_name='bedrock-runtime',
    region_name=region
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptGenerator:
    @staticmethod
    def generate_summary_prompt(HISTORY):
        ######################################## INPUT VARIABLES ########################################
        
        # Second input variable - the user's question
        QUESTION = "Can you Summarize the journal entry?"

        ######################################## PROMPT ELEMENTS ########################################
        TASK_CONTEXT = "You are like the users friend. You do not want to repeat what the user told you. Also talk to the user in the 2nd person."
        
        TONE_CONTEXT = "You should maintain a friendly warm and casual tone."
        
        TASK_DESCRIPTION = """ I want you to write a brief summary of the the users journal entry. Noting main events and things that they placed emphasis on"""
        
        EXAMPLES = None 
        
        INPUT_DATA = f"""Here is the conversational history (between the user and you) prior to the question. It could be empty if there is no history:
        <history>
        {HISTORY}
        </history>
        
        Here is the user's question:
        <question>
        {QUESTION}
        </question>"""
        
        IMMEDIATE_TASK = "How do you respond to the user's question in a thoughtful non-biased manner? Categorize these summaries into different Topics"
        
        PRECOGNITION = "Think about your answer first before you respond. Do not give them advice on what to do but summarize how they've been feeling."
        
        OUTPUT_FORMATTING = """ Start with the summary topics. Make it no longer than 1000 characters. No preamble just the thing specifically asked for. Do not do \"Here is your summary\" or anything like that.  """
        
        PREFILL = None

        ######################################## COMBINE ELEMENTS ########################################
        
        PROMPT = ""
        
        if TASK_CONTEXT:
            PROMPT += f"""{TASK_CONTEXT}"""
        
        if TONE_CONTEXT:
            PROMPT += f"""\n\n{TONE_CONTEXT}"""
        
        if TASK_DESCRIPTION:
            PROMPT += f"""\n\n{TASK_DESCRIPTION}"""
        
        if EXAMPLES:
            PROMPT += f"""\n\n{EXAMPLES}"""
        
        if INPUT_DATA:
            PROMPT += f"""\n\n{INPUT_DATA}"""
        
        if IMMEDIATE_TASK:
            PROMPT += f"""\n\n{IMMEDIATE_TASK}"""
        
        if PRECOGNITION:
            PROMPT += f"""\n\n{PRECOGNITION}"""
        
        if OUTPUT_FORMATTING:
            PROMPT += f"""\n\n{OUTPUT_FORMATTING}"""
        
        return PROMPT, PREFILL

    @staticmethod
    def generate_key_points_prompt(HISTORY):
        ######################################## INPUT VARIABLES ########################################
        
        # Second input variable - the user's question
        QUESTION = "Based on the provided summary can you generate short key insights/points?"

        ######################################## PROMPT ELEMENTS ########################################
        TASK_CONTEXT = "You are like the users friend. You do not want to repeat what the user told you. Also talk to the user in the 2nd person."
        
        TONE_CONTEXT = "You should maintain a friendly warm and casual tone."
        
        TASK_DESCRIPTION = """ I want you to write some key insights about the emotions the user has expressed in a digestable easy to read manner."""
        
        EXAMPLES = None 
        
        INPUT_DATA = f"""Here is the conversational history (between the user and you) prior to the question. It could be empty if there is no history:
        <history>
        {HISTORY}
        </history>

        Here is the user's question:
        <question>
        {QUESTION}
        </question>"""
        
        IMMEDIATE_TASK = "How do you respond to the user's question in a thoughful non biased manner?"
        
        PRECOGNITION = "Think about your answer first before you respond. Do not give them advice on what to do but give highlight trends they may not have noticed. Focus on emotions being felt."
        
        OUTPUT_FORMATTING = "Make it no longer than 230 characters. Do not format by category. Use bullet point fomrat. No preamble just the thing specifically asked for."
        
        PREFILL = None

        ######################################## COMBINE ELEMENTS ########################################
        
        PROMPT = ""
        
        if TASK_CONTEXT:
            PROMPT += f"""{TASK_CONTEXT}"""
        
        if TONE_CONTEXT:
            PROMPT += f"""\n\n{TONE_CONTEXT}"""
        
        if TASK_DESCRIPTION:
            PROMPT += f"""\n\n{TASK_DESCRIPTION}"""
        
        if EXAMPLES:
            PROMPT += f"""\n\n{EXAMPLES}"""
        
        if INPUT_DATA:
            PROMPT += f"""\n\n{INPUT_DATA}"""
        
        if IMMEDIATE_TASK:
            PROMPT += f"""\n\n{IMMEDIATE_TASK}"""
        
        if PRECOGNITION:
            PROMPT += f"""\n\n{PRECOGNITION}"""
        
        if OUTPUT_FORMATTING:
            PROMPT += f"""\n\n{OUTPUT_FORMATTING}"""
        
        return PROMPT, PREFILL

    @staticmethod
    def generate_title_prompt(HISTORY):
        ######################################## INPUT VARIABLES ########################################
        
        # Second input variable - the user's question
        QUESTION = "Generate a Title for this journal Entry?"

        ######################################## PROMPT ELEMENTS ########################################
        TASK_CONTEXT = "You are like the users friend. You do not want to repeat what the user told you. Also talk to the user in the 2nd person."
        
        TONE_CONTEXT = "You should maintain a friendly warm and casual tone."
        
        TASK_DESCRIPTION = """ You are going to be generating a jounral entry title. That should be unique and easy to pick out compared to other entries"""
        
        EXAMPLES = None 
        
        INPUT_DATA = f"""Here is the conversational history (between the user and you) prior to the question. It could be empty if there is no history:
        <history>
        {HISTORY}
        </history>

        Here is the user's question:
        <question>
        {QUESTION}
        </question>"""
        
        IMMEDIATE_TASK = "Generate a Jounral Entry title"
        
        PRECOGNITION = "Think about your answer first before you respond. Do not reveal any sensitive information. Don't make it extreemly negative. "
        
        OUTPUT_FORMATTING = """ Leave out any sensitive information like names. No preamble just the thing specifically asked for."""
        
        PREFILL = None

        ######################################## COMBINE ELEMENTS ########################################
        
        PROMPT = ""
        
        if TASK_CONTEXT:
            PROMPT += f"""{TASK_CONTEXT}"""
        
        if TONE_CONTEXT:
            PROMPT += f"""\n\n{TONE_CONTEXT}"""
        
        if TASK_DESCRIPTION:
            PROMPT += f"""\n\n{TASK_DESCRIPTION}"""
        
        if EXAMPLES:
            PROMPT += f"""\n\n{EXAMPLES}"""
        
        if INPUT_DATA:
            PROMPT += f"""\n\n{INPUT_DATA}"""
        
        if IMMEDIATE_TASK:
            PROMPT += f"""\n\n{IMMEDIATE_TASK}"""
        
        if PRECOGNITION:
            PROMPT += f"""\n\n{PRECOGNITION}"""
        
        if OUTPUT_FORMATTING:
            PROMPT += f"""\n\n{OUTPUT_FORMATTING}"""
        
        return PROMPT, PREFILL
    
    
async def get_completion(prompt, system_prompt=None, prefill=None):
    inference_config = {
        "temperature": 0.2,
         "maxTokens": 200
    }
    converse_api_params = {
        "modelId": modelId,
        "messages": [{"role": "user", "content": [{"text": prompt}]}],
        "inferenceConfig": inference_config
    }
    if system_prompt:
        converse_api_params["system"] = [{"text": system_prompt}]
    if prefill:
        converse_api_params["messages"].append({"role": "assistant", "content": [{"text": prefill}]})
    try:
        # Use asyncio to run the blocking bedrock_client.converse call
        response = await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: bedrock_client.converse(**converse_api_params)
        )
        text_content = response['output']['message']['content'][0]['text']
        return text_content

    except ClientError as err:
        message = err.response['Error']['Message']
        print(f"A client error occurred: {message}")
        raise HTTPException(status_code=500, detail=message)

from pydantic import BaseModel

class TranscriptionRequest(BaseModel):
    transcription: Union[dict, str]  # Accepts either a dictionary or string
    
    class Config:
        json_schema_extra = {
            "example": {
                "transcription": {
                    "text": "Your journal entry text here",
                    "metadata": {
                        "timestamp": "2024-03-14T12:00:00Z"
                    }
                }
            }
        }

router = APIRouter()

@router.post("/generate_summary/")
async def generate_summary(request: TranscriptionRequest):
    summary_prompt = PromptGenerator()
    try: 
        prompt, prefill = summary_prompt.generate_summary_prompt(request.transcription)
        summary = await get_completion(prompt, prefill) 
        return {"summary": summary}
    except Exception as e: 
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate_keypoints/")
async def generate_keypoints(request: TranscriptionRequest):
    key_points_prompt = PromptGenerator()
    try:
        prompt, prefill = key_points_prompt.generate_key_points_prompt(request.transcription)
        key_points = await get_completion(prompt, prefill)
        return {"key_points": key_points}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate_title/")
async def generate_title(request: TranscriptionRequest):
    title_prompt = PromptGenerator()
    try:
        prompt, prefill = title_prompt.generate_title_prompt(request.transcription)
        title = await get_completion(prompt, prefill)
        return {"title": title}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))