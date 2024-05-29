document.getElementById("submitBtn").addEventListener("click", function () {
  const url = document.getElementById("urlInput").value;
  if (url) {
    document.getElementById("loading").style.display = "block"; // Show the loading animation

    fetch("http://222.252.4.232:9999/reviews_classification", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url: url }),
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

        const resultDiv = document.getElementById("result");
        resultDiv.innerHTML = `
                  <p>Tên sản phẩm: ${data.product_name}</p>
                  <p>Số lượng bình luận tích cực: ${data.positive} / ${data.total}</p>
                  <p>Số lượng bình luận tiêu cực: ${data.negative} / ${data.total}</p>
              `;

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
