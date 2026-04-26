from docling.datamodel.accelerator_options import AcceleratorDevice
from pathlib import Path

ROOT = Path(__file__).parents[1]

RAW_OUT = ROOT / "out"
RAW_OUT.mkdir(parents=True, exist_ok=True) 

EXTRACT_OUT = ROOT / "out_extracted"
EXTRACT_OUT.mkdir(parents=True, exist_ok=True) 

NUM_THREADS = 60
DOCLING_BATCH_SIZE = 64
DOCLING_QUEUE_SIZE = 1000
DOCLING_DEVICE = AcceleratorDevice.CUDA

