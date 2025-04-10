import java.util.ArrayList;
import java.util.HashSet;
import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;
import java.util.HashMap;

/* Apriori
 * runs Apriori frequent itemset counting algorithm
 */
public class Apriori {
    // store the transaction list
    private ArrayList<HashSet<Integer>> transactions;
    private Integer transSize;

    // Constructor for Apriori
        // takes an arraylist of transactions
    Apriori(ArrayList<HashSet<Integer>> transactions){
        this.transactions = transactions;
        this.transSize = transactions.size();
    }

    // main method to read in dataset and run Apriori algorithm
        // takes one command line arg which is a path to the dataset
    public static void main(String[] args) {
        // code for reading command line arguments
            // if there's the correct number of arguments
            if (args.length == 2){
                // threshold and path
                double thres = Double.parseDouble(args[0]);
                String path = args[1];
                // check that there's a valid file at that path
                try{
                    File data_file = new File(path);
                    Scanner data_scanner = new Scanner(data_file);

                    // if the file exists, read in and process the transactions
                    System.out.println("Read in transactions");
                    double program_start = System.currentTimeMillis(); // start timing program run
                    var transactions = new ArrayList<HashSet<Integer>>();
                    String transactionList;
                    HashSet<Integer> transaction;
                    while (data_scanner.hasNextLine()) {
                        transactionList = data_scanner.nextLine();
                        transaction = toSet(transactionList);
                        transactions.add(transaction);
                    }
                    data_scanner.close();

                    System.out.println("Transactions read in");
                    
                    // run the algorithm using the file
                    Apriori algo = new Apriori(transactions);
                    // time the algorithm run time
                    double algo_start = System.currentTimeMillis();
                    ArrayList<HashSet<Integer>> tracker = algo.freqItemsets(thres);
                    double end = System.currentTimeMillis();

                    // output the itemset result
                    // TODO make this nicer
                    System.out.println(tracker);

                    // output measurements
                    System.out.println("Frequent itemsets: " + tracker.size());
                    System.out.println("Run time (milliseconds): " + (end-program_start) + " (includes reading transactions)");
                    System.out.println("Run time (milliseconds): " + (end-algo_start) + " (excludes reading transactions)");

                } catch(FileNotFoundException e){
                    System.out.println("Invalid file name: " + path);
                }
            // else, let user know they didn't use function correctly
            } else {
                System.out.println("Usage: Apriori _minimum.frequency.threshold_ _path.to.dataset_");
            }
    }

