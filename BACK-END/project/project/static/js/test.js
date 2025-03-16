"use strict";


// Start Swiper Section 1
const swiper = new Swiper(".swiper", {
  loop: true,

  pagination: {
    el: ".swiper-pagination",
    dynamicBullests: true,
    clickable: true,
  },
  autoplay: {
    delay: 1500,
  },

  scrollbar: {
    el: ".swiper-scrollbar",
  },
});
// End Swiper



// Start swiper product in section Four
var x = new Swiper(".products", {
  slidesPerView: 4,
  spaceBetween: 30,
  autoplay: { delay: 3000 },
  navigation: {
    nextEl: ".btSwapProNext",
    prevEl: ".btSwapProPrev",
  },
  loop: true,
  breakpoints: {
    1600: {
      slidesPerView: 5,
    },
    1200: {
      slidesPerView: 4,
      spaceBetween: 25,
    },
    700: {
      slidesPerView: 3,
      spaceBetween: 15,
    },
    0: {
      slidesPerView: 2,
      spaceBetween: 10,
    },
  },
});

// End swiper product in section Four




// Add and remove class active on icon Heart
document.querySelectorAll("#iconheart").forEach((icon) => {
  icon.addEventListener("click", function () {
    this.classList.toggle("active");
    if (this.classList.contains("active") && document.body.classList.contains("light")) {
      this.style.color = "black";
    }
    if(!this.classList.contains("active") && document.body.classList.contains("dark")){
      this.style.color = "white"
    }
  });
});






// Start Swiper Search by Category

var x = new Swiper(".categs", {
  slidesPerView: 4,
  spaceBetween: 30,
  autoplay: { delay: 2000 },
  navigation: {
    nextEl: ".btnSwapNext",
    prevEl: ".BtnSwapPrev",
  },
  loop: true,
  breakpoints: {
    1600: {
      slidesPerView: 5,
    },
    1200: {
      slidesPerView: 4,
      spaceBetween: 25,
    },
    700: {
      slidesPerView: 3,
      spaceBetween: 15,
    },
    0: {
      slidesPerView: 2,
      spaceBetween: 10,
    },
  },
});

// Start DarkMode
const body = document.querySelector("body");
const toggle = document.querySelector("#toggle");
const sunIcon = document.querySelector(".toggle .bxs-sun");
const moonIcon = document.querySelector(".toggle .bx-moon");

toggle.addEventListener("change", () => {
  body.classList.toggle("dark");
  sunIcon.className =
    sunIcon.className == "bx bxs-sun" ? "bx bx-sun" : "bx bxs-sun";
  moonIcon.className =
    moonIcon.className == "bx bxs-moon" ? "bx bx-moon" : "bx bxs-moon";
  if (body.classList.contains("dark")) {
    localStorage.setItem("DarkToogle", "Dark");
  } else {
    localStorage.removeItem("DarkToogle");
  }
});
document.addEventListener("DOMContentLoaded", () => {
  if (localStorage.getItem("DarkToogle")) {
    body.classList.add("dark");
    sunIcon.className =
      sunIcon.className == "bx bxs-sun" ? "bx bx-sun" : "bx bxs-sun";
    moonIcon.className =
      moonIcon.className == "bx bxs-moon" ? "bx bx-moon" : "bx bxs-moon";
  }
});
// End DarkMode





// start add to cart
document.querySelectorAll(".addcart").forEach(button => {
  button.addEventListener("click", function() {
      let productId = this.dataset.id;

      fetch(`/add-to-cart/?product_id=${productId}`)
      .then(response => response.json())
      .then(data => {
          console.log("🔍 Response from server:", data);
          if (data.status === "success") {
              alert("✅ المنتج تم إضافته بنجاح!");
              window.location.href = "/cart/";
          } else {
              alert("❌ حدث خطأ أثناء الإضافة!");
          }
      })
      .catch(error => console.error('❌ Fetch Error:', error));
  });
});

// end add to cart



