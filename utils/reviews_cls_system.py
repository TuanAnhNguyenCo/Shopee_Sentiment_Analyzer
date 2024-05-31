import re
import json
import requests
import pandas as pd
from tqdm.auto import tqdm
from utils.clean_data import CleanData
import requests
import sys
from model.model import ReviewsClassificationInference
from collections import defaultdict 

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



class Reviews_CLS_System:
    def __init__(self,device = 'cpu',device1 = 'cpu',device2 = 'cpu',bs = 4):

        self.bs = bs
        self.clean = CleanData(
            abbreviation_words_file_url='utils/specialchar.txt', save_dir='./')
        self.pipeline = ReviewsClassificationInference(device,device1,device2)

    def get_rating_urls(self, url):
        r = re.search(r"i\.(\d+)\.(\d+)", url)
        self.shop_id, self.item_id = r[1], r[2]
        self.ratings_url = "https://shopee.vn/api/v4/item/get_ratings?filter=0&flag=6&itemid={item_id}&limit=59&offset={offset}&shopid={shop_id}&type=0"

    def get_data_and_predict_from_url(self, url,aspect_analysis):
        self.data = []
        self.ratings_url = None
        self.get_rating_urls(url)
        positive = 0
        negative = 0
        total = 0
        cmts = []
        comments = []
        i = 0
        raw_reviews = []
        product_name = None


        def check_exist(comment):
            for obj in cmts:
                if obj == comment:
                    return True
            return False
        
        assert self.ratings_url is not None
        try:
            data = requests.get(
                    self.ratings_url.format(
                        shop_id=self.shop_id, item_id=self.item_id, offset="1"), headers=headers).json()
            max_offsetId = int(data["data"]["item_rating_summary"]["rcount_with_context"]/59)
    
            for offset in tqdm(range(0,max_offsetId+1)): # max max_offsetId*59 comments
                data = requests.get(
                    self.ratings_url.format(
                        shop_id=self.shop_id, item_id=self.item_id, offset=offset*59), headers=headers).json()
                for i, rating in enumerate(data["data"]["ratings"], 1):
                    if rating["comment"] == "" :
                        i+=1
                        continue
                    comment = self.clean.clean_text(rating["comment"]) 
                    if not check_exist(comment):
                        raw_reviews.append(rating["comment"])
                        product_name = data['data']['ratings'][0]['original_item_info']['name']
                        comments.append([
                            self.clean.clean_text(
                                data['data']['ratings'][0]['original_item_info']['name']),
                            rating["author_username"],
                            rating["rating_star"],
                            self.clean.clean_text(rating["comment"])])
                        cmts.append(comment)
                        
        
        except Exception as ex:
            print(ex)
            pass
        print('*'*15,"CRAWLING REVIEWS: DONE!",'*'*15)
        print('*'*15,"PREDICTING REVIEWS: STARTING!",'*'*15)
        print(i)
        detail_info= []
        aspects = defaultdict(lambda: [0,0]) 
        if len(cmts) != 0 :
            bs = self.bs
            total = len(cmts)
            j = 0
            posi_cmt = []
            nega_cmt = []
            for index in range(0,len(cmts),bs):
                sys.stdout.write(f"\rProgress: {min(index+bs,total)}/{total}")
                sys.stdout.flush()
                
                results,aspect = self.pipeline(comment =  cmts[index:index+bs],aspect_analysis = aspect_analysis)
                if aspect is not None:
                    for asp in aspect:
                        position = 0 if asp[1] == 'positive' else 1
                        aspects[asp[0]][position] +=1
                        
                
                label = 0
                for o in results:
                    if o == 'positive':
                        posi_cmt.append(comments[j])
                        positive +=1
                        detail_info.append(1)
                    elif o == 'negative':
                        nega_cmt.append(comments[j])
                        negative += 1
                        detail_info.append(0)
                    j+=1

            # df = pd.DataFrame(posi_cmt, columns=[
            #                 'product', 'username', 'rating', 'comment'])
            # df.to_csv(f"./positive.csv",
            #         index=False, encoding="utf8")
            # df = pd.DataFrame(nega_cmt, columns=[
            #         'product', 'username', 'rating', 'comment'])
            # df.to_csv(f"./negative.csv",
            #         index=False, encoding="utf8")
        return positive,negative,total,detail_info,raw_reviews,product_name,aspects
        
    def __call__(self,url,aspect_analysis):
        positive,negative,total,detail_info,raw_reviews,product_name,aspects = self.get_data_and_predict_from_url(url,aspect_analysis)
        return {
            'positive':positive,
            'negative':negative,
            'total':total,
            # 'detail_info':detail_info,
            # 'raw_reviews':raw_reviews,
            'product_name':product_name,
            'aspects':aspects
        }


pipeline = Reviews_CLS_System()
# pipeline('https://shopee.vn/%C3%81o-Ph%C3%B4ng-n%E1%BB%AF-ph%E1%BB%91i-Tay-K%E1%BA%BB-Unisex-Cotton-from-r%E1%BB%99ng-%C4%91%E1%BA%B9p-tho%E1%BA%A3i-m%C3%A1i-tr%E1%BA%BB-trung-i.885073589.22426271001?sp_atk=c012fd3d-650e-468d-afa5-fb47c8fe3bef&xptdk=c012fd3d-650e-468d-afa5-fb47c8fe3bef')

