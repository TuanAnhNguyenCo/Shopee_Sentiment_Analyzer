from handler.chatgpt_selenium_automation import ChatGPTAutomation
import json
from itertools import dropwhile
import os


def read_json_objects_from_file(file_path):
    with open(file_path, 'r', encoding="utf8") as file:
        data = json.load(file)
    return data


file_path = 'CleanedReviews/objs_1.json'
json_objects = read_json_objects_from_file(file_path)

start_iteration = False
labeled_reviews = []
label = ""
if os.path.exists("labeled_reviews.json"):
    labeled_reviews = read_json_objects_from_file("labeled_reviews.json")
    label = labeled_reviews[-1]["input"]["comment"]
else:
    start_iteration = True


chrome_driver_path = r"F:\Downloads\chromedriver-win64\chromedriver.exe"

chrome_path = r'"F:\Downloads\chrome-win64\chrome.exe"'

chatgpt = ChatGPTAutomation(chrome_path, chrome_driver_path)

for obj in json_objects:
    if obj["comment"] == label:
        start_iteration = True
        continue
    if start_iteration == True:
        try:
            product_name = obj['product']
            comment = obj['comment']
            prompt = "Tôi cần bạn label cho tôi các câu sau cho bài toán aspect based sentiment analysis;Inputs sẽ là tên sản phẩm và bình luận về sản phẩm đó;Outputs sẽ tuần tự là Aspect Label, Aspect Tag, Sentiment Tag;Aspect Tag: 1: B-Aspect 2: I-Aspect 0: others;Sentiment Tag: 0 là positive, 1 là negative, -1 là không có gì;Kết quả sẽ là 1 json object như các ví dụ bên dưới(không lấy dấu câu như dấu , . ! ?);CHỈ CHO RA KẾT QUẢ LÀ 1 JSONOBJECT NHƯ VÍ DỤ DƯỚI VÀ KHÔNG THÊM GÌ KHÁC !!!;"+f"Input của bạn là<Tên sản phẩm>{product_name}</Tên sản phẩm>; <bình luận>{comment}</bình luận>;" + \
                "Ví dụ 1:{{input:{{comment: Máy tính thì cũ nhưng bàn phím tốt,product_name: Máy tính laptop}},output: {{word: [máy,tính,thì,cũ,nhưng,bàn,phím,tốt],aspect_tag: [1,2,0,0,0,1,2,0],sentiment_tag: [1,1,-1,-1,-1,0,0,-1],label: 1}} }}Ví dụ 2:{{input:{{comment: Đồng hồ thì xấu nhưng kim thì rất đẹp,product_name: Đồng hồ treo tường}},output: {{word: [Đồng, hồ, thì, xấu, nhưng, kim, thì, rất, đẹp],aspect_tag: [1, 2, 0, 0, 0, 1, 0, 0, 0],sentiment_tag: [1, 1, -1, -1, -1, 0, -1, -1, -1],label: 1}} }}Ví dụ 3:{{input:{{comment: Nam mô a di đà phật,product_name: máy tính Casio 580vn}},output: {{word: [Nam, mô, a, di, đà, phật],aspect_tag: [0, 0, 0, 0, 0, 0],sentiment_tag: [-1, -1, -1, -1, -1, -1],label: 0}}"
            chatgpt.send_prompt_to_chatgpt(prompt.replace("\n", ""))
            response = chatgpt.return_last_response()
            print(response)
            json_string = response[response.index('{'):response.rindex('}')+1]
            modified_string = json_string.replace("'", '"').replace(
                "'", "\'").replace("ChatGPT\n", "")
            print(modified_string)
            json_object = json.loads(modified_string)
            print(json_object)
            labeled_reviews.append({
                'input': obj,
                'output': json_object['output']
            })
        except Exception as e:
            print(e)


with open('labeled_reviews.json', 'w', encoding='utf-8') as file:
    json.dump(labeled_reviews, file, ensure_ascii=False)
