import json
from datetime import datetime, timedelta
from collections import Counter
from pathlib import Path

# Load data
with open("breaches.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Count breaches
date_counts = Counter()
state_counts = Counter()
type_counts = Counter()

for entry in data:
    raw_date = entry.get("Date Added")
    if isinstance(raw_date, str):
        try:
            parsed_date = datetime.strptime(raw_date.strip(), "%m/%d/%Y").date()
            date_counts[parsed_date] += 1
        except ValueError:
            continue

    state = entry.get("State")
    if isinstance(state, str):
        state_counts[state.strip()] += 1

    breach_type = entry.get("Type of Breach")
    if isinstance(breach_type, str):
        type_counts[breach_type.strip()] += 1

# Build datasets for 1, 7, 30 days
today = datetime.today().date()
datasets = {}
for days in [1, 7, 30]:
    start = today - timedelta(days=days - 1)
    filtered = {d: c for d, c in date_counts.items() if start <= d <= today}
    sorted_items = sorted(filtered.items())
    datasets[days] = {
        "labels": [d.strftime("%b %d") for d, _ in sorted_items],
        "data": [c for _, c in sorted_items]
    }

# Top 15 states and types
top_states = state_counts.most_common(15)
top_types = type_counts.most_common(15)
state_labels, state_data = zip(*top_states) if top_states else ([], [])
type_labels, type_data = zip(*top_types) if top_types else ([], [])

# Chart block
chart_html = f"""
<style>
canvas {{
  width: 100% !important;
  max-width: 800px;
  height: 400px;
  margin: 0 auto 3rem;
  display: block;
}}
.stats-container h2 {{
  text-align: center;
  margin: 2rem 0 1rem;
}}
</style>

<h2>📊 Breaches Over Time</h2>
<div style="text-align:center;margin-bottom:1rem;">
  <label for="range">View:</label>
  <select id="range" onchange="updateChart()">
    <option value="1">Last 1 Day</option>
    <option value="7" selected>Last 7 Days</option>
    <option value="30">Last 30 Days</option>
  </select>
</div>
<canvas id="breachChart"></canvas>

<h2>🗺️ Breaches by State</h2>
<canvas id="stateChart"></canvas>

<h2>🧩 Breaches by Type</h2>
<canvas id="typeChart"></canvas>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
const chartData = {{
  1: {{ labels: {json.dumps(datasets[1]["labels"])}, data: {json.dumps(datasets[1]["data"])} }},
  7: {{ labels: {json.dumps(datasets[7]["labels"])}, data: {json.dumps(datasets[7]["data"])} }},
  30: {{ labels: {json.dumps(datasets[30]["labels"])}, data: {json.dumps(datasets[30]["data"])} }}
}};

const ctxTime = document.getElementById('breachChart').getContext('2d');
const ctxState = document.getElementById('stateChart').getContext('2d');
const ctxType = document.getElementById('typeChart').getContext('2d');

let breachChart = new Chart(ctxTime, {{
  type: 'bar',
  data: {{
    labels: chartData[7].labels,
    datasets: [{{
      label: 'Breaches',
      data: chartData[7].data,
      backgroundColor: 'rgba(0, 119, 182, 0.6)',
      borderColor: 'rgba(0, 119, 182, 1)',
      borderWidth: 1
    }}]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: false,
    scales: {{
      y: {{
        beginAtZero: true,
        ticks: {{ precision: 0 }}
      }}
    }}
  }}
}});

function updateChart() {{
  const days = document.getElementById('range').value;
  breachChart.data.labels = chartData[days].labels;
  breachChart.data.datasets[0].data = chartData[days].data;
  breachChart.update();
}}

new Chart(ctxState, {{
  type: 'bar',
  data: {{
    labels: {json.dumps(state_labels)},
    datasets: [{{
      label: 'Breach Count by State',
      data: {json.dumps(state_data)},
      backgroundColor: 'rgba(255, 99, 132, 0.6)',
      borderColor: 'rgba(255, 99, 132, 1)',
      borderWidth: 1
    }}]
  }},
  options: {{
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    scales: {{
      x: {{
        beginAtZero: true,
        ticks: {{ precision: 0 }}
      }}
    }}
  }}
}});

new Chart(ctxType, {{
  type: 'bar',
  data: {{
    labels: {json.dumps(type_labels)},
    datasets: [{{
      label: 'Breach Count by Type',
      data: {json.dumps(type_data)},
      backgroundColor: 'rgba(54, 162, 235, 0.6)',
      borderColor: 'rgba(54, 162, 235, 1)',
      borderWidth: 1
    }}]
  }},
  options: {{
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    scales: {{
      x: {{
        beginAtZero: true,
        ticks: {{ precision: 0 }}
      }}
    }}
  }}
}});
</script>
"""

# Inject into base template
with open("base_template_stats.html", "r", encoding="utf-8") as f:
    base_html = f.read()

start = base_html.find("<!-- START-STATS-SECTION -->")
end = base_html.find("<!-- END-STATS-SECTION -->") + len("<!-- END-STATS-SECTION -->")

final_html = base_html[:start] + "<!-- START-STATS-SECTION -->\n" + chart_html + "\n" + base_html[end:]

with open("stats.html", "w", encoding="utf-8") as f:
    f.write(final_html)

print("✅ stats.html generated.")
