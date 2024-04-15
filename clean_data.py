
import re
import pandas as pd
class CleanData:

    def __init__(self,abbreviation_words_file_url = 'SpecialChar/anhnct_filter.txt',save_dir = './'):
        self.emoj  = re.compile("["
            u"\U00002700-\U000027BF"  # Dingbats
            u"\U0001F600-\U0001F64F"  # Emoticons
            u"\U00002600-\U000026FF"  # Miscellaneous Symbols
            u"\U0001F300-\U0001F5FF"  # Miscellaneous Symbols And Pictographs
            u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            u"\U0001F680-\U0001F6FF"  # Transport and Map Symbols
                        "]+", re.UNICODE)
        self.abbreviation_words_file_url = abbreviation_words_file_url
        # if clean_csv function is used
        self.save_dir = save_dir

    def remove_replace_abbreviation_words(self,text):
        text = text.lower().strip() # remove space
        with open(self.abbreviation_words_file_url,'r', encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            words = line.split(',')
            if len(words) == 1:
                text = text.replace(words[0],'') # remove word
            elif len(words) == 2:
                new_w = words[1].replace('\n','')
                text = text.replace(f' {words[0]} ',f' {new_w} ')

               
        text = re.sub(' +', ' ', text)
        # remove only char
        text = ' '.join([w for w in text.split(' ') if len(w) > 1])
        return text
    def remove_special_char_replace(self,text):
        special_chars = "!@#$%^&*+-*(){}[]:;'<,>.?/\\|\"0123456789"
        for char in special_chars:
            text = text.replace(char, " ")
        return text
    def remove_emojis(self,text):
        return re.sub(self.emoj, '', text)

    def clean_text(self,text):
        text = self.remove_emojis(text)
        text = self.remove_special_char_replace(text)
        text = self.remove_replace_abbreviation_words(text)
        return text

    def clean_csv(self,csv_file_url = None):
        assert csv_file_url is not None 
        data = pd.read_csv(csv_file_url).dropna()
        data['product'] = data['product'].apply(self.clean_text)
        data['comment'] = data['comment'].apply(self.clean_text)

        data.to_csv(f"{self.save_dir}/cleaned_data.csv",
                      index=False, encoding="utf8")
    
    


clean = CleanData(abbreviation_words_file_url = 'specialchar.txt',save_dir = './')
clean.clean_csv('raw_reviews.csv')
