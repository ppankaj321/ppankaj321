import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

USERNAME = "ppankaj321"
START_DATE = datetime(2025, 8, 24)

# GitHub API URL for user events
url = f"https://api.github.com/users/{USERNAME}/events?per_page=100"

events = []
page = 1

while True:
    resp = requests.get(f"{url}&page={page}")
    if resp.status_code != 200:
        print("⚠️ API Error:", resp.json())
        break
    
    data = resp.json()
    if not data:  # no more pages
        break
    
    # Only keep events >= START_DATE
    valid_data = [
        ev for ev in data
        if datetime.strptime(ev["created_at"], "%Y-%m-%dT%H:%M:%SZ") >= START_DATE
    ]
    
    events.extend(valid_data)

    # Stop if last event in this page is older than START_DATE
    last_event = datetime.strptime(data[-1]["created_at"], "%Y-%m-%dT%H:%M:%SZ")
    if last_event < START_DATE:
        break

    page += 1

print(f"✅ Collected {len(events)} events since {START_DATE.date()}")

# Process weekly activities
weeks = {}
for event in events:
    created = datetime.strptime(event["created_at"], "%Y-%m-%dT%H:%M:%SZ")
    week_start = created - timedelta(days=created.weekday())  # Monday
    week_start_str = week_start.strftime("%Y-%m-%d")
    weeks[week_start_str] = weeks.get(week_start_str, 0) + 1

# Build DataFrame
df = pd.DataFrame(list(weeks.items()), columns=["Week", "Activities"])
df = df.sort_values("Week")
df["Cumulative"] = df["Activities"].cumsum()

# Update README.md with weekly table
readme_path = "README.md"
with open(readme_path, "r") as f:
    content = f.read()

before = "<!--START_SECTION:weekly_activity-->"
after = "<!--END_SECTION:weekly_activity-->"
table_md = df.to_markdown(index=False)

new_content = content.split(before)[0] + before + "\n\n" + table_md + "\n\n" + after + content.split(after)[1]

with open(readme_path, "w") as f:
    f.write(new_content)

# Plot weekly activity graph
plt.figure(figsize=(8, 4))
plt.plot(df["Week"], df["Activities"], marker="o", label="Weekly")
plt.title("Weekly GitHub Activity (from 24-08-2025)")
plt.xticks(rotation=45)
plt.ylabel("Number of Activities")
plt.legend()
plt.tight_layout()
plt.savefig("weekly_activity_graph.svg")

# Plot cumulative activity graph
plt.figure(figsize=(8, 4))
plt.plot(df["Week"], df["Cumulative"], marker="o", color="green", label="Cumulative")
plt.title("Cumulative GitHub Activity (from 24-08-2025)")
plt.xticks(rotation=45)
plt.ylabel("Total Activities")
plt.legend()
plt.tight_layout()
plt.savefig("cumulative_activity_graph.svg")