import glob

def merge_files(folder_path,file_name):
    # Đọc tất cả các tệp text trong thư mục
    all_files = glob.glob(folder_path + "*.txt")
    text = []
    for file in all_files:
        with open(file, 'r') as f:
            text.extend(f.readlines())

    # remove duplicate pair
    with open(file_name, 'w') as outfile:
        new_text = []
        for line in text:
            if line not in new_text:
                new_text.append(line)
                outfile.write(line)
   
       
    

merge_files("./SpecialChar/",'specialchar.txt')

