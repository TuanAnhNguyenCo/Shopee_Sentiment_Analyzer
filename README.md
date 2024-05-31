# Thư mục:
- data: Nơi chứa dữ liệu để huấn luyện mô hình
- model: Nơi chưa mô hình cho hệ thống và các file .ipynb để huấn luyện mô hình đó
- utils: Gồm các file cần thiết để chạy hệ thống

# Cách chạy
- Sửa device trong file reviews_cls_api.py (cuda or cpu)
- Chạy hệ thống: ```gunicorn reviews_cls_api:app --bind 0.0.0.0:9999 --worker-class uvicorn.workers.UvicornWorker --timeout 300 ```
- Mở file index.html và chạy live server để chạy giao diện
