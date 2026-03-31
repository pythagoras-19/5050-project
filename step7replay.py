from flask import Flask, Response

app = Flask(__name__)

XY = 81  # replace

@app.route("/weather", methods=["GET"])
def weather():
    with open("response.bin", "rb") as f:
        data = f.read()

    return Response(data, mimetype="application/json")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(f"50{XY}"), debug=False)