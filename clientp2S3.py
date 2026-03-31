import requests
import json
from crypto_utils import check_tag

XY = 81  # replace with your real XY

url = f"http://127.0.0.1:50{XY}/weather"

response = requests.get(url)
payload = response.json()

data = payload["data"]
tag = payload["tag"]

data_bytes = json.dumps(data, separators=(",", ":")).encode()

if check_tag(data_bytes, tag):
    print("MAC is valid.")
    print(data)
else:
    print("MAC is invalid.")