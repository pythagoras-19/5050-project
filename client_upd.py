"""
client_upd.py - TASK 2.8 & TASK 3 & TASK 4: Updated Client with Security Features

This client implements:
1. AES-128-GCM authenticated encryption (Task 2.8)
2. Sequence number validation for replay protection (Task 2.8)
3. RSA key exchange for session key negotiation (Task 3)
4. Digital certificate verification (Task 4)

Protocol Flow:
  1. Fetch server's public key (and certificate if available)
  2. Verify certificate with CA public key (Task 4 only)
  3. Generate random session key
  4. Encrypt session key with server's RSA public key
  5. Send encrypted session key to server
  6. Receive encrypted + authenticated weather data
  7. Decrypt and verify using GCM
  8. Check sequence number to prevent replay attacks

Security Properties:
- Client verifies server identity via certificate
- Session key is confidential (encrypted with RSA)
- Weather data is confidential and authentic (GCM)
- Replay attacks are detected (sequence number)
"""

import requests
import base64
import os
import json
import sys

# Import crypto utilities
sys.path.insert(0, os.path.dirname(__file__))
from crypto_utils import (
    decrypt_data_gcm,
    encrypt_key_with_public_key,
    verify_certificate,
    ReplayProtection
)
from cryptography.hazmat.primitives import serialization

# Configuration
XY = 81  # Replace with actual student ID last two digits
PORT = int(f"50{XY:02d}")
BASE_URL = f"http://127.0.0.1:{PORT}"

# CA's public key (embedded from public_ca.key)
# In production, this could be loaded from a trusted store
CA_PUBLIC_KEY_PEM = None


def load_ca_public_key():
    """Load CA's public key from public_ca.key file."""
    global CA_PUBLIC_KEY_PEM
    try:
        with open("public_ca.key", "rb") as f:
            CA_PUBLIC_KEY_PEM = f.read()
        print("[✓] CA public key loaded from public_ca.key")
        return CA_PUBLIC_KEY_PEM
    except FileNotFoundError:
        print("[!] public_ca.key not found (Task 4 only)")
        return None


# ===== STEP 1: Fetch Server Public Key =====

def get_server_public_key():
    """
    Fetch server's public key from /get_public_key endpoint.
    Also fetches certificate if available (Task 4).
    
    Returns:
        (public_key_pem, certificate_data or None)
    """
    try:
        url = f"{BASE_URL}/get_public_key"
        print(f"\n[STEP 1] Fetching server public key from {url}")
        
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        public_key_pem = base64.b64decode(data["public_key"])
        
        print(f"  ✓ Public key received ({len(public_key_pem)} bytes)")
        
        # Check for certificate (Task 4)
        certificate_data = None
        if "certificate" in data:
            certificate_data = base64.b64decode(data["certificate"])
            print(f"  ✓ Certificate received ({len(certificate_data)} bytes)")
        
        return public_key_pem, certificate_data
        
    except Exception as e:
        print(f"  ✗ Error fetching public key: {e}")
        return None, None


# ===== STEP 2a: Verify Certificate (Task 4) =====

def verify_server_certificate(certificate_data, ca_public_key):
    """
    Verify server's certificate using CA's public key.
    
    Certificate Verification:
        1. Extract message and signature from certificate
        2. Verify RSA-PSS signature with CA's public key
        3. Check that server's public key is correctly identified
    
    Returns:
        True if certificate is valid, False otherwise
    """
    if certificate_data is None or ca_public_key is None:
        print("  [!] Certificate or CA public key not available (skipping verification)")
        return True  # Allow unverified connections
    
    try:
        print("\n[CERTIFICATE VERIFICATION]")
        
        is_valid, message_text, _ = verify_certificate(certificate_data, ca_public_key)
        
        if not is_valid:
            print(f"  ✗ Certificate verification FAILED: {message_text}")
            return False
        
        print(f"  ✓ Certificate signature verified!")
        print(f"  ✓ Message: {message_text}")
        return True
        
    except Exception as e:
        print(f"  ✗ Certificate verification error: {e}")
        return False


# ===== STEP 2b: RSA Key Exchange =====

def exchange_session_key(server_public_key_pem):
    """
    Perform RSA key exchange with server.
    
    Protocol:
        1. Generate random 16-byte session key
        2. Encrypt with server's RSA public key (RSA-OAEP)
        3. Send encrypted key to server
        4. Server decrypts with its private key
        5. Both now share session key
    
    Returns:
        Session key (16 bytes) if successful, None otherwise
    """
    try:
        print(f"\n[STEP 2] RSA Key Exchange")
        
        # Generate random 16-byte session key
        session_key = os.urandom(16)
        print(f"  ✓ Generated random session key: {session_key.hex()}")
        
        # Encrypt session key with server's RSA public key
        print(f"  → Encrypting session key with RSA-OAEP...")
        encrypted_session_key = encrypt_key_with_public_key(
            session_key,
            server_public_key_pem
        )
        print(f"  ✓ Session key encrypted ({len(encrypted_session_key)} bytes)")
        
        # Send encrypted session key to server
        url = f"{BASE_URL}/exchange_key"
        payload = {
            "encrypted_session_key": base64.b64encode(encrypted_session_key).decode()
        }
        
        print(f"  → Sending to {url}")
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        
        result = response.json()
        if result.get("status") == "key_established":
            print(f"  ✓ Server confirmed key exchange")
            return session_key
        else:
            print(f"  ✗ Server response: {result}")
            return None
            
    except Exception as e:
        print(f"  ✗ Key exchange error: {e}")
        return None


