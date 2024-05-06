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
                        bad_rating +=1
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
    4000, './')
urls = [
   ' https://shopee.vn/G%C4%83ng-Tay-H%E1%BB%9F-2-Ng%C3%B3n-Ch%E1%BB%91ng-N%E1%BA%AFng-C%C3%B3-Th%E1%BB%83-S%E1%BB%AD-D%E1%BB%A5ng-C%E1%BA%A3m-%E1%BB%A8ng-%C4%90i%E1%BB%87n-Tho%E1%BA%A1i-i.151237226.18677901248?sp_atk=e4adac21-b24b-49aa-9101-50392fddeb58&xptdk=e4adac21-b24b-49aa-9101-50392fddeb58',
'    https://shopee.vn/B%C3%BAt-M%C3%A0u-Acrylic-Marker-12-24-36-48-60-Cao-C%E1%BA%A5p-M%C3%A0u-S%E1%BA%AFc-T%C6%B0%C6%A1i-S%C3%A1ng-B%C3%BAt-L%C3%B4ng-M%C3%A0u-i.295556635.25001096469?sp_atk=bf64c302-6fca-46eb-bba2-4514f15783ff&xptdk=bf64c302-6fca-46eb-bba2-4514f15783ff',
   ' https://shopee.vn/%C3%94-d%C3%B9-che-m%C6%B0a-%C4%91i-n%E1%BA%AFng-Sumio-12-nan-8-nan-m%E1%BB%9F-t%E1%BB%B1-%C4%91%E1%BB%99ng-g%E1%BA%A5p-nh%E1%BB%8F-g%E1%BB%8Dn-c%E1%BA%A7m-tay-2-chi%E1%BB%81u-%C4%91i-du-l%E1%BB%8Bch-c%E1%BB%A1-l%E1%BB%9Bn-to-cho-%C3%B4-t%C3%B4-xe-h%C6%A1i-i.2630589.10686216949?sp_atk=8abd4651-bfe1-4fb2-8f96-145efab837ba&xptdk=8abd4651-bfe1-4fb2-8f96-145efab837ba',
'    https://shopee.vn/Dao-C%E1%BA%AFt-Washi-Tape-T%E1%BB%89a-Sticker-D%E1%BB%A5ng-C%E1%BB%A5-D%C3%A1n-Bullet-Journal-Ti%E1%BB%87n-L%E1%BB%A3i-K%C3%A8m-6-L%C6%B0%E1%BB%A1i-Dao-BEYOU-i.284175510.22645663774?sp_atk=9bbcced3-6594-4b42-9d11-1ac597173aa7&xptdk=9bbcced3-6594-4b42-9d11-1ac597173aa7',
'    https://shopee.vn/PAPAOZHU-H%C3%ACnh-X%C4%83m-D%C3%A1n-T%E1%BA%A1m-Th%E1%BB%9Di-Ch%E1%BB%91ng-N%C6%B0%E1%BB%9Bc-L%C3%A2u-Tr%C3%B4i-H%C3%ACnh-M%E1%BA%B7t-Tr%C4%83ng-Ng%C3%B4i-Sao-C%C3%A1-T%C3%ADnh-Cho-Nam-V%C3%A0-N%E1%BB%AF-Paozhu-Ins-i.255856218.22038189687?sp_atk=9180c7f0-aa1c-4ad4-b9a8-4371e554268a&xptdk=9180c7f0-aa1c-4ad4-b9a8-4371e554268a',
'    https://shopee.vn/B%C3%BAt-Gel-MEKI-B%C3%BAt-Bi-N%C6%B0%E1%BB%9Bc-M%E1%BB%B1c-Gel-%C4%90en-Xanh-%C4%90%E1%BB%8F-Kh%C3%B4-Nhanh-Ng%C3%B2i-0.5mm-M%E1%BB%B1c-%C4%90%E1%BB%81u-N%C3%A9t-Ch%E1%BB%AF-%C4%90%E1%BA%B9p-%C4%90%E1%BB%A7-M%C3%A0u-i.1025748374.23973625035?sp_atk=7af011af-d6bc-4737-b009-c2842ea99b1a&xptdk=7af011af-d6bc-4737-b009-c2842ea99b1a',
'    https://shopee.vn/-Chuy%C3%AAn-B%C3%BAt-B%C3%BAt-Gel-b%C3%BAt-bi-n%C6%B0%E1%BB%9Bc-v%C4%83n-ph%C3%B2ng-B%C3%BAt-ch%C3%A9p-kinh-m%E1%BB%B1c-gel-0.5mm-m%E1%BB%B1c-%C4%91%E1%BB%81u-n%C3%A9t-ch%E1%BB%AF-%C4%91%E1%BA%B9p-%C4%91%E1%BB%A7-m%C3%A0u-xanh-%C4%91en-%C4%91%E1%BB%8F-i.1076210029.16696534146?sp_atk=c4e11e23-ee9a-436e-9136-1347efbde8fb&xptdk=c4e11e23-ee9a-436e-9136-1347efbde8fb',
'    https://shopee.vn/-M%C3%A3-FATREND65-gi%E1%BA%A3m-%C4%91%E1%BA%BFn-50k-%C4%91%C6%A1n-t%E1%BB%AB-150k-Qu%E1%BA%A7n-T%E1%BA%A5t-T%C3%A0ng-H%C3%ACnh-Che-Khuy%E1%BA%BFt-%C4%90i%E1%BB%83m-Thon-G%E1%BB%8Dn-Ch%C3%A2n-Cao-C%E1%BA%A5p-BEBECHIC-i.714557060.22514539268?sp_atk=cc3fbca6-27ac-4da1-a117-e3016c335bde&xptdk=cc3fbca6-27ac-4da1-a117-e3016c335bde',
'    https://shopee.vn/-M%C3%A3-CLS2404B-gi%E1%BA%A3m-30k-%C4%91%C6%A1n-99k-Set-10-50-Sticker-D%C3%A1n-Xe-H%C6%A1i-H%C3%ACnh-M%C3%A8o-S%C3%A1ng-T%E1%BA%A1o-i.972083861.18877788902?sp_atk=04a2b08c-73be-48a5-9a45-e1e6332c7706&xptdk=04a2b08c-73be-48a5-9a45-e1e6332c7706',
'    https://shopee.vn/D%C3%A2y-chuy%E1%BB%81n-MAYEBE-LAVEND-B%E1%BA%A1c-Phong-C%C3%A1ch-Punk-%C4%90%C6%A1n-Gi%E1%BA%A3n-i.130184653.8733115525?sp_atk=357de34c-dcad-463f-a0e7-e5888ef306b9&xptdk=357de34c-dcad-463f-a0e7-e5888ef306b9',
    'https://shopee.vn/Tr%C3%A2m-C%C3%A0i-T%C3%B3c-Tua-Rua-Hoa-Phong-C%C3%A1ch-C%E1%BB%95-%C4%90i%E1%BB%83n-Cao-C%E1%BA%A5p-Cho-N%E1%BB%AF-zhang-qipao-i.607980775.20295645515?sp_atk=843e3f09-4877-47cc-9422-e6ac120508ec&xptdk=843e3f09-4877-47cc-9422-e6ac120508ec',
    'https://shopee.vn/S%C3%A9t-5-%C4%90%C3%B4i-T%E1%BA%A5t-N%E1%BB%AF-Cao-C%E1%BB%95-H%E1%BB%8Da-Ti%E1%BA%BFt-G%E1%BA%A5u-D%C3%A2u-T%C3%A2y-M%C3%A0u-H%E1%BB%93ng-D%E1%BB%85-Th%C6%B0%C6%A1ng-Tcc5-i.17330949.19178093457?sp_atk=a7a3c1dc-58cb-4be0-bba3-e7db61479b16&xptdk=a7a3c1dc-58cb-4be0-bba3-e7db61479b16',
    'https://shopee.vn/M%E1%BA%AFt-k%C3%ADnh-n%E1%BB%AF-nam-gi%E1%BA%A3-c%E1%BA%ADn-ch%E1%BB%AF-V-r%C3%A2m-m%C3%A1t-ch%E1%BB%91ng-tia-UV-g%E1%BB%8Dng-k%C3%ADnh-c%E1%BA%ADn-th%E1%BB%9Di-trang-phong-c%C3%A1ch-H%C3%A0n-Qu%E1%BB%91c-ABICA-017-i.341024473.8655779569?sp_atk=464cd69f-0679-4c6b-b42e-ce339a6d93a7&xptdk=464cd69f-0679-4c6b-b42e-ce339a6d93a7',
    'https://shopee.vn/M%C5%A9-l%C6%B0%E1%BB%A1i-trai-Mlb-La-Fitted-m%C3%A0u-xanh-d%C6%B0%C6%A1ng-%C4%91%E1%BA%ADm-phong-c%C3%A1ch-hip-hop-c%C3%A1-t%C3%ADnh-i.734592238.19380767185?sp_atk=6a2a8f30-a4f2-4d40-b3d8-2271c2183036&xptdk=6a2a8f30-a4f2-4d40-b3d8-2271c2183036',
    'https://shopee.vn/B%C4%83ng-%C4%91%C3%B4-r%E1%BB%ADa-m%E1%BA%B7t-tai-th%E1%BB%8F-tai-m%C3%A8o-d%E1%BB%83-th%C6%B0%C6%A1ng-ti%E1%BB%87n-d%E1%BB%A5ng-phong-c%C3%A1ch-h%C3%A0n-qu%E1%BB%91c-i.1270348.9475079498?sp_atk=3577597d-8441-47cd-93d2-3b79960b10e9&xptdk=3577597d-8441-47cd-93d2-3b79960b10e9',
    'https://shopee.vn/SET-12-K%E1%BA%B9p-C%C3%A0ng-Cua-Nh%E1%BB%B1a-Trong-Su%E1%BB%91t-Cao-C%E1%BA%A5p-i.225214701.7935576979?sp_atk=3c00e51f-1110-4c1b-b49d-d34786f34fb9&xptdk=3c00e51f-1110-4c1b-b49d-d34786f34fb9',
    'https://shopee.vn/K%E1%BA%B9p-t%C3%B3c-c%C3%A0ng-cua-trong-su%E1%BB%91t-3-r%C4%83ng-5-r%C4%83ng-H%C3%A0n-Qu%E1%BB%91c-n%E1%BB%AF-%C4%91%E1%BA%B9p-hottrend-2023-iLita-C%E1%BA%B7p-b%C3%BAi-c%C3%A0o-t%C3%B3c-d%E1%BB%85-th%C6%B0%C6%A1ng-m%C3%A0u-%C4%91en-i.381825931.14637282496?sp_atk=ef4bf627-f494-4d59-a472-be7b0fbe4dfe&xptdk=ef4bf627-f494-4d59-a472-be7b0fbe4dfe',
    'https://shopee.vn/K%C3%ADnh-M%C3%A1t-Ph%C3%A2n-C%E1%BB%B1c-Phong-C%C3%A1ch-H%C3%A0n-Qu%E1%BB%91c-Th%E1%BB%9Di-Trang-Cho-Nam-V%C3%A0-N%E1%BB%AF-i.1006220775.20094869794?sp_atk=bc5d3cba-deba-4e0b-82b3-f832f3f7689f&xptdk=bc5d3cba-deba-4e0b-82b3-f832f3f7689f',
    'https://shopee.vn/Ghim-C%C3%A0i-Qu%E1%BA%A7n-%C3%81o-Ch%C3%A2n-V%C3%A1y-%C4%90%C3%ADnh-Ng%E1%BB%8Dc-Trai-Ch%E1%BB%91ng-Tr%C6%B0%E1%BB%A3t-Ti%E1%BB%87n-D%E1%BB%A5ng-i.309528275.21961474255?sp_atk=9edb0881-a2e2-419e-81ba-f5e4fc47547d&xptdk=9edb0881-a2e2-419e-81ba-f5e4fc47547d',
    'https://shopee.vn/2024-Ph%E1%BB%A5-Ki%E1%BB%87n-T%C3%B3c-M%E1%BB%9Bi-Cho-N%E1%BB%AF-K%E1%BA%B9p-T%C3%B3c-Hoa-%C4%90%E1%BA%B9p-i.492618660.24166359433?sp_atk=4075769e-78ac-4fbc-8104-6bf40b466682&xptdk=4075769e-78ac-4fbc-8104-6bf40b466682'
]

crawler.get_data_from_urls(urls)
