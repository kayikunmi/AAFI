import sys
import os
import time
import tracemalloc
from collections import defaultdict

class Eclat:
    def __init__(self):
        self.minsup = 0 #frequency × transactions
        self.vertical_db = {} #Item → set of TIDs (vertical format)
        self.frequent_itemsets = [] #list of freqItemsets
        self.stats = {} #timing and memory info
        self.command_str = "" #command to run 

    # Load data in vertical format
    def load_vertical_data(self, filepath):
        start_time = time.time()
        tid_lists = defaultdict(set)

        with open(filepath, 'r') as f:
            for line in f:
                if ':' in line:
                    item, tids = line.strip().split(':', 1)
                    tid_list = tids.strip().strip(',').split(',')
                    tid_lists[item.strip()] = set(tid_list)

        self.stats["load_time"] = time.time() - start_time
        return dict(tid_lists)

    # Bottom-up traversal using prefix extension and tid-list intersections
    def bottom_up_eclat(self, prefix, items):
        while items:
            item, tidlist = items.pop()
            support = len(tidlist)
            if support >= self.minsup:
                new_prefix = prefix + [item]
                self.frequent_itemsets.append((new_prefix, support)) #record as a frequent itemset

                new_items = []
                for other_item, other_tidlist in items:
                    intersected = tidlist & other_tidlist #candidate intersection
                    if len(intersected) >= self.minsup:
                        new_items.append((other_item, intersected))

                self.bottom_up_eclat(new_prefix, new_items) #recurse on new conditional class

    def run(self, filepath, minsup_fraction):
        tracemalloc.start()
        self.vertical_db = self.load_vertical_data(filepath) #load dataset

        total_txns = self.estimate_num_transactions()
        self.minsup = int(minsup_fraction * total_txns)

         #filter 1-itemsets by minsup
        items = [(item, tids) for item, tids in self.vertical_db.items() if len(tids) >= self.minsup]
        items.sort()

        start_time = time.time()
        self.bottom_up_eclat([], items) #run bottom up Eclat algorithm
        self.stats["mining_time"] = time.time() - start_time #track mining runtime
        self.stats["peak_memory_MB"] = round(tracemalloc.get_traced_memory()[1] / (1024 * 1024), 2)
        tracemalloc.stop()

    def print_results(self, input_path):
        dataset_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = f"Results/{dataset_name}_eclat_output.txt"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w") as f:
            f.write(f"== Command ==\n{self.command_str}\n\n")
            f.write("== Frequent Itemsets ==\n")
            for itemset, support in self.frequent_itemsets:
                f.write(f"{' '.join(itemset)} ({support})\n")

            f.write("\n== Execution Statistics ==\n")
            f.write(f"Transactions: {self.estimate_num_transactions()}\n")
            f.write(f"Minimum Frequency: {self.minsup} (minsup fraction applied)\n")
            for k, v in self.stats.items():
                label = k.replace("_", " ").title()
                f.write(f"{label}: {v:.4f} seconds\n" if 'time' in k else f"{label}: {v} MB\n")

        print(f"Results written to: {output_path}")

    # Count number of unique transactions (for scalability reporting)
    def estimate_num_transactions(self):
        all_tids = set()
        for tids in self.vertical_db.values():
            all_tids.update(tids)
        return len(all_tids)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python eclat.py <vertical_data_file> <minsup_fraction>")
        sys.exit(1)

    filepath = sys.argv[1]
    minsup_fraction = float(sys.argv[2])  

    eclat = Eclat()
    eclat.command_str = f"python {' '.join(sys.argv)}"  #store command line 
    eclat.run(filepath, minsup_fraction)
    eclat.print_results(filepath)
