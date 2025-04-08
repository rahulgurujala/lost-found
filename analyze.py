import json
import os
import re
from collections import Counter
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Set style for plots
plt.style.use("ggplot")
sns.set(font_scale=1.2)
sns.set_style("whitegrid")

# Create output directory for analysis results
os.makedirs("./output/analysis", exist_ok=True)

# Load the data
print("Loading data from JSON file...")
with open("./output/results_async.json", "r") as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data)

# Data cleaning and preprocessing
print("Cleaning and preprocessing data...")


# Parse dates
def parse_date(date_str):
    if not isinstance(date_str, str):
        return None
    try:
        # Format is DDMMYYYY HHMM
        return datetime.strptime(date_str, "%d%m%Y %H%M")
    except Exception as e:
        print(f"Error parsing date: {e}")
        return None


df["Date_Time_Parsed"] = df["Date & Time"].apply(parse_date)
df["Date"] = df["Date_Time_Parsed"].dt.date
df["Time"] = df["Date_Time_Parsed"].dt.time
df["Hour"] = df["Date_Time_Parsed"].dt.hour
df["Month"] = df["Date_Time_Parsed"].dt.month
df["Year"] = df["Date_Time_Parsed"].dt.year
df["Day_of_Week"] = df["Date_Time_Parsed"].dt.day_name()

# Extract pin codes and create a Mumbai flag
df["Valid_Pin"] = df["Pin code"].str.match(r"^\d{6}$")
df["Mumbai_Pin"] = df["Pin code"].str.match(r"^400\d{3}$")

# Basic statistics
print("\nGenerating basic statistics...")
total_records = len(df)
print(f"Total records: {total_records}")

# 1. Police Station Analysis
print("\nAnalyzing police station distribution...")
station_counts = df["Police Station"].value_counts().head(10)
plt.figure(figsize=(12, 6))
station_counts.plot(kind="bar", color="skyblue")
plt.title("Top 10 Police Stations with Most Lost Item Reports")
plt.xlabel("Police Station")
plt.ylabel("Number of Reports")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("./output/analysis/police_station_distribution.png")

# 2. Time Analysis
print("Analyzing time patterns...")
plt.figure(figsize=(12, 6))
df["Hour"].value_counts().sort_index().plot(kind="bar", color="lightgreen")
plt.title("Distribution of Lost Items by Hour of Day")
plt.xlabel("Hour of Day (24-hour format)")
plt.ylabel("Number of Reports")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("./output/analysis/hourly_distribution.png")

# 3. Day of Week Analysis
plt.figure(figsize=(12, 6))
day_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
day_counts = df["Day_of_Week"].value_counts().reindex(day_order)
day_counts.plot(kind="bar", color="salmon")
plt.title("Distribution of Lost Items by Day of Week")
plt.xlabel("Day of Week")
plt.ylabel("Number of Reports")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("./output/analysis/day_of_week_distribution.png")

# 4. Monthly Analysis
plt.figure(figsize=(12, 6))
month_counts = df["Month"].value_counts().sort_index()
month_counts.plot(kind="bar", color="purple")
plt.title("Distribution of Lost Items by Month")
plt.xlabel("Month")
plt.ylabel("Number of Reports")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("./output/analysis/monthly_distribution.png")

# 5. Location Analysis
print("Analyzing location patterns...")


# Extract areas from the "Place of Lost / Found and Other Details" field
def extract_areas(text):
    if not isinstance(text, str):
        return []
    # Common Mumbai areas to look for
    areas = [
        "Andheri",
        "Bandra",
        "Borivali",
        "Chembur",
        "Dadar",
        "Goregaon",
        "Juhu",
        "Kandivali",
        "Kurla",
        "Malad",
        "Powai",
        "Santacruz",
        "Vile Parle",
        "Worli",
        "Colaba",
        "Versova",
        "BKC",
        "Vikhroli",
    ]
    found_areas = []
    for area in areas:
        if re.search(r"\b" + area + r"\b", text, re.IGNORECASE):
            found_areas.append(area)
    return found_areas


# Apply to both place and description fields
df["Areas_Mentioned"] = df[
    "Place of Lost / Found and Other Details (If Any)"
].apply(extract_areas) + df["Article Description"].apply(extract_areas)

# Flatten the list of areas
all_areas = [area for sublist in df["Areas_Mentioned"] for area in sublist]
area_counts = Counter(all_areas)

# Plot top areas
plt.figure(figsize=(12, 6))
area_df = (
    pd.DataFrame.from_dict(area_counts, orient="index")
    .sort_values(by=0, ascending=False)
    .head(10)
)
area_df.plot(kind="bar", legend=False, color="teal")
plt.title("Top 10 Areas Mentioned in Lost Item Reports")
plt.xlabel("Area")
plt.ylabel("Frequency")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("./output/analysis/area_distribution.png")

# 6. Contact Information Analysis
print("Analyzing contact information patterns...")
# Check if email domains are personal or business
df["Email_Domain"] = df["E-mail ID"].str.extract(r"@([^.]+)")
email_domain_counts = df["Email_Domain"].value_counts().head(10)

plt.figure(figsize=(12, 6))
email_domain_counts.plot(kind="bar", color="orange")
plt.title("Top 10 Email Domains Used in Reports")
plt.xlabel("Email Domain")
plt.ylabel("Count")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("./output/analysis/email_domain_distribution.png")

# 7. Heatmap of Day and Hour
print("Creating time heatmap...")
day_hour_counts = pd.crosstab(df["Day_of_Week"], df["Hour"])
day_hour_counts = day_hour_counts.reindex(day_order)

plt.figure(figsize=(15, 8))
sns.heatmap(day_hour_counts, cmap="YlGnBu", linewidths=0.5, annot=False)
plt.title("Heatmap of Lost Item Reports by Day and Hour")
plt.xlabel("Hour of Day")
plt.ylabel("Day of Week")
plt.tight_layout()
plt.savefig("./output/analysis/day_hour_heatmap.png")

# 8. Generate a summary report
print("Generating summary report...")
with open("./output/analysis/summary_report.txt", "w") as f:
    f.write("Lost Items Analysis Summary\n")
    f.write("=========================\n\n")
    f.write(f"Total records analyzed: {total_records}\n\n")

    f.write("Top 5 Police Stations:\n")
    for station, count in station_counts.head(5).items():
        f.write(f"  - {station}: {count} reports\n")

    f.write(
        f"\nMost common time for lost items: {df['Hour'].value_counts().idxmax()} hours\n"
    )
    f.write(
        f"Most common day for lost items: {df['Day_of_Week'].value_counts().idxmax()}\n"
    )

    f.write("\nTop 5 Areas Mentioned:\n")
    for area, count in area_counts.most_common(5):
        f.write(f"  - {area}: {count} mentions\n")

    f.write(
        f"\nPercentage of Mumbai pin codes: {df['Mumbai_Pin'].mean()*100:.1f}%\n"
    )

    f.write("\nTop 3 Email Domains:\n")
    for domain, count in email_domain_counts.head(3).items():
        f.write(f"  - {domain}: {count} users\n")

print("\nAnalysis complete! Results saved to ./output/analysis/")
print("Summary report available at ./output/analysis/summary_report.txt")

# Display a sample of the data
print("\nSample of the processed data:")
print(
    df[
        ["Police Station", "Date", "Hour", "Day_of_Week", "Areas_Mentioned"]
    ].head()
)
