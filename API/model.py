from transformers import BertModel,BertTokenizer
from torch import nn
import torch
from huggingface_hub import PyTorchModelHubMixin

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
    
class ReviewsClassificationInference:
    def __init__(self,device = 'cpu'):
        self.model = ReviewsClassification.from_pretrained("NCTuanAnh/shopee_reviews_cls_no_product_name").to(device)
        self.model.eval()
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
        self.idx_to_class = {
            0:'positive',
            1:'negative'
        }
        self.device = device
    def __call__(self, comment):
        comment = comment.split('-----')
        if isinstance(comment,list):
            comment = [cm.lower().replace("\n",' ').replace('\r'," ") for cm in comment]
        else:
            comment = comment.lower().replace("\n",' ').replace('\r'," ")
        comment = self.tokenizer(comment, return_tensors="pt",padding = True, truncation = True,max_length = 100)
        comment = {key:value.to(self.device) for key,value in comment.items()}
        output = self.model(comment).argmax(dim = -1).cpu().squeeze(0).numpy().tolist()
        if isinstance(output,int):
            return self.idx_to_class[output]
        return '-----'.join([self.idx_to_class[pd] for pd in output])
