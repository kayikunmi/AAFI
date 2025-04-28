import subprocess
import time

# Paths to your algorithms
apriori_script = "apriori.py"
eclat_script = "eclat.py"
declat_script = "dEclat.py"

# Datasets you want to use
datasets = [
    ("Datasets/chess_horizontal.dat", 0.8),
    ("Datasets/mushroom_horizontal.dat", 0.8),
    ("Datasets/retail_horizontal.dat", 0.5)
]

# Algorithms to run
algorithms = [
    ("Apriori", apriori_script),
    ("Eclat", eclat_script),
    ("dEclat", declat_script)
]

def run_experiment(algo_name, script_name, dataset, minsup):
    print(f"\n=== Running {algo_name} on {dataset} with minsup {minsup} ===")
    start_time = time.time()
    
    # Run the Python script with arguments
    result = subprocess.run(["python3", script_name, dataset, str(minsup)], capture_output=True, text=True)
    
    # Print the output (optional, you can suppress if too verbose)
    print(result.stdout)
    if result.stderr:
        print("ERROR:", result.stderr)
    
    elapsed = time.time() - start_time
    print(f"--- {algo_name} completed in {elapsed:.2f} seconds ---\n")

def main():
    print("Starting experiments...")
    overall_start = time.time()

    for dataset, minsup in datasets:
        for algo_name, script_name in algorithms:
            run_experiment(algo_name, script_name, dataset, minsup)
    
    overall_elapsed = time.time() - overall_start
    print(f"All experiments completed in {overall_elapsed:.2f} seconds.")

if __name__ == "__main__":
    main()
