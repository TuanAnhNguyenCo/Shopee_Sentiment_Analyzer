from transformers import BertModel,BertTokenizer
from torch import nn
import torch
from huggingface_hub import PyTorchModelHubMixin
import os

class ReviewsClassification(nn.Module,PyTorchModelHubMixin):
    def __init__(self,n_classes = 2):
        super(ReviewsClassification,self).__init__()
        self.feature_extractor = BertModel.from_pretrained("bert-base-multilingual-cased")
        self.head = nn.Linear(768,n_classes)
    def forward(self, text_inputs):
        outputs = self.feature_extractor(**text_inputs)
        cls_token = outputs.last_hidden_state[:,0]
        y = self.head(cls_token)
        return y

# Aspect Extraction
class ABTEBert(nn.Module,PyTorchModelHubMixin):
    def __init__(self,dropout = 0.5):
        super(ABTEBert,self).__init__()
        self.feature_extractor = BertModel.from_pretrained("bert-base-multilingual-cased")
        self.head = nn.Linear(768,3)
        self.drop = nn.Dropout(dropout)
    def forward(self, ids_tensors, masks_tensors = None):
        outputs = self.feature_extractor(input_ids=ids_tensors, attention_mask=masks_tensors)
        cls_token = outputs.last_hidden_state
        y = self.head(self.drop(cls_token)) # bs,l,d
        return y.permute(0,2,1)
    
# Aspect Based Sentiment Analysis
class ABSABert(nn.Module,PyTorchModelHubMixin):
    def __init__(self,num_classes = 2):
        super(ABSABert,self).__init__()
        self.feature_extractor = BertModel.from_pretrained("bert-base-multilingual-cased")
        self.head = nn.Linear(768*2,num_classes)
    def forward(self, inputs1,inputs2):
        outputs = self.feature_extractor(**inputs1)
        cls_token1 = outputs.last_hidden_state[:,0]
        
        outputs2 = self.feature_extractor(**inputs2)
        cls_token2 = outputs2.last_hidden_state[:,0]
        
        y = self.head(torch.cat([cls_token1,cls_token2],dim = -1)) # bs,d
        return y
    

    
class ReviewsClassificationInference:
    def __init__(self,device = 'cpu',device1 = 'cpu',device2 = 'cpu'):
        if not os.path.exists('weights'):
            self.model = ReviewsClassification.from_pretrained("NCTuanAnh/shopee_reviews_cls_no_product_name").to(device)
        else:
            self.model = ReviewsClassification()
            self.model.load_state_dict(torch.load('weights/shopee_reviews_cls_no_product_name.pth',map_location = 'cpu'),strict = False)
            
            self.model.to(device)
        self.model.eval()
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
        self.idx_to_class = {
            0:'positive',
            1:'negative'
        }
        if not os.path.exists('weights'):
            self.aspect_extraction_model = ABTEBert.from_pretrained('NCTuanAnh/Aspect_Based_Term_Extraction_for_Reviews').to(device1)
        else:
            self.aspect_extraction_model = ABTEBert()
            self.aspect_extraction_model.load_state_dict(torch.load('weights/Aspect_Based_Term_Extraction_for_Reviews.pth',map_location = 'cpu'),strict = False)
            self.aspect_extraction_model.to(device1)
        self.aspect_extraction_model.eval()
        if not os.path.exists('weights'):
            self.aspect_sentiment_analysis_model = ABSABert.from_pretrained('NCTuanAnh/Aspect_Based_Sentiment_Analysis_for_Reviews').to(device2)
        else:
            self.aspect_sentiment_analysis_model = ABSABert()
            self.aspect_sentiment_analysis_model.load_state_dict(torch.load('weights/Aspect_Based_Sentiment_Analysis_for_Reviews.pth',map_location = 'cpu'),strict = False)
            self.aspect_sentiment_analysis_model.to(device2)
        self.aspect_sentiment_analysis_model.eval()
        self.device = device
        self.device1 = device1
        self.device2 = device2
    def __call__(self, comment,aspect_analysis = False):
        aspect = None
            
        if isinstance(comment,list):
            comment = [cm.lower().replace("\n",' ').replace('\r'," ") for cm in comment]
        else:
            comment = comment.lower().replace("\n",' ').replace('\r'," ")
    
        if aspect_analysis:
            aspect = []
            reviews = []
            for cm in comment:
                asp = self.__extract_aspect__(cm)
                if len(asp) != 0:
                    aspect.extend(asp)
                    reviews.extend([cm]*len(asp))
            if aspect != []:
                sentiment = self.__analyse_aspect_sentiment__(aspect,reviews)
                aspect = [[asp,stm] for asp,stm in zip(aspect,sentiment)]
        
        reviews_cls = self.__classify_reviews__(comment)
        
        
        return reviews_cls,aspect
            
            
    
    def __classify_reviews__(self,comment):
        comment = self.tokenizer(comment, return_tensors="pt",padding = True, truncation = True,max_length = 100)
        comment = {key:value.to(self.device) for key,value in comment.items()}
        with torch.no_grad():
            output = self.model(comment).argmax(dim = -1).cpu().squeeze(0).numpy().tolist()
        if isinstance(output,int):
            return [self.idx_to_class[output]]
        return [self.idx_to_class[pd] for pd in output]

    def __analyse_aspect_sentiment__(self,aspect,reviews):
        text_inputs = self.tokenizer(reviews,padding = True,truncation = True,max_length = 256,return_tensors="pt")
        aspect_inputs = self.tokenizer(aspect,padding = True,truncation = True,max_length = 256,return_tensors="pt")
        text_inputs = {key:value.to(self.device2) for key,value in text_inputs.items()}
        aspect_inputs = {key:value.to(self.device2) for key,value in aspect_inputs.items()}
        with torch.no_grad():
            output = self.aspect_sentiment_analysis_model(text_inputs,aspect_inputs).argmax(dim = -1).cpu().squeeze(0).numpy().tolist()
        if isinstance(output,int):
            return [self.idx_to_class[output]]
        return [self.idx_to_class[pd] for pd in output]
    
    def __extract_aspect__(self,comment):
        sentence = comment.split(" ")
        tag = []
        words = []
        for idx,word in enumerate(sentence):
            word = self.tokenizer.tokenize(word)
            tag.extend([idx+1]*len(word))
            words.extend(self.tokenizer.convert_tokens_to_ids(word))
        tag = torch.tensor(tag)[:512] # max 512 tokens
        words = words[:512] # max 512 tokens
        if len(words) == 0: # if sentence is "" return []
            return []
        with torch.no_grad():
            outputs = self.aspect_extraction_model(torch.tensor(words).unsqueeze(dim = 0).to(self.device1), None)
            
                
            predictions = outputs.permute(0,2,1).argmax(dim = -1).cpu()
            

        predictions = predictions[0]
        prediction = []
        for idx,word in enumerate(sentence):
            pd = predictions[idx + 1 == tag]
            if 1 in pd:
                prediction.append(1)
            elif 2 in pd:
                prediction.append(2)
            else:
                prediction.append(0)
            # get aspect
        aspect = []
        is_new_aspect = True
        k = 0
        for idx,v in enumerate(prediction):
            if not is_new_aspect:
                if v == 0:
                    aspect.append(' '.join(sentence[k:idx]))
                    is_new_aspect = True
            else:
                if v != 0:
                    k = idx
                    is_new_aspect = False            
        
        return aspect