"use strict";

//User Account

    // Account dropdown functionality
  const accountIcon = document.getElementById('user-icon');
  const accountDropdown = document.getElementById('accountDropdown');
  let isDropdownVisible = false;

    // Toggle dropdown when account icon is clicked
    accountIcon.addEventListener('click', (e) => {
    e.stopPropagation();
  isDropdownVisible = !isDropdownVisible;
  if (isDropdownVisible) {
    accountDropdown.classList.add('active');
      } else {
    accountDropdown.classList.remove('active');
      }
    });

    // Close dropdown when clicking elsewhere
    document.addEventListener('click', (e) => {
      if (isDropdownVisible && e.target !== accountIcon && !accountDropdown.contains(e.target)) {
    accountDropdown.classList.remove('active');
  isDropdownVisible = false;
      }
    });

    // Hide dropdown on scroll
    window.addEventListener('scroll', () => {
      if (isDropdownVisible) {
    accountDropdown.classList.remove('active');
  isDropdownVisible = false;
      }
    });

    
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
  div.addEventListener("click", function () {
    let img = this.querySelector("img");
    if (img) {
      let imgSrc = img.getAttribute("src");
      localStorage.setItem("imgsrc", imgSrc);
      window.location.href = "onepro.html";
    }
  });
});
