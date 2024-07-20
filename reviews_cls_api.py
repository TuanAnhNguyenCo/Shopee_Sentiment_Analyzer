from fastapi import FastAPI, File, UploadFile, Request
from secrets import token_hex
from utils.reviews_cls_system import Reviews_CLS_System
import requests 
from fastapi.middleware.cors import CORSMiddleware
import json
from pydantic import BaseModel

app = FastAPI()
system = Reviews_CLS_System(device = 'cuda:0',device1 = 'cuda:0',device2 = 'cuda:0',bs = 16)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả các nguồn gốc
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả các phương thức HTTP
    allow_headers=["*"],  # Cho phép tất cả các tiêu đề
)

class ItemUrl(BaseModel):
    url: str
    aspect_analysis: bool = False

@app.get('/')
def root():
    return {'message': 'Welcome to the Reviews Classification API'}


@app.post("/reviews_classification/")
async def classify_reviews(item: ItemUrl):
    return system(item.url,item.aspect_analysis)