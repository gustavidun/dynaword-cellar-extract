from pathlib import Path
from time import sleep

from datasets import load_dataset
from tenacity import retry, stop_after_attempt, wait_exponential
import requests

from docling_convert import docling_convert
from marker_convert import marker_convert

from config import ROOT, RAW_OUT, EXTRACTION_LIBRARY

ds = load_dataset("gustavidun/cellar-metadata", split="train")
LANGCODE = "SWE"

DS_PATH = ROOT / "swedish_metadata"
DS_PATH.mkdir(parents=True, exist_ok=True)

NUM_SHARDS = 500

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
            with open(RAW_OUT / f"{idx}.pdf", "wb+") as f: 
                f.write(resp.content) 
        
        elif type in ["html", "xhtml", "xhtml5"]:
            with open(RAW_OUT / f"{idx}.html", "wb+") as f: 
                f.write(resp.content) 
        
        elif type in ["xml", "etsi_xml"]:
            with open(RAW_OUT / f"{idx}.xml", "wb+") as f: 
                f.write(resp.content) 
        
        else:
            print(f"Skipping non-compatible filetype {type}.")

    except Exception as e:
        print(f"File error, skipping... {e}")
    
    sleep(0.1)
    return None

def clear_directory(dir_path: Path):
    for item in dir_path.iterdir():
        if item.is_file():
            item.unlink()

if __name__ == "__main__":
    filtered_ds = ds.filter(lambda x: x["langCode"] == LANGCODE)
    filtered_ds = filtered_ds.add_column("global_index", range(len(filtered_ds)))
    filtered_ds.save_to_disk(DS_PATH)

    for shard_idx in range(NUM_SHARDS):
        print(f"\n{'='*50}")
        print(f"Processing Shard {shard_idx + 1} of {NUM_SHARDS}")
        print(f"{'='*50}")
        
        current_shard = filtered_ds.shard(num_shards=NUM_SHARDS, index=shard_idx)
        
        print("Downloading files...")
        current_shard.map(fetch_and_save)
        
        print("Running conversion...")
        try:
            if EXTRACTION_LIBRARY == "marker": marker_convert()
            if EXTRACTION_LIBRARY == "docling": docling_convert()
            
        except Exception as e:
            print(f"Conversion failed on shard {shard_idx + 1}: {e}")
        
        print("Cleaning up raw staging files...")
        clear_directory(RAW_OUT)

    print("\nAll shards processed successfully!")
