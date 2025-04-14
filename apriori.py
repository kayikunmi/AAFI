import sys
import os
import time
import tracemalloc
from collections import defaultdict
from itertools import combinations

class Apriori:
    def __init__(self, minsup):
        self.minsup = minsup # minimum support threshold
        self.horizontal_db = [] # horizontal transactions: list of sets of items
        self.frequent_itemsets = [] # stores frequent itemsets and their support count
        self.confident_rules = [] #list of association rules (A → B)
            # TODO make the confidence rules
        self.stats = {} #stores performance metrics (runtime, memory)

 # Load data in horizontal format
    def load_horizontal_data(self, filepath):
        start_time = time.time()
        transactions = []

        with open(filepath, 'r') as f:
            for line in f:
                    transaction = frozenset(line.strip().split(" "))
                    transactions.append(transaction)

        self.stats["load_time"] = time.time() - start_time
        return transactions

# Compute supports for a set of candidates
    def get_candidate_supports(self, candidates):
        support_dict = defaultdict(int)
        for transaction in self.horizontal_db:
            for candidate in candidates:
                if set(candidate).issubset(transaction):
                    support_dict[candidate] += 1
        return support_dict
    
    # // get supports of a set of candidates
    #     // takes a set of candidates (which are itemsets)
    #     // returns a map of candidates to their supports
    # private HashMap<HashSet<Integer>, Integer> candidateSupport(HashSet<HashSet<Integer>> candidates){
    #     // go through the transaction collection and find the supports of the given items
    #     // make dictionary that includes the supports of every element of the given size
    #     var supportDict = new HashMap<HashSet<Integer>, Integer>();
    #     // for every transaction in the collection
    #     for (HashSet<Integer> transaction : transactions){
    #         // for every candidate
    #         for(HashSet<Integer> candidate : candidates){
    #             // if the transaction contains all the items in the candidate
    #             if(transaction.containsAll(candidate)){
    #                 // add 1 to the appropriate support
    #                 supportDict.merge(candidate, 1, Integer::sum);
    #             }
    #         }
    #     }
    #     // return candidates and their supports
    #     return supportDict;
    # }

    # def enumerate(self, items, support_dict, k):
    #     #print("enumerating")
    #     # TODO maybe move the adding to freq itemsets to the top of the next recursion
    #     # add the frequent itemsets from the passed itemsets
    #     self.frequent_itemsets += [(item, support_dict[item]) for item in items]
    #     #print("items", items)
    #     #print("freq", self.frequent_itemsets)

    #     # get candidates
    #     candidates = set()
    #     noncandidates = set()
    #     # for every pair of siblings, add their union as a candidate
    #     # for all the items in the layer
    #     #if items:
    #         #for item in items[:-1]:
    #             #if support >= self.minsup:
    #             #self.frequent_itemsets.append(item, support)
    #             # paired with all the other items in the layer
    #             #for other_item in items[1:]:
    #     items_set = set(items)

    #     #print("items", items)

    #     while items:
    #         item = items.pop()
    #         for other_item in items:
    #             #print("item", item, "other item", other_item)
    #             # get the union of the items
    #             union = item | other_item
    #             # if the union is the right size
    #             if len(union) == k+1:
    #                 # TODO better comment
    #                 # no need to check candidate further if its made of size 1 items
    #                 if k == 1:
    #                     candidates.add(frozenset(union))
    #                 else:
    #                     # if it hasn't already been generated as a candidate or noncandidate
    #                     if not (union in candidates) and not (union in noncandidates):
    #                         # check if it's a valid candidate
    #                         # if all the size k-1 subsets of the union are frequent then it is a candidate 
    #                         all_freq = True
    #                         for union_item in union:
    #                             if not((union - set(union_item)) in items_set):
    #                                 noncandidates.add(frozenset(union))
    #                                 all_freq = False
    #                                 break
    #                         if all_freq:
    #                             candidates.add(frozenset(union))
    #             # print("current candidates", candidates)
    #             # print("current items", items)
    #             # print("current item", item)

    #     # if there are any candidates to process
    #     if candidates:
    #         #print("YES")
    #         new_support_dict = self.get_candidate_supports(candidates)
    #         #print("candidate supports", new_support_dict)

    #         # get the frequent itemsets from the candidates
    #         # TODO definitely exists a more efficient way to do this/phrase it
    #         items = [item for item in new_support_dict if new_support_dict[item] >= minsup]
            
    #         if items:
    #             #print("items", items)
    #             # continue with only the frequent itemsets and the supports of the candidates
    #             self.enumerate(items, new_support_dict, k+1)

