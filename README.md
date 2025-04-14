# AAFI

COSC- 254 Data Mining

Alternate Algorithims for Frequent Itemsets

Initially, the ***Datasets folder*** contains the following compressed datasets: chess.dat.gz, retail.dat.gz, connect.dat.gz, and mushroom.dat.gz. Running ***convert.py*** generates:

* chess_horizontal.dat and chess_vertical.dat
* retail_horizontal.dat and retail_vertical.dat
* connect_horizontal.dat and connect_vertical.dat
* mushroom_horizontal.dat and mushroom_vertical.dat

*_horizontal.dat → Used for Apriori while _vertical.dat → Used for Eclat & dEclat.*

**APRIORI:**

* File: `apriori.py` (Python) or `Apriori.java` (Java)
* Requires horizontal format files (`_horizontal.dat`)
* Uses candidate generation and pruning to find frequent itemsets
* Usage: python apriori.py Datasets/`<dataset>`_horizontal.dat `<support>`

**ECLAT:**

* File: `eclat.py` (Python)
* Uses a recursive bottom-up traversal of the itemset lattice
* Parses vertical format lines like: `item: tid1,tid2,..`
* Logs performance:
  * Load time
  * Mining time
  * Rule generation time
  * Peak memory (via `tracemalloc`)
  * Total transactions processed
* Usage: python eclat.py Datasets/`<dataset>`_vertical.dat `<minsup> <conf>`
* Results saved to: `Results/<dataset>_eclat_output.txt`

*Folder Structure:*

.
├── Apriori.java

├── apriori.py

├── convert.py

├── eclat.py

├── README.md

├── Datasets/

│   ├── chess.dat.gz

│   ├── chess_horizontal.dat

│   ├── chess_vertical.dat

│   ├── connect.dat.gz

│   ├── connect_horizontal.dat

│   ├── connect_vertical.dat

│   ├── mushroom.dat.gz

│   ├── mushroom_horizontal.dat

│   ├── mushroom_vertical.dat

│   ├── retail.dat.gz

│   ├── retail_horizontal.dat

│   └── retail_vertical.dat

└── Results/
    ├── chess_eclat_output.txt
    ├── connect_eclat_output.txt
    ├── mushroom_eclat_output.txt
    └── retail_eclat_output.txt

3 directories, 17 files
