import requests

# CHANGE THIS to your last two digits (XY)
XY = 81  # <-- replace

def main():
    port = int(f"50{XY:02d}")
    url = f"http://127.0.0.1:{port}/weather"
    print("Requesting:", url)

    r = requests.get(url, timeout=5)
    print("Status:", r.status_code)
    print("Response JSON:")
    print(r.json())

if __name__ == "__main__":
    main()