"""
server_upd.py - TASK 2.8 & TASK 3 & TASK 4: Updated Server with Replay Protection

This server implements:
1. AES-128-GCM authenticated encryption (Task 2.8)
2. Sequence number-based replay attack prevention (Task 2.8)
3. RSA key exchange for session key (Task 3)
4. Digital certificate support (Task 4)

Security Features:
- Each response includes a sequence number (prevents replays)
- Ciphertext is authenticated with GCM (prevents tampering)
- Server public key and certificate sent to client (Task 4)
- Session key established via RSA encryption (Task 3)

Two modes of operation:
  MODE 1 (Task 2.8): Hardcoded symmetric key + sequence numbers
  MODE 2 (Task 3/4): Session key exchange + certificates
"""

from flask import Flask, jsonify, request
import base64
import os
import json

# Import crypto utilities
import sys
sys.path.insert(0, os.path.dirname(__file__))
from crypto_utils import (
    encrypt_data_gcm, 
    ReplayProtection,
    encrypt_key_with_public_key,
    decrypt_key_with_private_key,
    KEY
)
from cryptography.hazmat.primitives import serialization

app = Flask(__name__)

# Configuration
XY = 81  # Replace with actual student ID last two digits
PORT = int(f"50{XY:02d}")

# ===== TASK 2.8: Replay Protection with Sequence Numbers =====
replay_protection = ReplayProtection()


# ===== TASK 3 & 4: RSA Key Exchange Setup =====

def load_server_keys():
    """Load server's RSA key pair and certificate."""
    try:
        with open("secret.key", "rb") as f:
            server_private_pem = f.read()
        
        with open("public.key", "rb") as f:
            server_public_pem = f.read()
        
        # Try to load certificate (may not exist in Task 2.8)
        try:
            with open("pk.cert", "rb") as f:
                server_cert = f.read()
        except:
            server_cert = None
        
        return server_private_pem, server_public_pem, server_cert
    except FileNotFoundError as e:
        print(f"❌ ERROR: {e}")
        print("Please run keygen.py first to generate RSA keys.")
        return None, None, None


# Load keys at startup
server_private_pem, server_public_pem, server_cert = load_server_keys()

if server_private_pem is None:
    print("Keys not available. Exiting.")
    exit(1)


# ===== ROUTE 1: Send Public Key (Task 3 Step 2) =====

@app.route("/get_public_key", methods=["GET"])
def get_public_key():
    """
    Send server's public key to client.
    
    Response (Task 3):
        {
            "public_key": "base64(...PEM...)"
        }
    
    Response (Task 4):
        {
            "public_key": "base64(...PEM...)",
            "certificate": "base64(...signed cert...)"
        }
    
    Security: Public key is not secret, but certificate proves authenticity.
    """
    response = {
        "public_key": base64.b64encode(server_public_pem).decode()
    }
    
    # Include certificate if available (Task 4)
    if server_cert:
        response["certificate"] = base64.b64encode(server_cert).decode()
    
    print(f"[{request.method}] {request.path} -> Sending public key")
    return jsonify(response)


# ===== ROUTE 2: Receive Encrypted Session Key (Task 3 Step 2) =====

# Global variable to store negotiated session key per client
# In production, use proper session management
_session_key = None


@app.route("/exchange_key", methods=["POST"])
def exchange_key():
    """
    Receive encrypted session key from client.
    
    Request:
        {
            "encrypted_session_key": "base64(...RSA encrypted...)"
        }
    
    Response:
        {
            "status": "key_established"
        }
    
    Security:
        - Client encrypts session key with server's RSA public key
        - Server decrypts with RSA private key
        - Only server can decrypt (has private key)
        - Session key now shared between client and server
    """
    global _session_key
    
    try:
        data = request.get_json()
        encrypted_key_b64 = data["encrypted_session_key"]
        encrypted_key = base64.b64decode(encrypted_key_b64)
        
        # Decrypt session key using server's RSA private key
        _session_key = decrypt_key_with_private_key(encrypted_key, server_private_pem)
        
        print(f"[{request.method}] {request.path} -> Session key established")
        print(f"    Key: {_session_key.hex()[:32]}... ({len(_session_key)} bytes)")
        
        return jsonify({"status": "key_established"})
        
    except Exception as e:
        print(f"❌ Key exchange error: {e}")
        return jsonify({"error": str(e)}), 400


# ===== ROUTE 3: Send Encrypted Weather Data (Task 2.8 & Task 3) =====

@app.route("/weather", methods=["GET"])
def weather():
    """
    Send encrypted and authenticated weather data.
    
    Features:
        - Configured for Task 2.8 or Task 3 (depending on session key)
        - Uses sequence numbers for replay protection
        - Uses AES-GCM for authenticated encryption
        - Different nonce for each message (prevents replay if nonce verified)
    
    Response:
        {
            "nonce": "base64(12-byte nonce)",
            "ciphertext": "base64(encrypted weather data)",
            "tag": "base64(16-byte GCM auth tag)",
            "sequence": integer
        }
    
    Security Analysis:
        - GCM tag prevents tampering with ciphertext/nonce
        - Sequence number prevents replay attacks
        - New nonce each request ensures different ciphertext
    """
    try:
        # Prepare weather data
        weather_data = {
            "location": "Denton, TX",
            "temperature_c": 10,
            "temperature_f": 50,
            "condition": "Partly Cloudy",
            "humidity_percent": XY
        }
        
        # Choose session key: use exchanged key if available, else hardcoded key
        session_key = _session_key if _session_key else None
        
        # Encrypt and authenticate with GCM
        nonce, ciphertext, tag = encrypt_data_gcm(weather_data, session_key)
        
        # Get sequence number for replay protection
        sequence = replay_protection.get_next_seq()
        
        response = {
            "nonce": base64.b64encode(nonce).decode(),
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "tag": base64.b64encode(tag).decode(),
            "sequence": sequence
        }
        
        # Save response to file for potential replay attacks (demonstrates vulnerability)
        with open("response.bin", "wb") as f:
            f.write(json.dumps(response).encode())
        
        key_source = "exchanged session key" if _session_key else "hardcoded key"
        print(f"[{request.method}] {request.path}")
        print(f"    Sequence: {sequence}")
        print(f"    Key: {key_source}")
        print(f"    Nonce: {nonce.hex()}")
        print(f"    Ciphertext: {ciphertext.hex()[:32]}... ({len(ciphertext)} bytes)")
        print(f"    Tag: {tag.hex()}")
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ /weather error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print(f"[Server Starting]")
    print(f"Task: Task 2.8 (Replay Protection) + Task 3 (RSA Key Exchange) + Task 4 (Certificates)")
    print(f"Port: {PORT}")
    print(f"Routes:")
    print(f"  GET  /get_public_key -> Sends RSA public key + certificate")
    print(f"  POST /exchange_key   -> Receives encrypted session key")
    print(f"  GET  /weather        -> Sends encrypted + authenticated weather")
    print(f"")
    print(f"Endpoints:")
    print(f"  - Public key: http://127.0.0.1:{PORT}/get_public_key")
    print(f"  - Key exchange: http://127.0.0.1:{PORT}/exchange_key (POST)")
    print(f"  - Weather (encrypted): http://127.0.0.1:{PORT}/weather")
    print(f"")
    
    app.run(host="127.0.0.1", port=PORT, debug=False)
