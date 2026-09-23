import os
import urllib.request


URL = "http://192.168.0.60:8000/123.txt"
DEST = "./work/device/153.txt"

blob = urllib.request.urlopen(URL).read()
os.makedirs('./work/device', exist_ok=True)
open(DEST, 'wb').write(blob)
print('download:', len(blob), 'bytes')
print('saved:', DEST)
