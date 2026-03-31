from flask import Flask, jsonify
import json
from crypto_utils import make_tag

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

    data_bytes = json.dumps(data, separators=(",", ":")).encode()
    tag = make_tag(data_bytes)

    with open("tag.txt", "w") as f:
        f.write(tag)

    return jsonify({
        "data": data,
        "tag": tag
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(f"50{XY}"), debug=False)