import os
import re
import csv

RESULTS_DIR = "Results"
OUTPUT_CSV = "experiment_summary.csv"  

def parse_output_file(filepath):
    print(f">>>Processing: {os.path.basename(filepath)}<<<")
    with open(filepath, "r") as f:
        lines = f.readlines()

    stats = {
        "filename": os.path.basename(filepath),
        "transactions": None,
        "min_support": None,
        "mining_time": None,
        "peak_memory_MB": None,
        "rule_gen_time": None,
        "load_time": None,
        "total_runtime": None,
        "algorithm": None,
        "dataset": None,
        "support_value": None,
    }

    #Match files with the expected naming convention
    match = re.match(r"(.+?)_(vertical|horizontal)_(apriori|eclat|declat)_(\d+)_output\.txt", stats["filename"])
    if match:
        dataset, _, algo, support = match.groups()
        stats["dataset"] = dataset
        stats["algorithm"] = algo
        stats["support_value"] = int(support)
    else:
        print("!Skipping unrecognized file format!")
        return None

    for line in lines:
        if "Transactions:" in line:
            stats["transactions"] = int(re.findall(r"\d+", line)[0])
        elif "Min Support:" in line:
            stats["min_support"] = int(re.findall(r"\d+", line)[0])
        elif "Mining Time:" in line:
            stats["mining_time"] = float(re.findall(r"[\d.]+", line)[0])
        elif "Peak Memory" in line:
            stats["peak_memory_MB"] = float(re.findall(r"[\d.]+", line)[0])
        elif "Rule Gen Time" in line:
            stats["rule_gen_time"] = float(re.findall(r"[\d.]+", line)[0])
        elif "Load Time" in line:
            stats["load_time"] = float(re.findall(r"[\d.]+", line)[0])
        elif "Total Runtime" in line:
            stats["total_runtime"] = float(re.findall(r"[\d.]+", line)[0])

    return stats

def main():
    entries = []

    for filename in os.listdir(RESULTS_DIR):
        if filename.endswith("_output.txt"):
            filepath = os.path.join(RESULTS_DIR, filename)
            stats = parse_output_file(filepath)
            if stats:
                entries.append(stats)

    if not entries:
        print("!No result files matched!")
        return

    #write CSV 
    with open(OUTPUT_CSV, "w", newline="") as csvfile:
        fieldnames = [
            "filename", "dataset", "algorithm", "support_value",
            "transactions", "min_support", "mining_time",
            "rule_gen_time", "load_time", "total_runtime", "peak_memory_MB"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in entries:
            writer.writerow(entry)

    print(f"===Experiment summary written to ./{OUTPUT_CSV}===")

if __name__ == "__main__":
    main()
