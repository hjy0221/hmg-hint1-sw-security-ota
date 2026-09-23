import os
import urllib.request
from pathlib import Path


URL = "http://192.168.0.60:8000/123.txt"
ROOT_DIR = Path(__file__).resolve().parents[1]
DEST = ROOT_DIR / "work" / "device" / "153.txt"

blob = urllib.request.urlopen(URL).read()
os.makedirs(DEST.parent, exist_ok=True)
open(DEST, 'wb').write(blob)
print('download:', len(blob), 'bytes')
print('saved:', DEST)
