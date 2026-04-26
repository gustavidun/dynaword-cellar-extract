import subprocess
from config import RAW_OUT, EXTRACT_OUT

def convert():
    subprocess.run(
        ["marker", RAW_OUT, "--output_dir", EXTRACT_OUT, "--output_format", "markdown"],
        check=True
    )