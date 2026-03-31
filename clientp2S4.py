import requests
import json
from crypto_utils import check_tag

XY = 81  # replace with your real XY

url = f"http://127.0.0.1:50{XY+1}/weather"

response = requests.get(url)
payload = response.json()

data = payload["data"]
tag = payload["tag"]

data_bytes = json.dumps(data, separators=(",", ":")).encode()

if check_tag(data_bytes, tag):
    print("Fake server response accepted.")
else:
    print("Fake server response rejected.")