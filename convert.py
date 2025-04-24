import os
import time
import gzip
from collections import defaultdict

DATASET_DIR = "Datasets"

def extract_gz_file(gz_path, horizontal_path):
    with gzip.open(gz_path, 'rt') as gz_file, open(horizontal_path, 'w') as out_file:
        for line in gz_file:
            out_file.write(line)

def convert_to_vertical_format(horizontal_path, vertical_path):
    vertical_db = defaultdict(set)

    with open(horizontal_path, 'r') as file:
        for tid, line in enumerate(file):
            items = line.strip().split()
            for item in items:
                vertical_db[item].add(str(tid))

    with open(vertical_path, 'w') as out_file:
        for item, tids in sorted(vertical_db.items()):
            out_file.write(f"{item}: {','.join(sorted(tids))}\n")

def process_dataset(base_name):
    gz_path = os.path.join(DATASET_DIR, f"{base_name}.dat.gz")
    horizontal_path = os.path.join(DATASET_DIR, f"{base_name}_horizontal.dat")
    vertical_path = os.path.join(DATASET_DIR, f"{base_name}_vertical.dat")

    print(f"\n[INFO] Processing {base_name}.dat.gz")

    start_time = time.time()

    # Step 1: Extract horizontal format
    extract_gz_file(gz_path, horizontal_path)
    print(f"✓ Extracted to {horizontal_path}")

    # Step 2: Convert to vertical format
    convert_to_vertical_format(horizontal_path, vertical_path)
    print(f"✓ Converted to {vertical_path}")

    duration = time.time() - start_time
    print(f"✓ Total conversion time: {duration:.2f} seconds")

if __name__ == "__main__":
    datasets = ["chess", "connect", "mushroom", "retail"]

    for ds in datasets:
        process_dataset(ds)


'''
conversion times:
[INFO] Processing chess.dat.gz
✓ Extracted to Datasets/chess_horizontal.dat
✓ Converted to Datasets/chess_vertical.dat
✓ Total conversion time: 0.06 seconds

[INFO] Processing connect.dat.gz
✓ Extracted to Datasets/connect_horizontal.dat
✓ Converted to Datasets/connect_vertical.dat
✓ Total conversion time: 2.06 seconds

[INFO] Processing mushroom.dat.gz
✓ Extracted to Datasets/mushroom_horizontal.dat
✓ Converted to Datasets/mushroom_vertical.dat
✓ Total conversion time: 0.10 seconds

[INFO] Processing retail.dat.gz
✓ Extracted to Datasets/retail_horizontal.dat
✓ Converted to Datasets/retail_vertical.dat
✓ Total conversion time: 0.58 seconds
'''