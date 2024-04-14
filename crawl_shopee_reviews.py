import re
import json
import requests
import pandas as pd
from tqdm.auto import tqdm


class Crawl_Shopee_Review:
    def __init__(self, max_reviews_per_product=400, save_dir=''):
        self.data = []
        self.max_reviews_per_product = max_reviews_per_product
        self.save_dir = save_dir

    def get_rating_urls(self, url):
        r = re.search(r"i\.(\d+)\.(\d+)", url)
        self.shop_id, self.item_id = r[1], r[2]
        self.ratings_url = "https://shopee.vn/api/v2/item/get_ratings?filter=0&flag=1&itemid={item_id}&limit=20&offset={offset}&shopid={shop_id}&type=0"

    def get_data_from_urls(self, urls):
        assert type(urls) is list
        for url in tqdm(urls):
            self.get_data_from_url(url, batch=True)

        df = pd.DataFrame(self.data, columns=['username', 'rating', 'comment'])
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
                        data['data']['ratings'][0]['original_item_info']['name'],rating["author_username"],
                        rating["rating_star"], rating["comment"]])
        except Exception as ex:
            print(ex)

        if batch is False:
            df = pd.DataFrame(self.data, columns=[
                              'product','username', 'rating', 'comment'])
            df.to_csv(f"{self.save_dir}/reviews.csv",
                      index=False, encoding="utf8")

            print("*"*10, 'DONE', '*'*10)
            print(
                f'Your file was saved in {self.save_dir} with name is reviews.csv')


