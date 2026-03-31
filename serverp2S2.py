from flask import Flask, jsonify
import base64
from crypto_utils import encrypt_data

app = Flask(__name__)

XY = 81  # replace with your real XY

@app.route("/weather", methods=["GET"])
def weather():
    data = {
        "location": "Denton, TX",
        "temperature_c": 10,
        "temperature_f": 50,
        "condition": "Partly Cloudy",
        "humidity_percent": XY
    }

    iv, ciphertext = encrypt_data(data)

    return jsonify({
        "iv": base64.b64encode(iv).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode()
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(f"50{XY}"), debug=False)