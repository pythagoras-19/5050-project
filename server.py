from flask import Flask, jsonify

app = Flask(__name__)

# CHANGE THIS to your last two digits (XY)
XY = 81  # <-- replace

@app.get("/weather")
def weather():
    data = {
        "location": "Denton, TX",
        "temperature_c": 10,
        "temperature_f": 50,
        "condition": "Partly Cloudy",
        "humidity_percent": XY
    }
    return jsonify(data)

if __name__ == "__main__":
    port = int(f"50{XY:02d}")   # makes 5081 if XY=81, 5007 if XY=7, etc.
    app.run(host="127.0.0.1", port=port, debug=False)