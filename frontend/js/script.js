const API = "https://fake-review-detection-system-rj90.onrender.com";

let chartInstance = null;

console.log("SCRIPT LOADED");

async function login() {

  let email = document.getElementById("email").value;
  let password = document.getElementById("password").value;

  let res = await fetch(API + "/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      email,
      password
    })
  });

  let data = await res.json();

  if (data.msg === "success") {

    localStorage.setItem("email", email);

    window.location = "dashboard.html";

  } else {

    alert("Login failed");

  }
}

async function register() {

  let email = document.getElementById("r_email").value;
  let password = document.getElementById("r_password").value;

  let res = await fetch(API + "/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      email,
      password
    })
  });

  let data = await res.json();

  alert(data.msg);

  if (data.msg === "Registered Successfully") {
    window.location = "index.html";
  }

}

async function analyze() {

  let text = document.getElementById("review").value;

  let email = localStorage.getItem("email");

  document.getElementById("result").innerText = "Analyzing...";

  let res = await fetch(API + "/predict", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      text,
      email
    })
  });

  let data = await res.json();

  document.getElementById("result").innerText =
    data.prediction;

  document.getElementById("confidence").innerText =
    "Confidence: " + data.confidence + "%";

  document.getElementById("trustScore").innerText =
    "Product Trust Score: " + data.trust_score + "%";

  let explanationList =
    document.getElementById("explanation");

  explanationList.innerHTML = "";

  data.explanation.forEach(item => {

    let li = document.createElement("li");

    li.innerText = item;

    explanationList.appendChild(li);

  });

  let suspiciousList =
    document.getElementById("suspiciousWords");

  suspiciousList.innerHTML = "";

  data.suspicious_words.forEach(word => {

    let li = document.createElement("li");

    li.innerText = word;

    suspiciousList.appendChild(li);

  });

  loadAnalytics();
}

async function loadHistory() {

  let email = localStorage.getItem("email");

  let res = await fetch(
    API + "/history/" + email
  );

  let data = await res.json();

  let list = document.getElementById("history");

  list.innerHTML = "";

  data.forEach(r => {

    let li = document.createElement("li");

    li.innerText =
      r.text + " | " + r.confidence + "%";

    list.appendChild(li);

  });

}

async function loadAnalytics() {

  let res = await fetch(API + "/analytics");

  let data = await res.json();

  document.getElementById("totalReviews").innerText =
    data.total_reviews;

  document.getElementById("fakeReviews").innerText =
    data.fake_reviews;

  document.getElementById("realReviews").innerText =
    data.real_reviews;

  document.getElementById("analyticsTrust").innerText =
    data.trust_score;

  renderChart(
    data.real_reviews,
    data.fake_reviews
  );
}

function renderChart(real, fake) {

  if (chartInstance) {
    chartInstance.destroy();
  }

  chartInstance = new Chart(
    document.getElementById("chart"),
    {
      type: "pie",
      data: {
        labels: [
          "Genuine Reviews",
          "Fake Reviews"
        ],
        datasets: [
          {
            data: [real, fake]
          }
        ]
      }
    }
  );
}

async function sendChat() {

  let msg =
    document.getElementById("chatInput").value;

  let res = await fetch(
    API + "/chat",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        message: msg
      })
    }
  );

  let data = await res.json();

  document.getElementById("chatOutput").innerText =
    data.reply;
}

function toggleTheme() {

  document.body.classList.toggle("light");

}

function logout() {

  localStorage.removeItem("email");

  window.location = "index.html";

}

window.onload = function () {

  if (document.getElementById("chart")) {

    loadAnalytics();

  }

};

