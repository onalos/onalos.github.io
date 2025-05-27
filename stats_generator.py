import json
from datetime import datetime
from collections import Counter
from pathlib import Path
import random

# Load breach data
with open("breaches.json", "r", encoding="utf-8") as f:
    data = json.load(f)

state_counts = Counter()
type_counts = Counter()

for entry in data:
    state = entry.get("State")
    if isinstance(state, str):
        state_counts[state.strip()] += 1

    breach_type = entry.get("Type of Breach")
    if isinstance(breach_type, str):
        type_counts[breach_type.strip()] += 1

# Top 15 entries
top_states = state_counts.most_common(15)
top_types = type_counts.most_common(15)
state_labels, state_data = zip(*top_states) if top_states else ([], [])
type_labels, type_data = zip(*top_types) if top_types else ([], [])

# Generate distinct bar colors
def generate_colors(n):
    return [f"rgba({random.randint(50,255)}, {random.randint(50,255)}, {random.randint(50,255)}, 0.6)" for _ in range(n)]

state_colors = generate_colors(len(state_labels))
type_colors = generate_colors(len(type_labels))

# Load the base template
with open("base_template_stats.html", "r", encoding="utf-8") as f:
    template_html = f.read()

start = template_html.find("<!-- START-STATS-SECTION -->")
end = template_html.find("<!-- END-STATS-SECTION -->") + len("<!-- END-STATS-SECTION -->")

# Chart HTML block with no legends
chart_html = f"""
<style>
canvas {{
  max-height: 480px;
  width: 100% !important;
  height: auto !important;
  display: block;
  margin-bottom: 2rem;
}}
.chart-wrapper {{
  overflow-x: auto;
}}
</style>

<h2>🗺️ Breaches by State</h2>
<div class="chart-wrapper"><canvas id="stateChart"></canvas></div>

<h2>🧩 Breaches by Type</h2>
<div class="chart-wrapper"><canvas id="typeChart"></canvas></div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
new Chart(document.getElementById('stateChart').getContext('2d'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps(state_labels)},
    datasets: [{{
      data: {json.dumps(state_data)},
      backgroundColor: {json.dumps(state_colors)},
      borderColor: {json.dumps(state_colors)},
      borderWidth: 1
    }}]
  }},
  options: {{
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{
      legend: {{ display: false }}
    }},
    scales: {{
      x: {{
        beginAtZero: true,
        ticks: {{ precision: 0 }}
      }}
    }}
  }}
}});

new Chart(document.getElementById('typeChart').getContext('2d'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps(type_labels)},
    datasets: [{{
      data: {json.dumps(type_data)},
      backgroundColor: {json.dumps(type_colors)},
      borderColor: {json.dumps(type_colors)},
      borderWidth: 1
    }}]
  }},
  options: {{
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{
      legend: {{ display: false }}
    }},
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

# Inject chart block into template
final_html = template_html[:start] + "<!-- START-STATS-SECTION -->\n" + chart_html + "\n" + template_html[end:]

# Write output file
with open("stats.html", "w", encoding="utf-8") as f:
    f.write(final_html)

print("✅ stats.html generated.")
