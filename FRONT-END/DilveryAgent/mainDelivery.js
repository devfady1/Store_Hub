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

// Order History Select
/* 
  1 - لو عدد العناصر ف عدد الايام دى اقل من 5 اخفى السكشن ال تحت خالص

  2 - لو اكتر اعرض 5 بس و الباقى اودية ع الصفحة التانية

   و التانية يبقا 5 بس لغايت م اخلص العناصر كلها
  3 - عدد الايام هتتعمل ب فانكشن هتعدى ع كل ceil 
  فيها تاريخ و تشوف تاريخ انهاردا و تقارن 
  عل حسب عدد الايام ال اليوزر مختارها فوق 
  سوا 7 او 10 او 15 او 30

  4 - لازم لازم احط اوبشن ان القيمة ال ف السليكت تفضل حتى لو عملت ريفرش 
  
  5 - لازم لازم لازم احط اوبشن انى اقدر اشغل الاتنين سيليكت مع بعض و اسرش باكتر من حاجة ف نفس الوقت
*/
