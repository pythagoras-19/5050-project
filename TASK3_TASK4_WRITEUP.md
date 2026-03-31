# Task 3 and Task 4 Write-Up

## Overview
This section explains what was implemented for Task 3 and Task 4, what outputs were observed during execution, and what was learned from each phase.

---

## Task 3: Upgrade with Public-Key Key Exchange

### What Task 3 Does
Task 3 replaces the hardcoded symmetric key approach with a dynamic session key exchange using RSA public-key encryption.

The goal is to establish a fresh symmetric session key per run, without sending that key in plaintext.

### What Was Implemented

#### 1. RSA Key Generation (Server Setup)
- File used: keygen.py
- Generated a 2048-bit RSA key pair.
- Stored files:
  - secret.key (server private key)
  - public.key (server public key)

This is the initial setup step. It is done once before running the secure protocol.

#### 2. Public Key Distribution
- Server endpoint: /get_public_key in server_upd.py
- Server sends its public key to the client (base64-encoded PEM).

#### 3. Session Key Creation and Exchange
- Client file: client_upd.py
- Client generates a random 16-byte session key.
- Client encrypts that session key using the server public key (RSA-OAEP).
- Client sends encrypted session key to server endpoint /exchange_key.
- Server decrypts with secret.key and stores session key for communication.

#### 4. Encrypted Weather Communication
- Server encrypts weather JSON using AES-GCM with the exchanged session key.
- Client decrypts and verifies integrity/authenticity via GCM tag.

No sensitive key material is transmitted in plaintext.

### Typical Output Observed

#### keygen.py output
- RSA key generation started.
- Private key saved to secret.key.
- Public key saved to public.key.
- Key size and exponent printed.

#### server_upd.py output
- Server start with route list.
- GET /get_public_key logged.
- POST /exchange_key logged as session key established.
- GET /weather logged with sequence, nonce, ciphertext length, and tag.

#### client_upd.py output
- Step 1: fetched server public key.
- Step 2: generated random session key and sent RSA-encrypted key.
- Step 3: received encrypted weather data.
- GCM verification passed.
- Decrypted weather fields printed.

### What We Learned from Task 3
- A hardcoded shared key is not ideal for real systems.
- Public-key cryptography solves secure key distribution.
- Hybrid encryption is practical and standard:
  - RSA for key exchange
  - AES-GCM for payload encryption/authentication
- Confidentiality of key exchange improves significantly because only the holder of the private key can decrypt the session key.

---

## Task 4: Upgrade with Public-Key Certificates

### What Task 4 Does
Task 4 solves the identity problem left in Task 3.

Even if the session key is encrypted with a public key, the client still needs assurance that the public key truly belongs to the legitimate server. Task 4 introduces CA-based certificate validation for that trust check.

### What Was Implemented

#### 1. Certification Authority Key Generation
- File used: keygen_ca.py
- Generated CA RSA key pair.
- Stored files:
  - secret_ca.key (CA private key)
  - public_ca.key (CA public key)

#### 2. Certificate Creation
- File used: cert_key.py
- Constructed certificate message binding server public key and student identity.
- Signed message with CA private key using RSA-PSS + SHA-256.
- Saved certificate to pk.cert.

#### 3. Server Sends Certificate with Public Key
- File used: server_upd.py
- /get_public_key returns:
  - server public key
  - certificate (pk.cert), when available

#### 4. Client Verifies Certificate Before Key Exchange
- File used: client_upd.py
- Client loads CA public key from public_ca.key.
- Client verifies certificate signature.
- Only if verification succeeds does it continue to RSA session key exchange and encrypted weather retrieval.

This ensures the client trusts the server key before using it.

### Typical Output Observed

#### keygen_ca.py output
- CA key generation started.
- secret_ca.key saved.
- public_ca.key saved.

#### cert_key.py output
- Loaded server public key.
- Loaded CA private key.
- Signed certificate message.
- Saved pk.cert.

#### client_upd.py output
- CA public key loaded.
- Certificate received.
- Certificate signature verified.
- Continued with key exchange and encrypted communication.

If certificate verification fails, client prints failure and aborts.

### What We Learned from Task 4
- Encryption alone is not enough; identity authentication is required.
- Certificates prevent public-key substitution (man-in-the-middle setup).
- CA signature verification creates a trust chain:
  - CA signs server identity binding.
  - Client verifies with CA public key.
  - Client can safely trust the server public key.
- Combining Task 3 + Task 4 gives both secure key exchange and authenticated server identity.

---

## Final Takeaway
Task 3 and Task 4 together implement a realistic secure communication model:
- Task 3 gives confidential session key establishment.
- Task 4 adds key authenticity and trust.

After both upgrades, the client-server design achieves:
- Confidentiality (AES-GCM encryption)
- Integrity (GCM authentication tag)
- Authenticity (certificate verification)
- Stronger resistance to interception and key substitution attacks
