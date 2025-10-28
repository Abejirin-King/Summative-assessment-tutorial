async function loadOverview() {
  try {
    const res = await fetch("http://127.0.0.1:5000/api/overview");
    const data = await res.json();

    document.getElementById("totalTrips").innerText = data.total_trips.toLocaleString();
    document.getElementById("totalRevenue").innerText = "$" + data.total_revenue.toFixed(2);
    document.getElementById("avgFare").innerText = "$" + data.avg_fare.toFixed(2);
    document.getElementById("avgDistance").innerText = data.avg_distance.toFixed(2) + " km";
    document.getElementById("avgDuration").innerText = data.avg_duration.toFixed(2) + " min";
    document.getElementById("avgTip").innerText = data.avg_tip.toFixed(2) + "%";
  } catch (err) {
    console.error("Error loading overview:", err);
  }
}

async function loadPaymentDistribution() {
  try {
    const res = await fetch("http://127.0.0.1:5000/api/payment_distribution");
    const data = await res.json();

    const ctx = document.getElementById("paymentChart").getContext("2d");
    new Chart(ctx, {
      type: "pie",
      data: {
        labels: data.map(d => d.payment_type),
        datasets: [{
          data: data.map(d => d.count),
          backgroundColor: ["#4CAF50","#FF9800","#03A9F4","#E91E63","#9C27B0"]
        }]
      },
      options: {
        plugins: { legend: { position: 'bottom' } }
      }
    });
  } catch (err) {
    console.error("Error loading payment chart:", err);
  }
}

async function loadDistanceDistribution() {
  try {
    const res = await fetch("http://127.0.0.1:5000/api/trip_distance_distribution");
    const data = await res.json();

    const ctx = document.getElementById("distanceChart").getContext("2d");
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: data.map(d => d.distance_range),
        datasets: [{
          label: "Trip Count",
          data: data.map(d => d.count),
          backgroundColor: "#2196F3"
        }]
      },
      options: {
        responsive: true,
        scales: { y: { beginAtZero: true } }
      }
    });
  } catch (err) {
    console.error("Error loading distance chart:", err);
  }
}

window.addEventListener("DOMContentLoaded", () => {
  loadOverview();
  loadPaymentDistribution();
  loadDistanceDistribution();
});
