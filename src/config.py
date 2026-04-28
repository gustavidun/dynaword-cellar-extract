from docling.datamodel.accelerator_options import AcceleratorDevice
from pathlib import Path
from dotenv import load_dotenv

from typing import Literal
import os

ROOT = Path(__file__).parents[1]

load_dotenv(ROOT / ".env")

OUT = ROOT / "out"

RAW_OUT = OUT / "raw"
RAW_OUT.mkdir(parents=True, exist_ok=True) 

EXTRACT_OUT = OUT / "extracted"
EXTRACT_OUT.mkdir(parents=True, exist_ok=True) 

DS_NAME = os.getenv("DS_NAME")

LANGCODE = os.getenv("LANGCODE")
NUM_SHARDS = int(os.getenv("NUM_SHARDS"))
CLEAR_DIRECTORY = os.getenv("CLEAR_DIRECTORY", "false") == "true"

EXTRACTION_LIBRARY : Literal["marker", "docling"] = os.getenv("EXTRACTION_LIBRARY")

NUM_THREADS = int(os.getenv("NUM_THREADS"))
DOCLING_BATCH_SIZE = int(os.getenv("DOCLING_BATCH_SIZE"))
DOCLING_QUEUE_SIZE = int(os.getenv("DOCLING_QUEUE_SIZE"))
MARKER_WORKERS = int(os.getenv("MARKER_WORKERS"))

DOCLING_DEVICE : Literal["cuda", "auto"] = os.getenv("DOCLING_DEVICE")
docling_device = AcceleratorDevice.CUDA if DOCLING_DEVICE == "cuda" else AcceleratorDevice.AUTO