# Jank Apriori
    def enumerate(self):
        # count supports of frequent 1-itemsets
        support_dict = defaultdict(int)
        for transaction in self.horizontal_db:
            for item in transaction:
                support_dict[frozenset([item])] += 1

        # filter 1-itemsets by minsup
        items = [frozenset(item) for item in support_dict if support_dict[item] >= self.minsup]
        items.sort()

        # add the frequent itemsets and their supports into the frequent itemsets
        self.frequent_itemsets += [(item, support_dict[item]) for item in items]

        # size of itemsets in current layer
        k = 1

        # while there are still itemsets to attempt to generate candidates from
        while(len(items) > 0):
            # reset candidates and noncandidates
            candidates = set()
            noncandidates = set()
            # make set of items for easy frequent item checking
            items_set = set(items)

            # for every pair of itemsets...
            for i in range(0,len(items)-1):
                for j in range(1,len(items)):
                    # get the union of the items
                    union = items[i] | items[j]
                    # if the union is the right size...
                    if len(union) == k+1:
                        # no need to check candidate further if its made of size 1 items
                        if k == 1:
                            candidates.add(frozenset(union))
                        else:
                            # if it hasn't already been generated as a candidate or noncandidate...
                            if not (union in candidates) and not (union in noncandidates):
                                # check if it's a valid candidate
                                # if all the size k-1 subsets of the union are frequent then it is a candidate 
                                all_freq = True
                                for union_item in union:
                                    if not((union - set([union_item])) in items_set):
                                        noncandidates.add(frozenset(union))
                                        all_freq = False
                                        break
                                if all_freq:
                                    candidates.add(frozenset(union))

            # increment itemset size
            k += 1
            # count candidate supports
            support_dict = self.get_candidate_supports(candidates)
            # update items
            items = [frozenset(item) for item in support_dict if support_dict[item] >= self.minsup]
            # add the frequent itemsets and their supports into the frequent itemsets
            self.frequent_itemsets += [(item, support_dict[item]) for item in items]

# Run the algorithm
    def run(self, filepath):
        tracemalloc.start() #start memory tracking
        self.horizontal_db = self.load_horizontal_data(filepath) #load dataset

        start_time = time.time() # start timing

        self.enumerate() #run apriori
        self.stats["mining_time"] = time.time() - start_time #track mining runtime
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
                continue #no rule possible for 1-itemsets
            for i in range(1, len(itemset)):
                for A in combinations(itemset, i):
                    B = set(itemset) - set(A)
                    A_str = " ".join(sorted(A))
                    A_support = itemset_dict.get(A_str, 0)
                    if A_support > 0:
                        conf = support / A_support
                        if conf >= minconf:
                            self.confident_rules.append((list(A), list(B), conf)) #add rule A → B

        self.stats["rule_gen_time"] = time.time() - start_time #track rule generation time

# Output frequent itemsets and performance metrics
    def print_results(self, input_path):
        dataset_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = f"Results/{dataset_name}_apriori_output.txt"
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

 # Count number of transactions (for scalability reporting)
    def estimate_num_transactions(self):
        return len(self.horizontal_db)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python apriori.py <horizontal_data_file> <minsup> [<minconf>]")
        sys.exit(1)

    filepath = sys.argv[1]
    minsup = int(sys.argv[2])
    minconf = float(sys.argv[3]) if len(sys.argv) > 3 else 0.6

    apriori = Apriori(minsup)
    apriori.run(filepath)
    apriori.generate_association_rules(minconf)
    apriori.print_results(filepath)