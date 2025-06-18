"use strict";

document.querySelectorAll(".add-to-cart").forEach((button) => {
  button.addEventListener("click", function () {
    let productId = this.dataset.id;

    fetch(`/add-to-cart/?product_id=${productId}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          let quantity = data.cart[productId].quantity;
          alert(`✅ المنتج تم إضافته بنجاح! الكمية الحالية: ${quantity}`);
          window.location.href = "/cart/";
        } else {
          alert("❌ حدث خطأ أثناء الإضافة!");
        }
      })
      .catch((error) => console.error("❌ Fetch Error:", error));
  });
});

function toggleLike(productId, btn) {
  fetch(`/toggle-like/${productId}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": document
        .querySelector('meta[name="csrf-token"]')
        .getAttribute("content"),
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.liked) {
        btn.classList.add("liked");

        const likeSound = document.getElementById("likeSound");
        likeSound.currentTime = 0;
        likeSound.play();
      } else {
        btn.classList.remove("liked");
      }
    })
    .catch((error) => console.error("❌ Error:", error));
}
