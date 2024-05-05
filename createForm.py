import json
import pandas as pd
import requests
from tqdm.auto import tqdm 

data = pd.read_csv('reviews.csv')
data = data.dropna()
form = []

# if you run on your device please replace it. I'm runing on the server
url = 'http://222.252.4.232:9999/classify_reviews' 


for idx,row in tqdm(data.iterrows()):
    data = {
        'text': row['comment']
    }
    response = requests.post(url,params = data)
    label = 0
    output = response.json()['message'].lower()
    if output == 'positive':
        label = 1
    elif output == 'negative':
        label = 2
    else:
        print('error')
        break
   
    form.append({
        'product':row['product'],
        'rating':row['rating'],
        'comment':row['comment'],
        'label':label
    })
 

with open("data_form.json", "w",encoding="utf-8") as outfile:
    json.dump(form, outfile,ensure_ascii=False)