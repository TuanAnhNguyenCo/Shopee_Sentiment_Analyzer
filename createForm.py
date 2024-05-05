import json
import pandas as pd
 
data = pd.read_csv('RawRating/reviews.csv')
data = data.dropna()
form = []
for idx,row in data.iterrows():
    form.append({
        'product':row['product'],
        'rating':row['rating'],
        'comment':row['comment'],
        'label':0
    })
 

with open("data_form.json", "w",encoding="utf-8") as outfile:
    json.dump(form, outfile,ensure_ascii=False)