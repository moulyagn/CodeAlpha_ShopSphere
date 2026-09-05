document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.querySelector("#sales-chart");
  if (!canvas || typeof Chart === "undefined") return;
  const labels = JSON.parse(canvas.dataset.labels || "[]");
  const revenue = JSON.parse(canvas.dataset.revenue || "[]");
  new Chart(canvas, {
    type: "line",
    data: { labels, datasets: [{ label: "Revenue (₹)", data: revenue, borderColor: "#D4AF37", backgroundColor: "rgba(212,175,55,.14)", fill: true, tension: .35 }] },
    options: { responsive: true, plugins: { legend: { labels: { color: "#f6f1e8" } } }, scales: { x: { ticks: { color: "#a8a39a" }, grid: { color: "rgba(212,175,55,.12)" } }, y: { ticks: { color: "#a8a39a" }, grid: { color: "rgba(212,175,55,.12)" } } } }
  });
});
