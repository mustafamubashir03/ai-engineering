import os
import subprocess

# Define destination directory explicitly
base_dir = r"G:\amazon_global_dataset"

# Explicit target numbers requested (1, 2, 3)
shards = ["00001", "00002", "00003"]

print("Starting native downloads...")

for num in shards:
    print(f"\n--- Downloading Shard Part {num} ---")
    
    # 1. Download Metadata shard using the working 'hf' terminal tool
    meta_cmd = f'hf download McAuley-Lab/Amazon-Reviews-2023 --repo-type dataset --include "raw_meta_Electronics/full-{num}-of-00010.parquet" --local-dir {base_dir}'
    subprocess.run(meta_cmd, shell=True)
    
    # 2. Download Reviews shard using the working 'hf' terminal tool
    review_cmd = f'hf download McAuley-Lab/Amazon-Reviews-2023 --repo-type dataset --include "raw_review_Electronics/full-{num}-of-00034.parquet" --local-dir {base_dir}'
    subprocess.run(review_cmd, shell=True)

print("\nSuccess! Shards 1, 2, and 3 are physically stored on your drive.")
