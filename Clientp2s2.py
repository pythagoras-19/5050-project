import requests
import base64
from crypto_utils import decrypt_data

XY = 81  # replace with your real XY

url = f"http://127.0.0.1:50{XY}/weather"

response = requests.get(url)
payload = response.json()

iv = base64.b64decode(payload["iv"])
ciphertext = base64.b64decode(payload["ciphertext"])

data = decrypt_data(iv, ciphertext)

print("Decrypted data:")
print(data)