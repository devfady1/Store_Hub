"use strict";

// Side Bar
function toggleSideMenu() {
  document.getElementById("sideMenu").classList.toggle("active");
}

window.addEventListener("resize", function () {
  if (window.innerWidth > 768) {
    document.getElementById("sideMenu").classList.remove("active");
  }
});

document.querySelectorAll("#sideMenu a").forEach((link) => {
  link.addEventListener("click", () => {
    document.getElementById("sideMenu").classList.remove("active");
  });
});

// Account dropdown functionality
const accountIcon = document.getElementById("user-icon");
const accountDropdown = document.getElementById("accountDropdown");
let isDropdownVisible = false;

accountIcon.addEventListener("click", (e) => {
  e.stopPropagation();
  isDropdownVisible = !isDropdownVisible;
  if (isDropdownVisible) {
    accountDropdown.classList.add("active");
  } else {
    accountDropdown.classList.remove("active");
  }
});

document.addEventListener("click", (e) => {
  if (
    isDropdownVisible &&
    e.target !== accountIcon &&
    !accountDropdown.contains(e.target)
  ) {
    accountDropdown.classList.remove("active");
    isDropdownVisible = false;
  }
});

// StoreHub Text
const text = "STOREHUB";
const title = document.getElementById("store-title");
let index = 0;
let deleting = false;

function typeWriter() {
  if (!deleting) {
    title.textContent = text.substring(0, index + 1);
    index++;
    if (index === text.length) {
      deleting = true;
      setTimeout(typeWriter, 2000);
      return;
    }
  } else {
    title.textContent = text.substring(0, index - 1);
    index--;
    if (index === 1) {
      deleting = false;
    }
  }
  setTimeout(typeWriter, 150);
}

document.addEventListener("DOMContentLoaded", typeWriter);


// Seacrch Funcation
const searchInput = document.getElementById("searchInput");
const searchResults = document.getElementById("searchResults");
const searchLoading = document.querySelector(".search-loading");
const noResults = document.querySelector(".no-results");
let searchTimeout;
let lastQuery = "";

const updatePosition = () => {
  if (searchResults.style.display === "block") {
    const headerHeight = document.querySelector("header").offsetHeight;
    searchResults.style.top = `${headerHeight}px`;
  }
};

window.addEventListener("scroll", updatePosition);
window.addEventListener("resize", updatePosition);

// Seacrch Funcation
const performSearch = async (query) => {
  if (query === lastQuery) return;
  lastQuery = query;

  if (query.length < 2) {
    searchResults.style.display = "none";
    return;
  }

  try {
    searchResults.style.display = "block";
    searchLoading.style.display = "flex";
    noResults.style.display = "none";

    const response = await fetch(
      `/search-products/?q=${encodeURIComponent(query)}`
    );
    const data = await response.json();

    searchLoading.style.display = "none";

    if (data.length === 0) {
      noResults.style.display = "flex";
      return;
    }

    const resultsHtml = data
      .map(
        (product) => `
          <div class="search-result-item" data-product-id="${product.id}">
            <img src="${product.image}" alt="${product.name}" loading="lazy">
            <div class="product-info">
              <div class="product-name">${product.name}</div>
              <div class="product-meta">
                <span class="product-price">${product.price} جنيه</span>
                ${
                  product.category
                    ? `<span class="product-category">${product.category}</span>`
                    : ""
                }
              </div>
            </div>
          </div>
        `
      )
      .join("");

    const resultsContainer = document.createElement("div");
    resultsContainer.className = "search-results-container";
    resultsContainer.innerHTML = resultsHtml;

    // delete old result
    const oldContainer = searchResults.querySelector(
      ".search-results-container"
    );
    if (oldContainer) {
      oldContainer.remove();
    }

    searchResults.appendChild(resultsContainer);

    const resultItems = searchResults.querySelectorAll(".search-result-item");
    resultItems.forEach((item) => {
      item.addEventListener("click", () => {
        const productId = item.dataset.productId;
        window.location.href = `/product/${productId}/`;
      });

      item.addEventListener("mouseenter", () => {
        const productId = item.dataset.productId;
        const link = document.createElement("link");
        link.rel = "prefetch";
        link.href = `/product/${productId}/`;
        document.head.appendChild(link);
      });
    });
  } catch (error) {
    console.error("خطأ في البحث:", error);
    searchLoading.style.display = "none";
    noResults.style.display = "flex";
    noResults.querySelector("span").textContent = "حدث خطأ في البحث";
  }
};

searchInput.addEventListener("input", (e) => {
  clearTimeout(searchTimeout);
  const query = e.target.value.trim();

  searchTimeout = setTimeout(() => {
    performSearch(query);
  }, 300);
});

// close Result when click of any where in page
document.addEventListener("click", (e) => {
  if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
    searchResults.style.display = "none";
  }
});

// open Result when click on seacrch input
searchInput.addEventListener("focus", () => {
  if (searchInput.value.trim().length >= 2) {
    searchResults.style.display = "block";
  }
});

searchInput.addEventListener("keydown", (e) => {
  const results = searchResults.querySelectorAll(".search-result-item");
  const currentActive = searchResults.querySelector(
    ".search-result-item.active"
  );
  let nextActive;

  switch (e.key) {
    case "ArrowDown":
      e.preventDefault();
      if (!currentActive) {
        nextActive = results[0];
      } else {
        const currentIndex = Array.from(results).indexOf(currentActive);
        nextActive = results[currentIndex + 1] || results[0];
      }
      break;

    case "ArrowUp":
      e.preventDefault();
      if (!currentActive) {
        nextActive = results[results.length - 1];
      } else {
        const currentIndex = Array.from(results).indexOf(currentActive);
        nextActive = results[currentIndex - 1] || results[results.length - 1];
      }
      break;

    case "Enter":
      if (currentActive) {
        e.preventDefault();
        window.location.href = `/product/${currentActive.dataset.productId}/`;
      }
      break;

    case "Escape":
      e.preventDefault();
      searchResults.style.display = "none";
      searchInput.blur();
      break;
  }

  if (nextActive) {
    currentActive?.classList.remove("active");
    nextActive.classList.add("active");
    nextActive.scrollIntoView({ block: "nearest" });
  }
});

var x = new Swiper(".xx", {
  slidesPerView: 1,
  spaceBetween: 30,
  autoplay: { delay: 3000 },
  navigation: {
    nextEl: ".nxt",
    prevEl: ".bc",
  },
});

var xcxc = new Swiper(".z", {
  slidesPerView: 1,
  spaceBetween: 30,
  autoplay: { delay: 3000 },
  navigation: {
    nextEl: ".nxt",
    prevEl: ".bc",
  },
});