crawler = Crawl_Shopee_Review(100, '/Users/tuananh/Desktop/Dev/DL/Reviews_classification')
urls = [
    "https://shopee.vn/S%E1%BB%AFa-ch%E1%BB%91ng-n%E1%BA%AFng-La-Roche-Posay-Anthelios-UVMUNE400-Oil-Control-Fluid-50ml-i.37251700.21181809304?xptdk=ee6e0979-8aef-472f-bc34-7649bbee5ecf",
    "https://shopee.vn/Kem-n%E1%BB%81n-BB-FOCALLURE-31g-trang-%C4%91i%E1%BB%83m-khu%C3%B4n-m%E1%BA%B7t-che-khuy%E1%BA%BFt-%C4%91i%E1%BB%83m-ti%E1%BB%87n-l%E1%BB%A3i-i.182631756.3114622455?xptdk=6f2dfb7c-5ec7-4de0-8488-8ba41fa7b35c",
    "https://shopee.vn/Ph%E1%BA%A5n-ph%E1%BB%A7-FOCALLURE-3-m%C3%A0u-s%E1%BA%AFc-t%C3%B9y-ch%E1%BB%8Dn-trang-%C4%91i%E1%BB%83m-n%E1%BB%81n-th%E1%BB%9Di-trang-7g-i.182631756.7502654188?xptdk=6e4d1b2a-f71a-4735-a779-91575e37b06d",
    "https://shopee.vn/B%C3%BAt-k%E1%BA%BB-m%E1%BA%AFt-FOCALLURE-d%E1%BA%A1ng-l%E1%BB%8Fng-ch%E1%BB%91ng-th%E1%BA%A5m-n%C6%B0%E1%BB%9Bc-nhanh-kh%C3%B4-0.6g-i.182631756.6502613129?xptdk=c5c2e442-4597-46dd-b508-4cac23d004d7",
    "https://shopee.vn/Mascara-SACE-LADY-Ch%E1%BB%91ng-Th%E1%BA%A5m-N%C6%B0%E1%BB%9Bc-L%C3%A2u-Tr%C3%B4i-Chu%E1%BB%91t-Mi-D%C3%A0i-Ch%E1%BB%91ng-Lem-10g-0.35oz-i.83766754.4971846127?xptdk=d5f3acf8-b4cc-4bd1-b60f-790e14e6865b",
    "https://shopee.vn/Ch%C3%AC-K%E1%BA%BB-Vi%E1%BB%81n-M%C3%B4i-S%E1%BA%AFc-T%E1%BB%91-Cao-Trang-%C4%90i%E1%BB%83m-Cho-N%E1%BB%AF-SACE-LADY-i.83766754.20083941746",
    "https://shopee.vn/Ph%E1%BA%A5n-b%E1%BA%AFt-s%C3%A1ng-SACE-LADY-m%E1%BB%8Fng-nh%E1%BA%B9-t%E1%BA%A1o-hi%E1%BB%87u-%E1%BB%A9ng-3D-l%C3%AAn-m%C3%A0u-chu%E1%BA%A9n-trang-%C4%91i%E1%BB%83m-cho-m%E1%BA%B7t-Hilighter-6g-i.83766754.19545391737",
    "https://shopee.vn/Kem-che-khuy%E1%BA%BFt-%C4%91i%E1%BB%83m-Focallure-%C4%91%E1%BB%99-che-ph%E1%BB%A7-cao-ch%E1%BB%91ng-th%E1%BA%A5m-n%C6%B0%E1%BB%9Bc-gi%E1%BB%AF-m%C3%A0u-l%C3%A2u-tr%C3%B4i-4.3g-i.182631756.6364386266?xptdk=3c8c88cc-bf83-4098-8a7d-dc845c745987",
    "https://shopee.vn/Ph%E1%BA%A5n-m%C3%A1-h%E1%BB%93ng-FOCALLURE-11-m%C3%A0u-s%E1%BA%AFc-t%C3%B9y-ch%E1%BB%8Dn-trang-%C4%91i%E1%BB%83m-t%E1%BB%B1-nhi%C3%AAn-th%E1%BB%9Di-trang-2.8g-i.182631756.3302707838",
    "https://shopee.vn/Chai-x%E1%BB%8Bt-kh%C3%B3a-c%E1%BB%91-%C4%91%E1%BB%8Bnh-l%E1%BB%9Bp-trang-%C4%91i%E1%BB%83m-FOCALLURE-kh%C3%B4ng-b%E1%BB%8B-nh%C3%B2e-l%C3%A2u-tr%C3%B4i-nh%E1%BA%B9-65g-i.182631756.18270068868",
    "https://shopee.vn/N%C6%B0%E1%BB%9Bc-T%E1%BA%A9y-Trang-l%C3%A0m-s%E1%BA%A1ch-s%C3%A2u-d%E1%BB%8Bu-nh%E1%BA%B9-cho-m%E1%BB%8Di-lo%E1%BA%A1i-da-Garnier-Micellar-Cleansing-Water-400ml-i.421677475.10707015149?sp_atk=391ae58c-2c01-4ad8-a00b-a232c066d760&xptdk=391ae58c-2c01-4ad8-a00b-a232c066d760",
    "https://shopee.vn/Kem-D%C6%B0%E1%BB%A1ng-%E1%BA%A8m-Cerave-D%C3%A0nh-Cho-Da-Kh%C3%B4-Cerave-Moisturizing-Cream-50ml-340g-454g-i.18363975.19940164605?publish_id=&sp_atk=5a46f56c-2c07-4670-bbf9-56cf12a239c4&xptdk=5a46f56c-2c07-4670-bbf9-56cf12a239c4",
    "https://shopee.vn/Megaduo-Gel-Plus-Gamma-15g-30g-Gel-Gi%E1%BA%A3m-M%E1%BB%A5n-%E1%BA%A8n-Th%C3%A2m-%C4%90%E1%BA%A7u-%C4%90en-Cho-Da-D%E1%BA%A7u-M%E1%BB%A5n-Dr-Th%C3%AAm-i.18363975.5451541710",
    "https://shopee.vn/S%E1%BB%AFa-R%E1%BB%ADa-M%E1%BA%B7t-Hada-Labo-Advanced-Nourish-Perfect-White-Acne-Care-Pro-Anti-Aging-Cleanser-80g-Kem-R%E1%BB%ADa-M%E1%BA%B7t-D%C6%B0%E1%BB%A1ng-%E1%BA%A8m-i.18363975.23232932577",
    "https://shopee.vn/S%E1%BB%AFa-R%E1%BB%ADa-M%E1%BA%B7t-SVR-Cho-Da-D%E1%BA%A7u-M%E1%BB%A5n-SVR-Sebiaclear-Gel-Moussant-55ml-200ml-400ml-Lo%E1%BA%A1i-B%E1%BB%8F-T%E1%BA%BF-B%C3%A0o-Da-Ch%E1%BA%BFt-SRM-i.18363975.10001549800",
    "https://shopee.vn/M%E1%BA%B7t-N%E1%BA%A1-Gi%E1%BA%A5y-FOODAHOLIC-Mask-23g-(1-mi%E1%BA%BFng)-Ch%C4%83m-S%C3%B3c-Da-To%C3%A0n-Di%E1%BB%87n-D%C6%B0%E1%BB%A1ng-%E1%BA%A8m-D%C6%B0%E1%BB%A1ng-Tr%E1%BA%AFng-Da-H%C3%A0n-Qu%E1%BB%91c-i.18363975.22655926921",
    "https://shopee.vn/S%E1%BB%AFa-R%E1%BB%ADa-M%E1%BA%B7t-Ziaja-Manuka-Cho-Da-D%E1%BA%A7u-M%E1%BB%A5n-Tr%E1%BB%A9ng-C%C3%A1-Tree-Purifying-Normalising-Cleansing-Gel-200ml-i.18363975.25451358567",
    "https://shopee.vn/B%E1%BB%99-2-S%E1%BB%AFa-ch%E1%BB%91ng-n%E1%BA%AFng-d%E1%BB%8Bu-nh%E1%BA%B9-cho-da-nh%E1%BA%A1y-c%E1%BA%A3m-v%C3%A0-tr%E1%BA%BB-em-SPF-50-PA-60mlx2-i.58411241.8273131355",
    "https://shopee.vn/(New)-Son-Tint-B%C3%B3ng-Romand-Glasting-Color-GLOSS-c%C4%83ng-m%E1%BB%8Dng-m%C3%B4i-i.58282982.25304540160?sp_atk=8c1257db-a909-4bad-ae00-cae5a5f8f234&xptdk=8c1257db-a909-4bad-ae00-cae5a5f8f234",
    "https://shopee.vn/B%C3%BAt-k%E1%BA%BB-m%E1%BA%AFt-Pinkflash-d%E1%BA%A1ng-l%E1%BB%8Fng-nhanh-kh%C3%B4-m%C3%A0u-%C4%91en-m%C3%A0u-n%C3%A2u-ch%E1%BA%A5t-l%C3%AC-ch%E1%BB%91ng-n%C6%B0%E1%BB%9Bc-l%C3%A2u-tr%C3%B4i-30g-i.299282693.5151439378?publish_id=&sp_atk=8718aeaf-2edf-41ca-98d0-9de781f9ba8a&xptdk=8718aeaf-2edf-41ca-98d0-9de781f9ba8a"]
crawler.get_data_from_url(urls[0])

