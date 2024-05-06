import re
import json
import requests
import pandas as pd
from tqdm.auto import tqdm
from clean_data import CleanData

# khi chạy code cần login shopee lấy cookies thay vào phần cookie
# truy cập link https://shopee.vn/api/v2/item/get_ratings?filter=0&flag=1&itemid=11424337247&limit=20&offset=0&shopid=39682649&type=0
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
        self.clean = CleanData(
            abbreviation_words_file_url='specialchar.txt', save_dir='./')

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
        good_rating = 0
        bad_rating = 0
        try:
            for offset in tqdm(range(20, self.max_reviews_per_product+1, 20)):
                data = requests.get(
                    self.ratings_url.format(
                        shop_id=self.shop_id, item_id=self.item_id, offset=offset), headers=headers).json()
                for i, rating in enumerate(data["data"]["ratings"], 1):
                    if rating["rating_star"] >= 4 and good_rating < 20:
                        good_rating += 1
                        self.data.append([
                            self.clean.clean_text(
                                data['data']['ratings'][0]['original_item_info']['name']),
                            rating["author_username"],
                            rating["rating_star"],
                            self.clean.clean_text(rating["comment"])])
                    if rating["rating_star"] < 3 and bad_rating < 20:
                        bad_rating += 1
                        self.data.append([
                            self.clean.clean_text(
                                data['data']['ratings'][0]['original_item_info']['name']),
                            rating["author_username"],
                            rating["rating_star"],
                            self.clean.clean_text(rating["comment"])])
                    if good_rating == 20 and bad_rating == 20:
                        break
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
    400, 'G:\Projects\Reviews_classification\RawRating')
