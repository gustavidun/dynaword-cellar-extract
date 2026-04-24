from pathlib import Path

from batch_convert import main
from datasets import load_dataset

from tenacity import retry, stop_after_attempt, wait_exponential
import requests

ds = load_dataset("gustavidun/cellar-metadata", split="train")
LANGCODE = "SWE"
SOURCE = "cellar"
OUT = Path(__file__).parent / "out"
OUT.mkdir(parents=True, exist_ok=True)

DS_PATH = Path(__file__).parent / "swedish_metadata"
DS_PATH.mkdir(parents=True, exist_ok=True)

NUM_SHARDS = 100

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1))
def fetch(url):
    return requests.get(url, timeout=30)

def fetch_and_save(example):
    type = example["type"]
    url = example["item"]
    idx = example["global_index"]

    try:
        resp = fetch(url)
    except Exception as e:
        print(f"Fetch exception, skipping... {e}")

    try:
        if type in ["pdf", "pdfa2a", "pdfa1a", "pdf1x", "pdfx4", "pdfx", "pdfa1b"]:
            with open(OUT / f"{idx}.pdf", "wb+") as f: 
                f.write(resp.content) 
        
        elif type in ["html", "xhtml", "xhtml5"]:
            with open(OUT / f"{idx}.html", "wb+") as f: 
                f.write(resp.content) 
        
        elif type in ["xml", "etsi_xml"]:
            with open(OUT / f"{idx}.xml", "wb+") as f: 
                f.write(resp.content) 
        
    except Exception as e:
        print(f"File error, skipping... {e}")
    
    return None

def clear_directory(dir_path: Path):
    """Deletes all files in the staging directory to free up space."""
    for item in dir_path.iterdir():
        if item.is_file():
            item.unlink()

if __name__ == "__main__":
    # 1. Filter the dataset first to get the exact target records
    filtered_ds = ds.filter(lambda x: x["langCode"] == LANGCODE)
    filtered_ds = filtered_ds.add_column("global_index", range(len(filtered_ds)))
    filtered_ds.save_to_disk(DS_PATH)

    # 2. Iterate over the dataset in shards
    for shard_idx in range(NUM_SHARDS):
        print(f"\n{'='*50}")
        print(f"Processing Shard {shard_idx + 1} of {NUM_SHARDS}")
        print(f"{'='*50}")
        
        # Slice the dataset into the current shard
        current_shard = filtered_ds.shard(num_shards=NUM_SHARDS, index=shard_idx)
        
        # Step A: Fetch and save the raw files for this shard into 'OUT'
        print("Downloading files...")
        current_shard.map(fetch_and_save)
        
        # Step B: Run the Docling conversion
        print("Running Docling conversion...")
        try:
            main()
        except Exception as e:
            print(f"Docling conversion failed on shard {shard_idx + 1}: {e}")
        
        # Step C: Clean up the raw download files to save disk space
        print("Cleaning up raw staging files...")
        clear_directory(OUT)

        print("\nAll shards processed successfully!")
