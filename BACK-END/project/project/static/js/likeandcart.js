"use strict";

function addToCart(productId) {
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
}

function toggleLike(productId, btn, event) {
  event.preventDefault();

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
      } else {
        btn.classList.remove("liked");
      }
    })
    .catch((error) => console.error("❌ Error:", error));
}