urls = ["https://shopee.vn/%C4%90%C3%A8n-Tr%E1%BB%A3-S%C3%A1ng-xe-ma%CC%81y-xe-%C4%91i%E1%BB%87n-%C4%91%C3%A8n-bi-c%E1%BA%A7u-mini-bi-C%E1%BA%A7u-%C4%91e%CC%80n-pha-bi-ca%CC%82%CC%80u-xe-ma%CC%81y-2-M%C3%A0u-Cos-v%C3%A0ng-Pha-tr%E1%BA%AFng-i.229294463.22962381648?sp_atk=b41f1c2b-28fe-4fb7-9fbc-ffbaa0621b0a&xptdk=b41f1c2b-28fe-4fb7-9fbc-ffbaa0621b0a",
        "https://shopee.vn/%C4%90%C3%A8n-tr%E1%BB%A3-s%C3%A1ng-l4-Ng%E1%BA%AFn.-t%E1%BA%B7ng-k%C3%A8m-c%C3%B4ng-t%E1%BA%AFc-%E1%BB%91c-g%C6%B0%C6%A1ng-i.82786224.7574853946?sp_atk=5c7cb885-ef3f-4f5d-9c09-eb26cb9c304a&xptdk=5c7cb885-ef3f-4f5d-9c09-eb26cb9c304a",
        "https://shopee.vn/%C4%90%C3%A8n-LED-Xi-nhan-%C4%90%C3%A8n-L%C3%B9i-Ch%C3%A2n-T15-T10-Cho-%C3%94-t%C3%B4-Xe-m%C3%A1y-Ch%C3%ADp-4014-Si%C3%AAu-s%C3%A1ng-15w-i.125611244.19022657474?sp_atk=45b34bdb-2bb6-4738-a6b9-645e4f638204&xptdk=45b34bdb-2bb6-4738-a6b9-645e4f638204",
        "https://shopee.vn/%C4%90%C3%A8n-Led-Nh%C3%A1y-H%E1%BA%ADu-Audi-H%C3%A0ng-X%E1%BB%8Bn-L%E1%BA%AFp-M%E1%BB%8Di-D%C3%B2ng-Xe-M%C3%A1y-Wave-Dream-Win-..-Xe-%C4%90i%E1%BB%87n-i.1071218497.21396052704?sp_atk=591c8cd3-4772-4a11-8a83-76d4c7e3ef2d&xptdk=591c8cd3-4772-4a11-8a83-76d4c7e3ef2d",
        "https://shopee.vn/N%C3%B3n-b%E1%BA%A3o-hi%E1%BB%83m-l%C6%B0%E1%BB%A1i-trai-Vespa-cao-c%E1%BA%A5p-M%C5%A9-b%E1%BA%A3o-hi%E1%BB%83m-n%C3%B3n-k%E1%BA%BFt-c%C3%A1-t%C3%ADnh-v%C3%A0-sang-tr%E1%BB%8Dng-d%C3%A0nh-cho-c%E1%BA%A3-nam-v%C3%A0-n%E1%BB%AF-i.620451827.19892594482?sp_atk=9fe9c9d9-7868-4117-a18d-2e1524f72447&xptdk=9fe9c9d9-7868-4117-a18d-2e1524f72447",
        "https://shopee.vn/%E1%BB%90c-Titan-Gr5-%E1%BB%90c-Salaya-6li10-GI%C3%81-R%E1%BA%BA-G%E1%BA%AFn-N%C3%B3n-S%C6%A1n-G%E1%BA%AFn-Xe-C%E1%BB%B1c-%C4%90%E1%BA%B9p-i.919061854.17597699598?sp_atk=8387ec75-1841-4ebb-8e4a-f38bd9c1a500&xptdk=8387ec75-1841-4ebb-8e4a-f38bd9c1a500",
        "https://shopee.vn/bao-tay-tay-n%E1%BA%AFm-daytona-t%E1%BA%B7ng-g%C3%B9-xi-m%E1%BA%ABu-th%C3%A1i-qu%C3%A1-r%E1%BA%BB-g%E1%BA%AFn-m%E1%BB%8Di-lo%E1%BA%A1i-xe-i.171651588.12476475612?sp_atk=834ee466-4301-4f15-924a-b9ae24a07ac5&xptdk=834ee466-4301-4f15-924a-b9ae24a07ac5",
        "https://shopee.vn/N%C3%B3n-B%E1%BA%A3o-Hi%E1%BB%83m-Nhi%E1%BB%81u-M%C3%A0u-Gi%C3%A1-R%E1%BA%BB-S%C6%A1n-Nh%C3%A1m-H%E1%BB%99p-Tem-Mac-%C4%90%E1%BA%A7y-%C4%90%E1%BB%A7-i.393971263.13765995112?sp_atk=4d2f7077-0f41-4382-8e9c-bcc50bfe1b41&xptdk=4d2f7077-0f41-4382-8e9c-bcc50bfe1b41",
        "https://shopee.vn/M%C5%A9-B%E1%BA%A3o-Hi%E1%BB%83m-N%E1%BB%ADa-%C4%90%E1%BA%A7u-1-2-Nhi%E1%BB%81u-Tem-Si%C3%AAu-HOT-H%C3%A0ng-Ch%C3%ADnh-H%C3%A3ng-Cao-C%E1%BA%A5p-%C4%90%E1%BB%A7-Tem-CR-Ki%E1%BB%83m-%C4%90%E1%BB%8Bnh-Tem-C%C3%B4ng-Ty-i.14616559.4137217113?sp_atk=40d27ea0-a644-4fe9-9e49-2313f46d0938&xptdk=40d27ea0-a644-4fe9-9e49-2313f46d0938",
        "https://shopee.vn/%C4%90%C3%A8n-Pha-Led-Bi-C%E1%BA%A7u-T9-Pro-mQ-LED-H4-B%E1%BA%A3n-2024-(-Ko-L%E1%BA%AFp-%C4%90i%E1%BB%87n-M%C3%A1y-)-Cho-Xe-M%C3%A1y-M01B-i.19883040.2026090810?sp_atk=f862c8c2-bc5c-4077-a2e9-41c7ef7b24d6&xptdk=f862c8c2-bc5c-4077-a2e9-41c7ef7b24d6",
        "https://shopee.vn/-Combo-%C4%90%C3%A8n-Tr%E1%BB%A3-S%C3%A1ng-L4x-Lo%E1%BA%A1i-T%E1%BB%91t-1-ch%E1%BA%BF-%C4%91%E1%BB%99-i.179904488.7879607600?sp_atk=523de5c6-dd3c-4729-86e8-6f7ac9214449&xptdk=523de5c6-dd3c-4729-86e8-6f7ac9214449",
        "https://shopee.vn/M%C5%A9-b%E1%BA%A3o-hi%E1%BB%83m-n%E1%BB%ADa-%C4%91%E1%BA%A7u-Napoli-Bosozoku-Japan-Style-n%E1%BB%ADa-%C4%91%E1%BA%A7u-vintage-M%C5%A9-b%E1%BA%A3o-hi%E1%BB%83m-moto-Vintage-1-2-%C4%91%E1%BA%A7u-t%E1%BA%B7ng-k%C3%A8m-sticker-JP-i.391641034.23567830483?sp_atk=2237f670-81e9-4aa2-bc70-f82e873998ff&xptdk=2237f670-81e9-4aa2-bc70-f82e873998ff",
        "https://shopee.vn/N%C3%B3n-ba%CC%89o-hi%C3%AA%CC%89m-g%E1%BA%AFn-%E1%BB%91c-titan-gr5-T%E1%BA%B6NG-TEM-BIKER-M%C5%A9-b%E1%BA%A3o-hi%C3%AA%CC%89m-n%C6%B0%CC%89a-%C4%91%E1%BA%A7u-7-%C3%B4%CC%81c-Titan-phu%CC%89-bo%CC%81ng-nano-nhi%C3%AA%CC%80u-ma%CC%80u-i.919061854.17293070811?sp_atk=c66f7b9e-f907-496b-b63d-7d0ff384b918&xptdk=c66f7b9e-f907-496b-b63d-7d0ff384b918",
        "https://shopee.vn/M%C5%A9-B%E1%BA%A3o-Hi%E1%BB%83m-N%E1%BB%ADa-%C4%90%E1%BA%A7u-1-2-Nhi%E1%BB%81u-Tem-Si%C3%AAu-HOT-H%C3%A0ng-Ch%C3%ADnh-H%C3%A3ng-Cao-C%E1%BA%A5p-%C4%90%E1%BB%A7-Tem-CR-Ki%E1%BB%83m-%C4%90%E1%BB%8Bnh-Tem-C%C3%B4ng-Ty-i.14616559.4137217113?sp_atk=9096578d-da12-4fd7-af07-902e3155fd14&xptdk=9096578d-da12-4fd7-af07-902e3155fd14",
        "https://shopee.vn/%C4%90%C3%A8n-Pha-Led-Bi-C%E1%BA%A7u-T9-Pro-mQ-LED-H4-B%E1%BA%A3n-2024-(-Ko-L%E1%BA%AFp-%C4%90i%E1%BB%87n-M%C3%A1y-)-Cho-Xe-M%C3%A1y-M01B-i.19883040.2026090810?sp_atk=d444a8bb-5c9a-4551-9637-60d56554ac52&xptdk=d444a8bb-5c9a-4551-9637-60d56554ac52",
        "https://shopee.vn/Tai-m%C3%A8o-Hoa-S%E1%BB%ABng-nh%E1%BB%8F-Chong-ch%C3%B3ng-g%E1%BA%AFn-m%C5%A9-b%E1%BA%A3o-hi%E1%BB%83m-g%E1%BA%AFn-xe-m%C3%A1y-g%E1%BA%AFn-%C3%B4-t%C3%B4-ph%E1%BB%A5-ki%E1%BB%87n-xe-trang-tr%C3%AD-b%C3%A0n-h%E1%BB%8Dc-si%C3%AAu-cute-T%E1%BA%B7ng-keo-i.381179915.17296441518?sp_atk=d1e76c30-0271-4ce4-a81a-595e0e948220&xptdk=d1e76c30-0271-4ce4-a81a-595e0e948220",
        "https://shopee.vn/M%C5%A9-B%E1%BA%A3o-Hi%E1%BB%83m-N%E1%BB%ADa-%C4%90%E1%BA%A7u-M%C3%A0u-%C4%90en-Nh%C3%A1m-K%C3%A8m-K%C3%ADnh-Th%E1%BB%9Di-Trang-T%C3%B9y-Ch%E1%BB%8Dn-Theo-Ph%C3%A2n-Lo%E1%BA%A1i-i.417316466.14902386964?sp_atk=a49d0e3a-9994-44e7-9745-925c6b22e648&xptdk=a49d0e3a-9994-44e7-9745-925c6b22e648",
        "https://shopee.vn/(750ml-%E2%80%93-CH%E1%BB%8CN-M%C3%80U)-B%C3%ACnh-N%C6%B0%E1%BB%9Bc-Xe-%C4%90%E1%BA%A1p-Th%E1%BB%83-Thao-750ml-H%C3%A0ng-Chu%E1%BA%A9n-i.166962170.13159309492?sp_atk=0ad0ed04-aa1a-4da4-897f-b63c58923877&xptdk=0ad0ed04-aa1a-4da4-897f-b63c58923877",
        "https://shopee.vn/BI-S%E1%BA%AET-6.35MM-V%C3%80-7MM-C%C3%81C-T%C3%9AI-100VIEN-200VIEN-500VIEN-D%C3%99NG-TRONG-M%C3%81Y-M%C3%93C-S%E1%BB%ACA-CH%E1%BB%AEA-%E1%BB%94-TR%E1%BB%A4C-B%C3%81NH-XE-%C4%90%E1%BA%A0P-XE-M%C3%81Y-i.484258176.11835992337?sp_atk=d0a71b6c-456a-4c40-abb5-5654c75b0828&xptdk=d0a71b6c-456a-4c40-abb5-5654c75b0828",
        "https://shopee.vn/B%E1%BB%99-c%C3%B9m-c%C3%B4ng-t%E1%BA%AFc-Fz-hai-b%C3%AAn-(C%C3%B3-b%C3%A1n-l%E1%BA%BB)-i.82786224.3929136914?sp_atk=61c420c2-962f-4fb5-8ca2-c5723985fa63&xptdk=61c420c2-962f-4fb5-8ca2-c5723985fa63"]
crawler.get_data_from_urls(urls)
