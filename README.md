# Introduction
<p>In this project, we have built a system that automatically crawls reviews for a product from a URL provided by the user and analyzes those reviews. Specifically, our system has two functions:  </p>
<ul>
  <li>Our system classifies reviews into two categories (positive or negative) and shows statistics on how many reviews were classified as positive and negative.  </li>
  <li>Our system extracts aspects from reviews and then classifies each aspect as positive or negative, showing statistics on the number of positive and negative mentions for each aspect. </li>
</ul>

# Folder:
<p> data: Data is stored here.</p>
<p> model: The training code and the final model for inference are placed here. </p> 
<p> utils: We put the necessary files to support running our system here. </p>

# Running
<p> 1. Edit Device Configuration: In the reviews_cls_api.py file, set the device variable to either "GPU" or "CPU" depending on the hardware available on your system.</p>
<p> 2. Run the API Server: Start the system's API by executing the following command in your terminal: ```gunicorn reviews_cls_api:app --bind 0.0.0.0:9999 --worker-class uvicorn.workers.UvicornWorker --timeout 300 ```</p>
<p> 3. Update API Endpoint: Open the utils/script.js file and modify the API endpoint URL within the fetch function to match the address and port used in the previous command (e.g., http://0.0.0.0:9999).</p>
<p> 4. Launch Web Interface: Open the index.html file and start a live server (using a tool like the Live Server extension in VS Code) to view and interact with the system's web interface.</p>