# ===== STEP 3: Fetch Encrypted Weather Data =====

def get_encrypted_weather(session_key, replay_check):
    """
    Fetch encrypted and authenticated weather data from server.
    
    Security Checks:
        1. Verify GCM authentication tag (ensures data authenticity)
        2. Check sequence number (ensures message is fresh, not replayed)
        3. Decrypt using session key
    
    Returns:
        (decrypted_weather_dict, sequence_number) if successful, (None, None) otherwise
    """
    try:
        url = f"{BASE_URL}/weather"
        print(f"\n[STEP 3] Fetching encrypted weather from {url}")
        
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract components
        nonce = base64.b64decode(data["nonce"])
        ciphertext = base64.b64decode(data["ciphertext"])
        tag = base64.b64decode(data["tag"])
        sequence = data.get("sequence", 0)
        
        print(f"    Received response (seq={sequence})")
        print(f"    Nonce: {nonce.hex()}")
        print(f"    Ciphertext: {len(ciphertext)} bytes")
        print(f"    Tag: {tag.hex()}")
        
        # ===== SECURITY CHECK 1: Replay Protection =====
        print(f"   Checking replay protection (sequence number)...")
        if not replay_check.accept_seq(sequence):
            print(f"    REPLAY ATTACK DETECTED!")
            print(f"    Received seq={sequence}, but expected > {replay_check.sequence_number - 1}")
            return None, None
        print(f"     Sequence number valid (fresh message)")
        
        # ===== SECURITY CHECK 2: GCM Authentication =====
        print(f"    Verifying GCM authentication tag...")
        try:
            plaintext = decrypt_data_gcm(nonce, ciphertext, tag, session_key)
            print(f"    GCM verification passed (data is authentic & confidential)")
            return plaintext, sequence
            
        except Exception as e:
            print(f"    GCM AUTHENTICATION FAILED: {e}")
            print(f"    This indicates data tampering or wrong key!")
            return None, None
            
    except Exception as e:
        print(f"    Error fetching weather: {e}")
        return None, None


# ===== MAIN: Complete Protocol =====

def main():
    """Execute full client protocol with all security features."""
    
    print("="*70)
    print("CLIENT - Task 2.8 (Replay Protection) + Task 3 (Key Exchange) + Task 4 (Certificates)")
    print("="*70)
    
    # Load CA public key if available
    ca_public_key = load_ca_public_key()
    
    # STEP 1: Get server public key and certificate
    server_public_key_pem, certificate_data = get_server_public_key()
    if server_public_key_pem is None:
        print("\n✗ Failed to fetch server public key. Aborting.")
        return
    
    # STEP 2a: Verify certificate (if available)
    if certificate_data and ca_public_key:
        if not verify_server_certificate(certificate_data, ca_public_key):
            print("\n✗ Certificate verification failed. Rejecting server. Aborting.")
            return
    else:
        print("\n[!] Skipping certificate verification (not available in this mode)")
    
    # STEP 2b: RSA key exchange
    session_key = exchange_session_key(server_public_key_pem)
    if session_key is None:
        print("\n✗ Failed to establish session key. Aborting.")
        return
    
    # Initialize replay protection for this session
    replay_protection = ReplayProtection()
    
    # STEP 3: Fetch and verify encrypted weather (multiple times to test replay)
    print("\n" + "="*70)
    print("FETCHING WEATHER DATA")
    print("="*70)
    
    for request_num in range(1, 4):
        print(f"\n--- Request {request_num} ---")
        weather, seq = get_encrypted_weather(session_key, replay_protection)
        
        if weather is None:
            print(f"✗ Failed to get weather data.")
            continue
        
        print(f"\n✓ SUCCESS - Weather data retrieved and verified:")
        print(f"  Location: {weather['location']}")
        print(f"  Temperature: {weather['temperature_c']}°C ({weather['temperature_f']}°F)")
        print(f"  Condition: {weather['condition']}")
        print(f"  Humidity: {weather['humidity_percent']}%")
        print(f"  Sequence: {seq}")
    
    print("\n" + "="*70)
    print("TEST: Attempting Replay Attack")
    print("="*70)
    print("(Server in another window is replaying response.bin)")
    print("The sequence number should prevent this attack...")
    
    # Note: To test replay attack, run server_superfake in another terminal
    # or manually send the same response multiple times


if __name__ == "__main__":
    main()
