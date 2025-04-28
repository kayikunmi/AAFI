import sys
import os
import time
import tracemalloc
from collections import defaultdict
from itertools import combinations

class dEclat:
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
            item, support, diffset = items.pop()
            if support >= self.minsup:
                new_prefix = prefix + [item]
                self.frequent_itemsets.append((new_prefix, support)) #record as a frequent itemset
                new_items = []
                for other_item, _ , other_diffset in items:
                    # get the difference between the diffsets for the prefix and the item
                    difference = set(diffset) - set(other_diffset) # candidate difference between the diffsets
                    # support is difference between prefix's support and the diffset length
                    new_support = support - len(difference)
                    if new_support >= self.minsup:
                        new_items.append((other_item, new_support, difference))

                self.bottom_up_eclat(new_prefix, new_items) #recurse on new conditional class

    # Count number of unique transactions (for scalability reporting)
    def estimate_num_transactions(self):
        all_tids = set()
        for tids in self.vertical_db.values():
            all_tids.update(tids)
        return len(all_tids)

    def run(self, filepath):
        tracemalloc.start() #start memory tracking
        self.vertical_db = self.load_vertical_data(filepath) #load dataset
 
        #filter 1-itemsets by minsup
        items = [(item, tids) for item, tids in self.vertical_db.items() if len(tids) >= self.minsup]
        items.sort()  #sort for prefix order

        # intersect the full tidlist with the tidlist for each 1-itemset to get the diffsets for them
        # each entry in the items list is now (item, diffset, support)

        # make the full tidlist (numbers 0 to # of horizontal db entries-1)
        all_tids = set(range(0,self.estimate_num_transactions()))
        
        # for each 1-itemset, get it and its tidlist
            # length of the tidlist is the support
            # diffset is set difference between all tids and the item's tidlist (total tids - item tidlist)
        # filter 1-itemsets by min sup
        items = [(item, len(tids), (set(tids)-all_tids)) for item, tids in self.vertical_db.items() if len(tids) >= self.minsup]

        start_time = time.time()
        self.bottom_up_eclat([], items) #run bottom up Eclat algorithm
        self.stats["mining_time"] = time.time() - start_time  #track mining runtime
        self.stats["peak_memory_MB"] = round(tracemalloc.get_traced_memory()[1] / (1024 * 1024), 2)
        tracemalloc.stop()

    def print_results(self, input_path):
        dataset_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = f"Results/{dataset_name}_declat_{self.minsup}_output.txt"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w") as f:
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
    declat.run(filepath)
    declat.print_results(filepath)