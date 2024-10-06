from fastapi import FastAPI, HTTPException
from aws_func import S3_BUCKET_NAME, setup_aws_clients, translate_text_func
import logging

from models import (
    TranslateRequest,
)

app = FastAPI()

# Initialize AWS clients
aws_clients = setup_aws_clients()

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post("/text_translate")
async def text_translate(request: TranslateRequest):
    if not aws_clients:
        raise HTTPException(status_code=500, detail="AWS clients not initialized")
    
    translated_text = translate_text_func(aws_clients, request.text, request.source_lang, request.target_lang)
    
    if translated_text is None:
        raise HTTPException(status_code=500, detail="Translation failed")
    
    return {"translated_text": translated_text}
