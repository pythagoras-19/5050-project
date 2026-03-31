"""
Task 4.1: Certification Authority (CA) Key Generation

This program generates an RSA key pair for the Certification Authority.
The CA's private key will be used to sign server certificates.
The CA's public key will be embedded in clients for certificate verification.

Security Notes:
- RSA key size: 2048 bits (industry standard as of 2024)
- Public exponent: 65537 (standard)
- Private key is stored without password (this is for a lab environment)
  In production, private keys should be encrypted with a passphrase
"""

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

print("[CA Key Generation]")
print("Generating RSA-2048 key pair for Certification Authority...")

# Generate RSA key pair for CA
# - public_exponent=65537: Standard RSA public exponent (2^16 + 1)
# - key_size=2048: 2048-bit RSA, sufficient for security through 2030 (NIST recommendation)
ca_private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
ca_public_key = ca_private_key.public_key()

# Save CA private key to "secret_ca.key"
# Format: PEM (Human-readable, portable)
# PrivateFormat.PKCS8: Standard format, compatible with utilities like OpenSSL
# NoEncryption: Key stored in plaintext (only for lab use; use BestAvailableEncryption in production)
with open("secret_ca.key", "wb") as f:
    ca_private_pem = ca_private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    f.write(ca_private_pem)
    print(f"✅ CA Private key saved: secret_ca.key ({len(ca_private_pem)} bytes)")

# Save CA public key to "public_ca.key"
# Format: PEM, SubjectPublicKeyInfo (standard for public keys)
# Can be shared with all clients
with open("public_ca.key", "wb") as f:
    ca_public_pem = ca_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    f.write(ca_public_pem)
    print(f"✅ CA Public key saved: public_ca.key ({len(ca_public_pem)} bytes)")

print("\n[CA Key Generation Complete]")
print("Files created:")
print("  - secret_ca.key: CA private key (KEEP SECURE)")
print("  - public_ca.key: CA public key (distribute to clients)")
