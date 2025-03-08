"use strict";

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