    // gets frequent itemsets from the transactions given a frequency threshold
        // takes a minimum frequency threshold
        // returns frequent itemsets
    public ArrayList<HashSet<Integer>> freqItemsets(double minFreq){

        // find frequent 1-itemsets and put them in the frequent itemset tracker
        System.out.println("Counting 1-itemsets");

        // go through the transaction collection and find the supports of every single item
        var supportDict = new HashMap<HashSet<Integer>, Integer>();
        // for every transaction in the collection
        for (HashSet<Integer> transaction : transactions){
            // for every item in the transaction, add 1 to approriate support
            for (Integer item : transaction){
                var itemset1 = new HashSet<Integer>();
                itemset1.add(item);
                supportDict.merge(itemset1, 1, Integer::sum);
            }
        }

        // make frequent itemsets tracker
        var tree = new ArrayList<HashSet<Integer>>();
        // go through the support dictionary and get items above the threshold
        getFreqSets(tree, supportDict, minFreq);
        // create variables to track "layers" in frequent itemsets tracker
            // layer is collection of all frequent itemsets of a given size
        var layerStart = 0;
        var layerSize = tree.size();

        System.out.println("Counting larger itemsets' supports");

        // initialize variables used in generating each new layer of the freq itemset tracker
        HashSet<HashSet<Integer>> layer = new HashSet<HashSet<Integer>>(tree);
        HashSet<HashSet<Integer>> candidates; // candidate frequent itemsets
        HashSet<HashSet<Integer>> nonCandidates; // itemsets that cannot be frequent
        int k = 1; // size of itemsets in the current layer

        // while there are still things in the layer to generate more frequent itemsets from...
        while(layerSize > 0){

            // reset candidates and noncandidates to generate new ones for the next layer
            candidates = new HashSet<HashSet<Integer>>();
            nonCandidates = new HashSet<HashSet<Integer>>();

            // for every pair of siblings, add their union as a candidate
            for(int i = layerStart; i < (layerStart+layerSize)-1; i++){
                for(int j = i+1; j < (layerStart+layerSize); j++){
                    // get the siblings
                    var set1 = tree.get(i);
                    var set2 = tree.get(j);
                    // get the union
                    var union = new HashSet<Integer>();
                    union.addAll(set1);
                    union.addAll(set2);

                    // determine if their union is a valid candidate
                    // if it's the right size (one bigger than the itemsets that make it up)
                    if(union.size()==k+1) {
                        // if the itemset size is 2 then no need for pre-processing of candidates
                            // (in order for it to be generated its component 1itemsets must necessarily be frequent)
                        if (k == 1) {
                            candidates.add(union);
                        } else {
                            // if it has not already been generated as a candidate or non-candidate
                            if (!candidates.contains(union) && !nonCandidates.contains(union)) {
                                // check if it's a valid candidate
                                // for every item in the union, see if the subset of the union without the item is frequent
                                    // if not, then add it to the nonCandidates
                                    // if so, then add it to the candidates
                                boolean allFreq = true;
                                HashSet<Integer> kmer;
                                for(Integer itemset1 : union){
                                    kmer = new HashSet<Integer>(union);
                                    kmer.remove(itemset1);
                                    //System.out.println("kmer: " + kmer);
                                    if (!layer.contains(kmer)){
                                        nonCandidates.add(union);
                                        allFreq = false;
                                        break;
                                    }
                                }
                                if(allFreq){
                                    candidates.add(union);
                                }
                            }
                        }
                    }
                }
            }

            // move onto the next layer
            layerStart += layerSize;
            k++;

            // count candidate support
            layerSize = getFreqSets(tree, candidateSupport(candidates), minFreq);

            // hold onto the current layer as a set
            layer = new HashSet<>(tree.subList(layerStart,layerStart+layerSize));

            System.out.println("Done counting layer");
        }

        // return frequent itemset counter
        return tree;
    }

    // get supports of a set of candidates
        // takes a set of candidates (which are itemsets)
        // returns a map of candidates to their supports
    private HashMap<HashSet<Integer>, Integer> candidateSupport(HashSet<HashSet<Integer>> candidates){
        // go through the transaction collection and find the supports of the given items
        // make dictionary that includes the supports of every element of the given size
        var supportDict = new HashMap<HashSet<Integer>, Integer>();
        // for every transaction in the collection
        for (HashSet<Integer> transaction : transactions){
            // for every candidate
            for(HashSet<Integer> candidate : candidates){
                // if the transaction contains all the items in the candidate
                if(transaction.containsAll(candidate)){
                    // add 1 to the appropriate support
                    supportDict.merge(candidate, 1, Integer::sum);
                }
            }
        }
        // return candidates and their supports
        return supportDict;
    }

    // get frequent itemsets
        // (go through the support dictionary and add itemsets above the minimum frequency threshold into a list)
        // takes a frequent itemset tracker, a map of itemsets to their supports, and a minimum frequency threshold
        // returns the number of frequent items that were added
    private int getFreqSets(ArrayList<HashSet<Integer>> enumTree, HashMap<HashSet<Integer>, Integer> supportDict, double minFreq){
        // count number of itemsets added
        var layerSize = 0;
        // for every key in the support dictionary, put the relevant itemsets into the tracker
        for(HashSet<Integer> itemset : supportDict.keySet()){
            double freq = (double) supportDict.get(itemset) / (double) transSize; // frequency = support divided by number of transactions in collection
            // if the itemset's freq is greater than the threshold, put the itemset in the tracker
            if(freq >= minFreq) {
                enumTree.add(itemset);
                layerSize ++;
            }
        }

        // return number of frequent items that were added
        return layerSize;
    }

    // convert String form of transaction into hashset of integers
        // takes itemset as a string
        // returns itemset as a hashset
    public static HashSet<Integer> toSet(String itemset) {
        // make a new hashset
        var setTransaction = new HashSet<Integer>();
        // split the transaction into integers and add them into the set
        var strItems = itemset.split("\\s");
        // parse each of the items into integers and add into the current transaction hash
        for (String strItem : strItems) {
            setTransaction.add(Integer.parseInt(strItem));
        }
        return setTransaction;
    }
}

