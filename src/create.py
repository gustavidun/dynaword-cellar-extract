from datetime import date
from pathlib import Path
import tempfile
import uuid

import requests
from datasets import load_dataset
from lxml import html, etree
from tenacity import retry, stop_after_attempt, wait_exponential

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

ds = load_dataset("gustavidun/cellar-metadata", split="train")
LANGCODE = "NOR"
SOURCE = "cellar"
OUT = Path(__file__).parent / "out"

column_order = [
    "id",
    "text",
    "source",
    "created",
    "added",
]

converter = PdfConverter(
    artifact_dict=create_model_dict(),
)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1))
def fetch(url):
    return requests.get(url, timeout=30)

def fetch_and_save(example):
    type = example["type"]
    url = example["item"]

    try:
        resp = fetch(url)
    except Exception as e:
        print(f"Fetch exception, skipping... {e}")

    try:
        if type in ["pdf", "pdfa2a", "pdfa1a", "pdf1x", "pdfx4", "pdfx", "pdfa1b"]:
            with open(OUT / f"{uuid.uuid1()}.pdf", "wb+") as f: 
                f.write(resp.content) 
        
        if type in ["html", "xhtml", "xhtml5"]:
            with open(OUT / f"{uuid.uuid1()}.html", "wb+") as f: 
                f.write(resp.content) 
        
        if type in ["xml", "etsi_xml"]:
            with open(OUT / f"{uuid.uuid1()}.xml", "wb+") as f: 
                f.write(resp.content) 
        
    except Exception as e:
        print(f"File error, skipping... {e}")
    
    return None

def create_samples():
    rows = []
    for file in OUT.glob("*.pdf"):
        rows.append({
            "text": extract_text_from_item(example["item"], example["type"]),
            "source": SOURCE,
            "added": date.today().strftime("%Y-%m-%d"),
            "created": example["date"],
        })


def extract_text_from_item(url, type):
    try:
        resp = fetch(url)
    except Exception as e:
        print(f"Fetch exception, skipping... {e}")
        return ""
    
    try:
        if type in ["pdf", "pdfa2a", "pdfa1a", "pdf1x", "pdfx4", "pdfx", "pdfa1b"]:
            with tempfile.NamedTemporaryFile() as temp:
                temp.write(resp.content) 
                rendered = converter(temp.name)
                text, _, images = text_from_rendered(rendered)
                return text
        
        if type in ["html", "xhtml", "xhtml5"]:
            return html.fromstring(resp.content).text_content()
        
        if type in ["xml", "etsi_xml"]:
            root = etree.fromstring(resp.content)
            return "".join(root.itertext())
        
        return ""
    
    except Exception as e:
        print(f"Extraction exception, skipping... {e}")
        return ""

def reformat_samples(example):
    return {
        "text": extract_text_from_item(example["item"], example["type"]),
        "source": SOURCE,
        "added": date.today().strftime("%Y-%m-%d"),
        "created": example["date"],
    }

if __name__ == "__main__":
    ds = ds.filter(lambda x: x["langCode"] == LANGCODE)
    ds.map(fetch_and_save)

    

    ds = ds.map(reformat_samples)
    ds = ds.filter(lambda x: x["text"] != "") # drop na (type not extractable or fetch error)

    ds = ds.add_column("id", [f"{SOURCE}_{i}" for i in range(len(ds))])
    ds = ds.select_columns(column_order) #order 

    save_path = Path(__file__).parent / f"{SOURCE}.parquet"
    ds.to_parquet(save_path)