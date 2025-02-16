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
var x = new Swiper(".pro-div .container .products", {
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
    500: {
      slidesPerView: 2,
      spaceBetween: 15,
    },
    0: {
      slidesPerView: 1,
      spaceBetween: 10,
    },
  },
});

// End swiper product in section Four

// Add and remove class active on icon Heart
document.querySelectorAll("#iconheart").forEach((icon) => {
  icon.addEventListener("click", function () {
    this.classList.toggle("active");
    if (
      this.classList.contains("active") &&
      document.body.classList.contains("light")
    ) {
      this.style.color = "black";
    }
    if (
      !this.classList.contains("active") &&
      document.body.classList.contains("dark")
    ) {
      this.style.color = "white";
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
    500: {
      slidesPerView: 2,
      spaceBetween: 15,
    },
    0: {
      slidesPerView: 1,
      spaceBetween: 10,
    },
  },
});
document.querySelectorAll(".pro").forEach((div) => {
  div.addEventListener("click", function (event) {
    if (event.target.closest(".addcart") || event.target.closest(".icons"))
      return;
    let img = this.querySelector("img");
    let name = this.querySelector("h5").innerHTML;
    let newSall = this.querySelector(".new-sall").innerHTML;
    let imgSrc = img.getAttribute("src");
    localStorage.setItem("namePro", name);
    localStorage.setItem("newSall", newSall);
    localStorage.setItem("imgsrc", imgSrc);
    let oldSall = this.querySelector(".old-sall");
    if (oldSall) {
      let oldSallH = oldSall.innerHTML;
      localStorage.setItem("oldSall", oldSallH);
    } else localStorage.removeItem("oldSall");
    window.location.href = "onepro.html";
  });
});
