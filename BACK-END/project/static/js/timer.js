"use strict";
// Start Timer
let days = document.querySelector(".day");
let hour = document.querySelector(".hour");
let minut = document.querySelector(".minut");
let second = document.querySelector(".second");

// تحديد وقت النهاية (يمكنك تغيير الوقت على حسب ما تريد)
let endTime = localStorage.getItem("endTime");
if (!endTime) {
  // وضع وقت نهاية محدد إذا لم يتم تحديده من قبل
  endTime = Date.now() + 5 * 24 * 60 * 60 * 1000; // مثلا 5 أيام من الآن
  localStorage.setItem("endTime", endTime);
}

function updateClock() {
  let currentTime = Date.now();
  let remainingTime = endTime - currentTime;

  if (remainingTime <= 0) {
    // إذا انتهى الوقت
    days.innerText = "00:";
    hour.innerText = "00:";
    minut.innerText = "00:";
    second.innerText = "00";
    return; // التوقف عن التحديث بعد انتهاء الوقت
  }

  let totalSeconds = Math.floor(remainingTime / 1000);
  let dayValue = Math.floor(totalSeconds / (24 * 60 * 60));
  let hourValue = Math.floor((totalSeconds % (24 * 60 * 60)) / (60 * 60));
  let minutValue = Math.floor((totalSeconds % (60 * 60)) / 60);
  let secondValue = totalSeconds % 60;

  days.innerText = dayValue < 10 ? "0" + dayValue + ":" : dayValue + ":";
  hour.innerText = hourValue < 10 ? "0" + hourValue + ":" : hourValue + ":";
  minut.innerText = minutValue < 10 ? "0" + minutValue + ":" : minutValue + ":";
  second.innerText = secondValue < 10 ? "0" + secondValue : secondValue;
}

// تحديث العد التنازلي كل ثانية
setInterval(updateClock, 1000);
// End Timer
