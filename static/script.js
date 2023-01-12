checkboxes = document.querySelectorAll('input[type="checkbox"]');
progressBar = document.getElementById("progress");
clear = document.getElementById("clear");

today = new Date();
day = document.getElementById(today.getDay());
day.style.color = "var(--bs-warning)";
day.style.borderBottomColor = "var(--bs-light)";

let checked = 0;
let percentage = 0;

checkboxes.forEach((checkbox) => {
  checkbox.addEventListener("change", (e) => {
    checked += checkbox.checked ? 1 : -1;
    percentage = (checked / checkboxes.length) * 100;
    progressBar.style.width = `${percentage}%`;
    fetch("/", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        type: "",
        id: checkbox.id,
        value: e.target.checked ? "checked" : "",
      }),
    })
      .then((res) => {
        if (!res.ok) {
          throw Error(res.status);
        }
        return res.json();
      })
      .catch((err) => console.error(err));
  });
});

clear.addEventListener("click", (e) => {
  checkboxes.forEach((checkbox) => {
    checkbox.checked = false;
  });
  checked = 0;
  progressBar.style.width = "0%";
  fetch("/", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      type: "clear",
    }),
  })
    .then((res) => {
      if (!res.ok) {
        throw Error(res.status);
      }
      return res.json();
    })
    .catch((err) => console.error(err));
});

window.addEventListener("load", () => {
  checked = 0;
  percentage = 0;
  checkboxes.forEach((checkbox) => {
    checked += checkbox.checked ? 1 : 0;
  });
  percentage = (checked / checkboxes.length) * 100;
  progressBar.style.width = `${percentage}%`;
});
