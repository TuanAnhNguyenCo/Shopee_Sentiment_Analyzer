document.getElementById("submitBtn").addEventListener("click", function () {
    const url = document.getElementById("urlInput").value;
    if (url) {
      fetch("http://222.252.4.232:9999/reviews_classification", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: url }),
      })
        .then((response) => response.json())
        .then((data) => {
          const resultDiv = document.getElementById("result");
  
          resultDiv.innerHTML = `
          <p>Tên sản phẩm: ${data.product_name}</p>
          <p>Số lượng bình luận tích cực: ${data.positive} / ${data.total}</p>
          <p>Số lượng bình luận tiêu cực: ${data.negative} / ${data.total}</p>
              `;
        })
        .catch((error) => {
          document.getElementById("result").innerText = "Lỗi: ${error}";
        });
    } else {
      document.getElementById("result").innerText = "Vui lòng nhập đường dẫn";
    }
  });