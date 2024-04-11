import pandas as pd
import glob



def merge_files(folder_path,file_name):
    # Đọc tất cả các tệp CSV trong thư mục
    all_files = glob.glob(folder_path + "*.csv")

    # Khởi tạo một danh sách rỗng để lưu trữ các DataFrame từ các tệp CSV
    dfs = []

    # Đọc từng tệp CSV và thêm vào danh sách dfs
    for file in all_files:
        df = pd.read_csv(file)
        dfs.append(df)

    # Ghép các DataFrame trong danh sách dfs thành một DataFrame duy nhất
    combined_df = pd.concat(dfs,ignore_index=True)

    # Lưu DataFrame ghép vào một tệp CSV
    combined_df.to_csv(f'./{file_name}.csv',index=False)

    print(f"Các tệp CSV trong {folder_path} đã được ghép thành công thành một tệp duy nhất.")

merge_files("./RawRating/",'reviews')
