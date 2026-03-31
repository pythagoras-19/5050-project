"""
Task 4.2: Public Key Certificate Generation

This program creates a certificate signing the server's public key with the CA's private key.

Certificate Structure:
  Message: "This public key: [hex of public key] belongs to [Student ID]."
  Signature: RSA signature of the message with CA's private key

The certificate proves:
  1. The public key belongs to the claimed server
  2. The CA vouches for this (signature verification with CA public key)
  3. No tampering: signature must verify with CA's public key

Security Properties:
  - Only CA can create valid signatures (has secret_ca.key)
  - Anyone with public_ca.key can verify the certificate
  - Non-repudiation: CA cannot deny signing (assuming private key safety)
"""

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import os

# Student ID (replace with actual student ID)
STUDENT_ID = "81"

print("[Certificate Generation]")

# Step 1: Load server's public key from public.key
print("Loading server public key from public.key...")
if not os.path.exists("public.key"):
    print("❌ ERROR: public.key not found. Run keygen.py first.")
    exit(1)

with open("public.key", "rb") as f:
    server_public_pem = f.read()
    server_public_key = serialization.load_pem_public_key(server_public_pem)

# Convert public key to hex bytes for certificate message
# PublicNumbers() extracts the key's mathematical components
public_numbers = server_public_key.public_numbers()
n_hex = hex(public_numbers.n)[2:]  # Remove "0x" prefix
e_hex = hex(public_numbers.e)[2:]

print(f"✅ Server public key loaded")
print(f"   Key size: {server_public_key.key_size} bits")
print(f"   N (first 32 chars): {n_hex[:32]}...")
print(f"   E: {e_hex}")

# Step 2: Load CA private key from secret_ca.key
print("\nLoading CA private key from secret_ca.key...")
if not os.path.exists("secret_ca.key"):
    print("❌ ERROR: secret_ca.key not found. Run keygen_ca.py first.")
    exit(1)

with open("secret_ca.key", "rb") as f:
    ca_private_pem = f.read()
    ca_private_key = serialization.load_pem_private_key(ca_private_pem, password=None)

print(f"✅ CA private key loaded ({ca_private_key.key_size} bits)")

# Step 3: Create the certificate message
# Format: "This public key: [N[...]]:[E[...]] belongs to [STUDENT_ID]."
message = f"This public key: {n_hex[:64]}:{e_hex} belongs to {STUDENT_ID}."
message_bytes = message.encode()

print(f"\nCertificate message ({len(message_bytes)} bytes):")
print(f"  {message}")

# Step 4: Sign the message with CA's private key using RSA-PSS
# RSA-PSS: Probabilistic Signature Scheme (more secure than PKCS1v15)
# - Uses random padding (different signature each time for same message)
# - Prevents signature forgery attacks
# - Standard in modern cryptography (RFC 8017)
signature = ca_private_key.sign(
    message_bytes,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

print(f"✅ Message signed with CA private key (PSS)")
print(f"   Signature size: {len(signature)} bytes")
print(f"   Signature (first 32 bytes hex): {signature[:32].hex()}")

# Step 5: Save certificate to pk.cert
# Certificate file contains: [message_bytes] || [signature_bytes]
# Delimiter: newline between message and signature
certificate_data = message_bytes + b"\n" + signature

with open("pk.cert", "wb") as f:
    f.write(certificate_data)

print(f"\n✅ Certificate saved: pk.cert ({len(certificate_data)} bytes)")
print(f"   Message portion: {len(message_bytes)} bytes")
print(f"   Signature portion: {len(signature)} bytes")

print("\n[Certificate Generation Complete]")
print("Certificate can now be sent to clients along with the server's public key.")
print("Clients will verify the certificate using CA's public key (public_ca.key).")
