cd dynaword-cellar-extract
git pull
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd src
export NUM_THREADS=60
export DOCLING_BATCH_SIZE=64
export DOCLING_QUEUE_SIZE=1000
export DOCLING_DEVICE="cuda"
export MARKER_WORKERS=60
export LANGCODE="SWE"
export EXTRACTION_LIBRARY="marker"
export NUM_SHARDS=500
export DS_NAME="swedish_metadata"
python -m extract