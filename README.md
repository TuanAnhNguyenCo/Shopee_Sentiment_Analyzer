# Reviews_classification

- Run python3 merge_csv_files.py to merge all files into one
- Run python3 filter_reviews.py to filter low and high rating
- Run python3 crawl_shopee_reviews.py to crawl reviews from shopee

# Run model api
- cd API
- gunicorn reviews_cls_api:app --bind 0.0.0.0:9999 --worker-class uvicorn.workers.UvicornWorker --timeout 300