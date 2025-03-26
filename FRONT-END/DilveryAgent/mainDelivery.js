"use strict";
const accountIcon = document.getElementById("user-icon");
const accountDropdown = document.getElementById("accountDropdown");
let isDropdownVisible = false;

// Toggle dropdown when account icon is clicked
accountIcon.addEventListener("click", (e) => {
  e.stopPropagation();
  isDropdownVisible = !isDropdownVisible;
  if (isDropdownVisible) accountDropdown.classList.add("active");
  else accountDropdown.classList.remove("active");
});

// Close dropdown when clicking elsewhere
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


// Icons in Select

