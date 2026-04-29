cd dynaword-cellar-extract
git pull
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd src
NUM_THREADS = 60 DOCLING_BATCH_SIZE = 64 DOCLING_QUEUE_SIZE = 1000 DOCLING_DEVICE = "cuda" MARKER_WORKERS = 60 LANGCODE = "SWE" EXTRACTION_LIBRARY = "marker" NUM_SHARDS = 500 DS_NAME = "swedish_metadata" CLEAR_DIRECTORY = "true" python -m extract