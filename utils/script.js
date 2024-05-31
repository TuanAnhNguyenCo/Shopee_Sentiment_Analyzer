document
  .getElementById("show-aspect-result")
  .addEventListener("click", function () {
    if (document.getElementById("aspect-result").style.display === "grid") {
      document.getElementById("aspect-result").style.display = "none";
      document.getElementById("show-aspect-result").textContent =
        "Hiển thị phân tích khía cạnh";
    } else {
      document.getElementById("show-aspect-result").textContent =
        "Tắt hiển thị phân tích khía cạnh";
      document.getElementById("aspect-result").style.display = "grid";
    }
  });

document.getElementById("submitBtn").addEventListener("click", function () {
  const url = document.getElementById("urlInput").value;
  const aspect = document.getElementById("aspect").checked;
  if (url) {
    document.getElementById("loading").style.display = "block"; // Show the loading animation
    document.getElementById("result").style.display = "none";
    document.getElementById("show-aspect-result").style.display = "none";
    document.getElementById("aspect-result").style.display = "none";

    // fetch("http://222.252.4.232:9999/reviews_classification", {
    //fetch("http://0.0.0.0:9999/reviews_classification", {
    fetch("http://222.252.4.92:9091/reviews_classification", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": true,
      },
      body: JSON.stringify({ url: url, aspect_analysis: aspect }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        document.getElementById("submitBtn").disabled = false;
        document.getElementById("loading").style.display = "none"; // Hide the loading animation
        document.getElementById("result").style.display = "block";
        const resultDiv = document.getElementById("result");
        resultDiv.innerHTML = `
                  <p>Tên sản phẩm: ${data.product_name}</p>
                  <p>Số lượng bình luận tích cực: ${data.positive} / ${data.total}</p>
                  <p>Số lượng bình luận tiêu cực: ${data.negative} / ${data.total}</p>
              `;
        if (aspect) {
          document.getElementById("show-aspect-result").style.display = "block";
          const aspectResultDiv = document.getElementById("aspect-result");
          aspectResultDiv.innerHTML = `<div class="grid-item">Tên khía cạnh</div><div class="grid-item">Số lượng đánh giá tích cực</div><div class="grid-item">Số lượng đánh giá tiêu cực</div>`;
          for (let key in data.aspects) {
            if (data.aspects.hasOwnProperty(key)) {
              const aspectKeyElement = document.createElement("div");
              const aspectPositiveElement = document.createElement("div");
              const aspectNegativeElement = document.createElement("div");
              aspectKeyElement.className = "grid-item";
              aspectKeyElement.textContent = `${key}`;
              aspectPositiveElement.className = "grid-item";
              aspectPositiveElement.textContent = `${data.aspects[key][0]}`;
              aspectNegativeElement.className = "grid-item";
              aspectNegativeElement.textContent = `${data.aspects[key][1]}`;
              aspectResultDiv.appendChild(aspectKeyElement);
              aspectResultDiv.appendChild(aspectPositiveElement);
              aspectResultDiv.appendChild(aspectNegativeElement);
            }
          }
        }

        // Calculate the ratio and display the appropriate gif
        const ratio = (data.positive / data.negative) * 100;
        const gifUrl =
          ratio > 90
            ? "https://i.pinimg.com/originals/fa/e0/6b/fae06b7a7bafadcc2f69d4849a202973.gif"
            : "https://i.pinimg.com/originals/e2/95/93/e295933f3ea7b57c3754c307320f2430.gif";

        const gifElement = document.createElement("img");
        gifElement.src = gifUrl;
        gifElement.alt = ratio > 90 ? "Positive Feedback" : "Negative Feedback";
        gifElement.width = 300; // Set the width of the gif
        resultDiv.appendChild(gifElement);
      })
      .catch((error) => {
        document.getElementById("submitBtn").disabled = false;
        document.getElementById("loading").style.display = "none"; // Hide the loading animation
        document.getElementById("result").innerText = `Lỗi: ${error.message}`;
      });
  } else {
    document.getElementById("result").innerText = "Vui lòng nhập đường dẫn";
  }
});
