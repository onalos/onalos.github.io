from datetime import datetime

chart_html = """
<div>
  <h2 style="text-align:center;">📊 Breaches Over Time (Mock Data)</h2>
  <canvas id="breachChart"></canvas>
</div>
<script>
const ctx = document.getElementById('breachChart').getContext('2d');
new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    datasets: [{
      label: 'Breaches',
      data: [5, 9, 3, 7, 6],
      backgroundColor: 'rgba(0, 119, 182, 0.2)',
      borderColor: 'rgba(0, 119, 182, 1)',
      borderWidth: 2,
      fill: true
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: { beginAtZero: true }
    }
  }
});
</script>
"""

with open("base_template_stats.html", "r", encoding="utf-8") as f:
    template = f.read()

start = template.find("<!-- START-STATS-SECTION -->")
end = template.find("<!-- END-STATS-SECTION -->") + len("<!-- END-STATS-SECTION -->")

final_html = template[:start] + "<!-- START-STATS-SECTION -->\n" + chart_html + "\n" + template[end:]

with open("stats.html", "w", encoding="utf-8") as f:
    f.write(final_html)

print("✅ stats.html generated.")
