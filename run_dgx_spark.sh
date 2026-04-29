git pull
cd src
export HF_HOME="/home/chc_apps/huggingface"
export NUM_THREADS=60
export DOCLING_BATCH_SIZE=64
export DOCLING_QUEUE_SIZE=100
export DOCLING_DEVICE="cuda"
export MARKER_WORKERS=16
export LANGCODE="NOR"
export EXTRACTION_LIBRARY="marker"
export NUM_SHARDS=1
export DS_NAME="norwegian_metadata"
python -m extract