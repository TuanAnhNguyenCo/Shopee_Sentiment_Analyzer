import re
import json
import requests
import pandas as pd
from tqdm.auto import tqdm
from clean_data import CleanData

class Crawl_Shopee_Review:
    def __init__(self, max_reviews_per_product=400, save_dir=''):
        self.data = []
        self.max_reviews_per_product = max_reviews_per_product
        self.save_dir = save_dir
        self.clean = CleanData()

    def get_rating_urls(self, url):
        r = re.search(r"i\.(\d+)\.(\d+)", url)
        self.shop_id, self.item_id = r[1], r[2]
        self.ratings_url = "https://shopee.vn/api/v2/item/get_ratings?filter=0&flag=1&itemid={item_id}&limit=20&offset={offset}&shopid={shop_id}&type=0"
        print(self.ratings_url)

    def get_data_from_urls(self, urls):
        assert type(urls) is list
        for url in tqdm(urls):
            self.get_data_from_url(url, batch=True)

        df = pd.DataFrame(self.data, columns=[
            'product', 'username', 'rating', 'comment'])
        df.to_csv(f"{self.save_dir}/reviews.csv", index=False, encoding="utf8")

        print("*"*10, 'DONE', '*'*10)
        print(
            f'Your file was saved in {self.save_dir} with name is reviews.csv')

    def get_data_from_url(self, url, batch=False):
        self.ratings_url = None
        self.get_rating_urls(url)
        assert self.ratings_url is not None
        try:
            for offset in tqdm(range(20, self.max_reviews_per_product+1, 20)):
                data = requests.get(
                    self.ratings_url.format(
                        shop_id=self.shop_id, item_id=self.item_id, offset=offset)
                ).json()
                for i, rating in enumerate(data["data"]["ratings"], 1):
                    self.data.append([
                        self.clean_text(data['data']['ratings'][0]['original_item_info']['name']),
                        rating["author_username"],
                        rating["rating_star"], 
                        self.clean_text(rating["comment"])])
        except Exception as ex:
            print(ex)

        if batch is False:
            df = pd.DataFrame(self.data, columns=[
                              'product', 'username', 'rating', 'comment'])
            df.to_csv(f"{self.save_dir}/reviews.csv",
                      index=False, encoding="utf8")

            print("*"*10, 'DONE', '*'*10)
            print(
                f'Your file was saved in {self.save_dir} with name is reviews.csv')


crawler = Crawl_Shopee_Review(
    100, 'G:\Projects\Reviews_classification\RawRating')
urls = ["https://shopee.vn/%C3%81o-croptop-m%C3%A0u-%C4%91en-%C3%A1o-crt-thun-n%E1%BB%AF-ki%E1%BB%83u-ph%E1%BB%91i-c%E1%BB%95-s%C6%A1-mi-tr%E1%BA%AFng-%C3%B4m-body-tay-d%C3%A0i-sexy-c%C3%A1-t%C3%ADnh-%C4%91%E1%BA%B9p-ng%E1%BA%A7u-gi%C3%A1-r%E1%BA%BB-i.39682649.11424337247?sp_atk=1ba4155e-a5e7-45fe-bbe4-ed846c81e7aa&xptdk=1ba4155e-a5e7-45fe-bbe4-ed846c81e7aa"]
crawler.get_data_from_urls(urls)
