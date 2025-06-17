"use strict";

function removeFromWishlist(productId) {
  fetch(`/toggle-like/${productId}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": "{{ csrf_token }}",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (!data.liked) 
        document.getElementById(`product-${productId}`).remove();
    });
}
let product = document.querySelectorAll(".wishlist-row .product");
product.forEach((pro) => {
  let oldP = parseInt(
    pro.querySelector(".old-price").textContent.replace("$", "")
  );
  let newP = parseInt(
    pro.querySelector(".new-price").textContent.replace("$", "")
  );
  let disSpan = pro.querySelector(".discount-badge");
  let dis = ((oldP - newP) / oldP) * 100;
  disSpan.textContent = `${Math.round(dis)}%`;
});
