from flask import Flask, jsonify

app = Flask(__name__)

XY = 81  # replace with your real XY

@app.route("/weather", methods=["GET"])
def weather():
    fake_data = {
        "location": "Denton, TX",
        "temperature_c": 10,
        "temperature_f": 50,
        "condition": "Partly Cloudy",
        "humidity_percent": XY + 1
    }

    with open("tag.txt", "r") as f:
        old_tag = f.read().strip()

    return jsonify({
        "data": fake_data,
        "tag": old_tag
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(f"50{XY+1}"), debug=False)