import sys
import os
import time
import tracemalloc
from collections import defaultdict

class dEclat:
    def __init__(self, minsup):
        self.minsup = minsup #minimum support threshold
        self.vertical_db = {} #vertical TID-lists: item -> set of transaction IDs
        self.frequent_itemsets = [] #stores frequent itemsets and their support count
        self.stats = {} #stores performance metrics (runtime, memory)
        self.command_str = "" #command to run

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
    
    # Bottom-up traversal using prefix extension and diffsets
    def bottom_up_declat(self, prefix, items):
        while items:
            item, support, diffset = items.pop()
            if support >= self.minsup:
                new_prefix = prefix + [item]
                self.frequent_itemsets.append((new_prefix, support)) #record as a frequent itemset
                new_items = []
                for other_item, _ , other_diffset in items:
                    # get the difference between the diffsets for the prefix and the item
                    difference = other_diffset - diffset
                    # support is difference between prefix's support and the diffset length
                    new_support = support - len(difference)
                    if new_support >= self.minsup:
                        new_items.append((other_item, new_support, difference))
                self.bottom_up_declat(new_prefix, new_items) #recurse on new conditional class

    # Count number of unique transactions (for scalability reporting)
    def estimate_num_transactions(self):
        all_tids = set()
        for tids in self.vertical_db.values():
            all_tids.update(tids)
        return len(all_tids)

    def run(self, filepath):
        tracemalloc.start() #start memory tracking
        self.vertical_db = self.load_vertical_data(filepath) #load dataset
 
        # full possible tidlist (numbers 1 to # of horizontal db entries)
        all_tids = set(map(str, range(1,self.estimate_num_transactions()+1)))

        # filter 1-itemsets by min sup
            # each entry in the items list is (item, support, diffset)
            # support is length of the tidlist
            # diffset is set difference between all tids and the item's tidlist (total tids - item tidlist)
        items = [(item, len(tids), (all_tids - tids)) for item, tids in self.vertical_db.items() if len(tids) >= self.minsup]

        start_time = time.time()
        self.bottom_up_declat([], items) #run bottom up Eclat algorithm
        self.stats["mining_time"] = time.time() - start_time  #track mining runtime
        self.stats["peak_memory_MB"] = round(tracemalloc.get_traced_memory()[1] / (1024 * 1024), 2)
        tracemalloc.stop()

    def print_results(self, input_path):
        dataset_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = f"Results/{dataset_name}_declat_{self.minsup}_output.txt"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w") as f:
            f.write(f"== Command ==\n{self.command_str}\n\n")

            f.write("== Frequent Itemsets ==\n")
            for itemset, support in self.frequent_itemsets:
                f.write(f"{' '.join(itemset)} ({support})\n")

            f.write("\n== Execution Statistics ==\n")
            f.write(f"Transactions: {self.estimate_num_transactions()}\n")
            f.write(f"Min Support: {self.minsup}\n")
            for k, v in self.stats.items():
                label = k.replace("_", " ").title()
                f.write(f"{label}: {v:.4f} seconds\n" if 'time' in k else f"{label}: {v} MB\n")

        print(f"Results written to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python dEclat.py <vertical_data_file> <minsup>")
        sys.exit(1)

    filepath = sys.argv[1]
    minsup = int(sys.argv[2])

    declat = dEclat(minsup)
    declat.command_str = f"python {' '.join(sys.argv)}"  #store command line
    declat.run(filepath)
    declat.print_results(filepath)