import sys
import os
import time
import tracemalloc
from collections import defaultdict
from itertools import combinations

class Eclat:
    def __init__(self, minsup):
        self.minsup = minsup #minimum support threshold
        self.vertical_db = {} #vertical TID-lists: item -> set of transaction IDs
        self.frequent_itemsets = [] #stores frequent itemsets and their support count
        self.confident_rules = [] #list of association rules (A → B)
        self.stats = {} #stores performance metrics (runtime, memory)

    # Load data in vertical format
    def load_vertical_data(self, filepath):
        start_time = time.time()
        tid_lists = defaultdict(set)

        with open(filepath, 'r') as f:
            for line in f:
                if ':' in line:
                    item, tids = line.strip().split(':', 1)
                    tid_list = tids.strip().strip(',').split(',')  # Remove trailing comma and split
                    tid_lists[item.strip()] = set(tid_list)

        self.stats["load_time"] = time.time() - start_time
        return dict(tid_lists)


    # Compute support for an itemset by intersecting their TID-lists
    def compute_support(self, items):
        if not items:
            return 0, set()
        tids = self.vertical_db[items[0]]
        for item in items[1:]:
            tids = tids & self.vertical_db[item] #set intersection of TID-lists via HashSet
        return len(tids), tids

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

    def run(self, filepath):
        tracemalloc.start() #start memory tracking
        self.vertical_db = self.load_vertical_data(filepath) #load dataset
 
        #filter 1-itemsets by minsup
        items = [(item, tids) for item, tids in self.vertical_db.items() if len(tids) >= self.minsup]
        items.sort()  #sort for prefix order

        start_time = time.time()
        self.bottom_up_eclat([], items) #run bottom up Eclat algorithm
        self.stats["mining_time"] = time.time() - start_time  #track mining runtime
        self.stats["peak_memory_MB"] = round(tracemalloc.get_traced_memory()[1] / (1024 * 1024), 2)
        tracemalloc.stop()

     # Generate confident association rules from frequent itemsets
    def generate_association_rules(self, minconf=0.6):
        start_time = time.time()
        itemset_dict = {
            " ".join(sorted(itemset)): support
            for itemset, support in self.frequent_itemsets
        }

        for itemset, support in self.frequent_itemsets:
            if len(itemset) < 2:
                continue  #no rule possible for 1-itemsets
            for i in range(1, len(itemset)):
                for A in combinations(itemset, i):
                    B = set(itemset) - set(A)
                    A_str = " ".join(sorted(A))
                    A_support = itemset_dict.get(A_str, 0)
                    if A_support > 0:
                        conf = support / A_support
                        if conf >= minconf:
                            self.confident_rules.append((list(A), list(B), conf))  #add rule A → B

        self.stats["rule_gen_time"] = time.time() - start_time #track rule generation time

    def print_results(self, input_path):
        dataset_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = f"Results/{dataset_name}_eclat_output.txt"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w") as f:
            f.write("== Frequent Itemsets ==\n")
            for itemset, support in self.frequent_itemsets:
                f.write(f"{' '.join(itemset)} ({support})\n")

            f.write("\n== Confident Association Rules ==\n")
            for A, B, conf in self.confident_rules:
                f.write(f"{' '.join(A)} => {' '.join(B)} (conf: {conf:.2f})\n")

            f.write("\n== Execution Statistics ==\n")
            f.write(f"Transactions: {self.estimate_num_transactions()}\n")
            f.write(f"Min Support: {self.minsup}\n")
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
        print("Usage: python eclat.py <vertical_data_file> <minsup> [<minconf>]")
        sys.exit(1)

    filepath = sys.argv[1]
    minsup = int(sys.argv[2])
    minconf = float(sys.argv[3]) if len(sys.argv) > 3 else 0.6

    eclat = Eclat(minsup)
    eclat.run(filepath)
    eclat.generate_association_rules(minconf)
    eclat.print_results(filepath)

