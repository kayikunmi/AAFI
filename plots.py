import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Load CSV
df = pd.read_csv("experiment_summary.csv")
df = df.dropna(subset=["mining_time"])  #remove incomplete rows

#colors
algorithm_colors = {
    "apriori": "red",
    "eclat": "green",
    "declat": "blue"
}

os.makedirs("plots", exist_ok=True)

#Mining Time vs. Support per dataset (3 plots)
for dataset in df["dataset"].unique():
    subset = df[df["dataset"] == dataset]
    plt.figure(figsize=(8, 5))
    sns.lineplot(
        data=subset,
        x="support_value",
        y="mining_time",
        hue="algorithm",
        style="algorithm",
        markers=True,
        palette=algorithm_colors
    )
    plt.title(f"Mining Time vs. Support — {dataset.capitalize()}")
    plt.xlabel("Support")
    plt.ylabel("Mining Time (s)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"plots/{dataset}_mining_time.png")
    plt.close()

#Peak Memory Usage (bar chart)
plt.figure(figsize=(12, 6))
df["label"] = df["dataset"] + "_" + df["support_value"].astype(str)
sns.barplot(
    data=df,
    x="label",
    y="peak_memory_MB",
    hue="algorithm",
    palette=algorithm_colors
)
plt.xticks(rotation=45)
plt.title("Peak Memory Usage by Dataset and Support")
plt.xlabel("Dataset Support")
plt.ylabel("Memory (MB)")
plt.tight_layout()
plt.savefig("plots/peak_memory_usage.png")
plt.close()

print("Plots generated and saved in the 'plots/' folder.")
