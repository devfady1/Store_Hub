"use strict";

// Start One Product Page
let dec = document.querySelector(
  ".imgAndDetailes .container .detailes .buyLove .dec"
);
let inc = document.querySelector(
  ".imgAndDetailes .container .detailes .buyLove .inc"
);
let Num = document.getElementById("Num");

dec.addEventListener("click", () => {
  if (Num.innerHTML == "0") Num.innerHTML = "0";
  else Num.innerHTML--;
});
inc.addEventListener("click", () => {
  Num.innerHTML++;
});

window.addEventListener("load", function () {
  let storedSrc = localStorage.getItem("imgsrc");
  let namePro = localStorage.getItem("namePro");
  let newSall = localStorage.getItem("newSall");
  let oldSall = localStorage.getItem("oldSall");
  let imgInOnePro = document.querySelector(".imgAndDetailes .img img");
  let nameProH5 = document.querySelector(".imgAndDetailes #proname");
  let newSallH = document.querySelector(".imgAndDetailes #newSall");
  let oldSallH = document.querySelector(".imgAndDetailes #oldSall");
  if (newSall) newSallH.innerHTML = newSall;
  if (namePro) nameProH5.innerHTML = namePro;
  if (storedSrc) imgInOnePro.setAttribute("src", storedSrc);
  if (oldSall) {
    oldSallH.innerHTML = oldSall;
    oldSallH.style.display = "block";
  } else {
    oldSallH.style.display = "none";
  }
});
