import requests
import json
import base64
from Crypto.Cipher import AES

KEY = b"mohammed_5050key"
XY = 81  # replace

url = f"http://127.0.0.1:50{XY}/weather"

response = requests.get(url)
data = response.json()

nonce = base64.b64decode(data["nonce"])
ciphertext = base64.b64decode(data["ciphertext"])
tag = base64.b64decode(data["tag"])

cipher = AES.new(KEY, AES.MODE_GCM, nonce=nonce)

try:
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    print("✅ Decrypted & authenticated:")
    print(json.loads(plaintext))
except:
    print("❌ Authentication failed")