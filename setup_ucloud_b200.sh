cd dynaword-cellar-extract
git pull
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd src
python -m extract