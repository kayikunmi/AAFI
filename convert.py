import os
import gzip
from collections import defaultdict

DATASET_FOLDER = "Datasets"

#Extract .gz files
def extract_gz_file(gz_file_path, output_file_path):
    with gzip.open(gz_file_path, 'rt') as gz_file, open(output_file_path, 'w') as out_file:
        for line in gz_file:
            out_file.write(line)

#Function to convert from horizontal to vertical
def convert_to_vertical_format(horizontal_path, vertical_path):
    vertical_db = defaultdict(set)

    with open(horizontal_path, 'r') as file:
        for tid, line in enumerate(file):
            items = line.strip().split()
            for item in items:
                vertical_db[item].add(tid)

    with open(vertical_path, 'w') as out_file:
        for item, tids in sorted(vertical_db.items()):
            out_file.write(f"{item}: {','.join(map(str, sorted(tids)))}\n")

#Process gz files
for filename in os.listdir(DATASET_FOLDER):
    if filename.endswith(".gz"):
        gz_file_path = os.path.join(DATASET_FOLDER, filename)
        dataset_name = filename.replace(".dat.gz", "")
        
        #file paths
        horizontal_path = os.path.join(DATASET_FOLDER, f"{dataset_name}_horizontal.dat")
        vertical_path = os.path.join(DATASET_FOLDER, f"{dataset_name}_vertical.dat")

        #Extract and convert
        print(f"{filename}: {dataset_name}_horizontal.dat and {dataset_name}_vertical.dat")
        extract_gz_file(gz_file_path, horizontal_path)
        convert_to_vertical_format(horizontal_path, vertical_path)

print("Dataset conversion is done")
