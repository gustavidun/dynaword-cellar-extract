import subprocess
from config import RAW_OUT, EXTRACT_OUT, NUM_THREADS, MARKER_WORKERS

def marker_convert():
    subprocess.run(
        ["marker", RAW_OUT, "--output_dir", EXTRACT_OUT, "--output_format", "markdown", "--workers", str(MARKER_WORKERS)],
        check=True
    )