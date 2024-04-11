import pandas as pd
import random

data = pd.read_csv("reviews.csv")
print(data.shape)
max_low_rv = 1200
max_high_rv = 1200
data = data.sample(frac=1)
# Filter low rating and non-empty comment
low_rating = data[(data['rating'] <= 3) & (data['comment'] != '')]

# Filter high rating and non-empty comment
high_rating = data[(data['rating'] >= 4) & (data['comment'] != '')]

if low_rating.shape[0] < max_low_rv:
    max_high_rv += (max_low_rv - low_rating.shape[0])

if high_rating.shape[0] < max_high_rv:
    max_low_rv += (max_high_rv - high_rating.shape[0])

low_rating = low_rating[:max_low_rv]
high_rating = high_rating[:max_high_rv]

filtered_files = []
filtered_files.extend(low_rating.values)
filtered_files.extend(high_rating.values)

print(len(filtered_files))


random.shuffle(filtered_files)

name = ['hoangnb','anhnct','hoangpv','hanhnth','anhpt','thunt']
for idx,n in enumerate(name):
    print(len(filtered_files[idx*400:(idx+1)*400]) )
    pd.DataFrame(filtered_files[idx:(idx+1)*400],columns = ['author','rating','comment']).to_csv(f"FilteredReviews/{n}.csv",index = False)
