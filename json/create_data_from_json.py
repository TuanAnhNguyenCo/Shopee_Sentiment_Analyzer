import glob
import json
import pandas as pd

json_files = glob.glob("*.json")
limit = 200
aspect_based_data = []
for file in json_files:
    with open(file, 'r') as f:
        data = json.load(f)
    for idx,js in enumerate(data):
        if limit is not None and idx == limit:
            break
        comment = js['comment'].split(' ')
        aspect_tag = [0]*len(comment)
        sentiment_tag = [-1]*len(comment)
        cnt = 0
        if js['aspect'] != "":
            js['aspect'] = js['aspect'].strip().replace('.',',')
            # print(js['aspect'],file,idx)
            if js['aspect'][-1] == ",":
                js['aspect'] = js['aspect'][:-1]
           
            
            for i in range(len(comment)):
                for ap in js['aspect'].split(',')[cnt:]:
                    ap,sentiment = ap.strip().split('-')
                    ap = ap.strip().split(' ') 
                    if ' '.join(ap) == ' '.join(comment[i:i+len(ap)]):
                        for k in range(len(ap)):
                            if k == 0:
                                aspect_tag[i] = 1
                            else:
                                aspect_tag[i+k] = 2
                            sentiment_tag[i+k] = sentiment
                        cnt +=1
                        
        aspect_based_data.append([js['product'],comment,aspect_tag,sentiment_tag])

df = pd.DataFrame(aspect_based_data,columns = ['product','comment','aspect_tag','sentiment_tag'])
df.to_csv("aspect_based_data.csv",index = False)



