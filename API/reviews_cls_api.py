from fastapi import FastAPI, File, UploadFile, Request
from secrets import token_hex
from model import ReviewsClassificationInference
import requests 
import json

app = FastAPI()
pipeline = ReviewsClassificationInference('cuda:1')


@app.get('/')
def root():
    return {'message': 'Welcome to the Image Classification API'}


@app.post("/classify_reviews/")
async def transform_text_to_speech(text: str):
    output = pipeline(text)
    return {'message': f'{output}'}
