import re
import json
import requests
import pandas as pd
from tqdm.auto import tqdm
from clean_data import CleanData

#khi chạy code cần login shopee lấy cookies thay vào phần cookie
#truy cập link https://shopee.vn/api/v2/item/get_ratings?filter=0&flag=1&itemid=11424337247&limit=20&offset=0&shopid=39682649&type=0
headers = {
    'authority': 'shopee.vn',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'vi,vi-VN;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
    'Cache-Control': 'max-age=0',
    'Cookie': 'SPC_SI=TE0vZgAAAABBRWFsZVE2UpQQlAAAAAAAQ0Z0QlVDTjg=; SPC_SEC_SI=v1-RThMdUgwWVZTYXJEajh1OeVetya1oDW5FSCjWTWZRWL6qBT2SAMvv8qlQdKkMbIXxyn8rKgc4nMvir7BD/z4o/lLeIvBZqGFQKR1+C/Ysb8=; SPC_F=4wVsgvENFFS5Jp61U0BnGtl0WgwLdM84; REC_T_ID=d3e85524-0ab4-11ef-be27-5ef2fac23a29; __LOCALE__null=VN; csrftoken=VY4GDo5O4AJaFRHqzCfoInyHShHKQHuS; _sapid=fd9c00bf3ea337d9723ce66fc5d547780a3041204ee519be8686b923; _QPWSDCXHZQA=2e22e258-6806-4097-ca22-04fd8b892ed5; REC7iLP4Q=b9af0c29-a4b1-4c78-bc32-e342e037fdc1; SPC_CLIENTID=NHdWc2d2RU5GRlM1ymekwsezfaczwcsd; SPC_EC=.SDJxMDJOUm5CcU41NEFCOcpi0HTsW8oAGy6YFG3VwtpweO90UWXwCwrLO116rA9KV9OppDzDMYUaove32JmFB6u3O5UIDF4N55VU3/MRR232qZauoG1CPz4JrPQ8iOEaL3tdcDn8uW4Zn5nHceNEvJ9ClWgZZQbhvESVcwjqdL7exsg49Z8GKvfr6uGpvnL31X8V2B6TmvwbUXAbw4w2BQ==; SPC_ST=.SDJxMDJOUm5CcU41NEFCOcpi0HTsW8oAGy6YFG3VwtpweO90UWXwCwrLO116rA9KV9OppDzDMYUaove32JmFB6u3O5UIDF4N55VU3/MRR232qZauoG1CPz4JrPQ8iOEaL3tdcDn8uW4Zn5nHceNEvJ9ClWgZZQbhvESVcwjqdL7exsg49Z8GKvfr6uGpvnL31X8V2B6TmvwbUXAbw4w2BQ==; SPC_U=991218307; SPC_R_T_ID=rRvFPAjAW61phddGCWwHce0VCHcRV3Pwh62/GyaGwcuF83oqqY8StJxyVtsw3hJfIaqeK+VVXaMSOotHcJPjrP4ndDgnhElDmlLufYTDacdM7X2PSn/nE2AZRe6oC3+A6T6FN08EmBLSt2igov5r66Ti6VQLNta/Le2wSgPl+DA=; SPC_R_T_IV=aXFFeEdjM2Y4bGptWDFPOA==; SPC_T_ID=rRvFPAjAW61phddGCWwHce0VCHcRV3Pwh62/GyaGwcuF83oqqY8StJxyVtsw3hJfIaqeK+VVXaMSOotHcJPjrP4ndDgnhElDmlLufYTDacdM7X2PSn/nE2AZRe6oC3+A6T6FN08EmBLSt2igov5r66Ti6VQLNta/Le2wSgPl+DA=; SPC_T_IV=aXFFeEdjM2Y4bGptWDFPOA==; SPC_CDS_CHAT=26698a3c-d82d-43ae-86f2-5cbf30853723',
    'Priority': 'u=0, i',
    'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

class Crawl_Shopee_Review:
    def __init__(self, max_reviews_per_product=400, save_dir=''):
        self.data = []
        self.max_reviews_per_product = max_reviews_per_product
        self.save_dir = save_dir
        self.clean = CleanData(abbreviation_words_file_url = 'specialchar.txt',save_dir = './')

    def get_rating_urls(self, url):
        r = re.search(r"i\.(\d+)\.(\d+)", url)
        self.shop_id, self.item_id = r[1], r[2]
        self.ratings_url = "https://shopee.vn/api/v4/item/get_ratings?filter=0&flag=1&itemid={item_id}&limit=20&offset={offset}&shopid={shop_id}&type=0"

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
                ,headers=headers).json()
                print(data)
                for i, rating in enumerate(data["data"]["ratings"], 1):
                    self.data.append([
                        self.clean.clean_text(data['data']['ratings'][0]['original_item_info']['name']),
                        rating["author_username"],
                        rating["rating_star"], 
                        self.clean.clean_text(rating["comment"])])
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
