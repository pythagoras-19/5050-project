"""
Task 3.1: Server RSA Key Generation

This program generates an RSA key pair for the server.
The public key will be sent to clients for key exchange (Task 3).
The private key will be kept secret by the server for decryption.

Key Details:
  - Algorithm: RSA (Rivest-Shamir-Adleman)
  - Key size: 2048 bits (NIST recommended for security through 2030)
  - Public exponent: 65537 (standard, balances security and performance)
  - Private key storage: PEM format, PKCS8, unencrypted (lab environment)

Security Notes:
  - 2048-bit RSA provides ~112 bits of symmetric-equivalent security
  - This is sufficient for session key exchange with AES-128 or AES-256
  - In production: encrypt private key with passphrase using BestAvailableEncryption
  - In production: use HSM (Hardware Security Module) for private key storage

Files Generated:
  - secret.key: RSA private key (KEEP SECURE - do not share!!)
  - public.key: RSA public key (send to clients)
"""

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

print("[RSA Key Generation]")
print("Generating RSA-2048 key pair for server...")

# Generate RSA key pair
#public_exponent=65537: RSA public exponent (2^16 + 1)
#This is the standard choice: balance between security and speed from my understanding
#prevents timing attacks compared to other exponents
#key_size=2048: 2048-bit RSA key
#NIST recommends 2048-bit minimum for security through 2030 from my research
#256-bit AES + 2048-bit RSA is well-matched
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
public_key = private_key.public_key()

# Lets save private key to "secret.key"
# in the format: PEM (Privacy Enhanced Mail - human readable, ASCII-based)
# PrivateFormat.PKCS8: Public Key Cryptography Standards #8
#   - Standard format, compatible with OpenSSL, Java, etc.
#   - Stores algorithm identifier + key material
# NoEncryption: Private key NOT encrypted (only for lab/demo)
#   - In production: Use BestAvailableEncryption() with passphrase
with open("secret.key", "wb") as f:
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    f.write(private_pem)
    print(f"✅ Server private key saved: secret.key ({len(private_pem)} bytes)")
    print(f"   Keep this file SECURE - anyone with it can impersonate the server")

# Save public key to "public.key"
# Format: PEM
# PublicFormat.SubjectPublicKeyInfo: Standard format for public keys
#   - Can be freely distributed
#   - clients will use this for RSA encryption
with open("public.key", "wb") as f:
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    f.write(public_pem)
    print(f"✅ Server public key saved: public.key ({len(public_pem)} bytes)")
    print(f"   Share this with clients for key exchange and signature verification")

print("\n[RSA Key Generation Complete]")
print(f"Key Size: {private_key.key_size} bits")
print(f"Public Exponent: 65537")
print(f"Files created!!:")
print(f"  - secret.key: Server private key (private/secure)")
print(f"  - public.key: Server public key (public distribution)")
print(f"\nthe next steps:")
print(f"  1. Run keygen_ca.py to generate CA keys (Task 4)")
print(f"  2. Run cert_key.py to create certificate (Task 4)")
print(f"  3. Run server_upd.py to start secure server (Task 3+)")

