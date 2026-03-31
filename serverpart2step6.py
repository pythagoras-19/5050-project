from flask import Flask, jsonify
import json
import os
import base64
from Crypto.Cipher import AES

app = Flask(__name__)

KEY = b"mohammed_5050key"
XY = 81  # replace

@app.route("/weather", methods=["GET"])
def weather():
    data = {
        "location": "Denton, TX",
        "temperature_c": 10,
        "temperature_f": 50,
        "condition": "Partly Cloudy",
        "humidity_percent": XY
    }

    plaintext = json.dumps(data).encode()

    cipher = AES.new(KEY, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)

    response = {
        "nonce": base64.b64encode(cipher.nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "tag": base64.b64encode(tag).decode()
    }

    # Save raw response for replay attack
    with open("response.bin", "wb") as f:
        f.write(json.dumps(response).encode())

    return jsonify(response)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(f"50{XY}"), debug=False)