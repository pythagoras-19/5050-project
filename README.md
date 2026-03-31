# Cryptographic System: Complete Implementation

**Project**: Secure REST Client-Server Communication with Symmetric and Asymmetric Cryptography

**Overview**: This project demonstrates the evolution of a client-server weather service from plain communication through various security layers: encryption, authentication, key exchange, and certificate-based authentication.

---

## Table of Contents
1. [Environment Setup](#environment-setup)
2. [Task Breakdown](#task-breakdown)
3. [Step-by-Step Execution](#step-by-step-execution)
4. [Files Reference](#files-reference)
5. [Security Analysis](#security-analysis)

---

## Environment Setup

### Prerequisites
```bash
# Python 3.8+
python3 --version

# Install dependencies
pip install Flask requests cryptography
```

### Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install Flask requests cryptography
```

### Verify Installation
```bash
python3 -c "from cryptography.hazmat.primitives.asymmetric import rsa; print('✓ cryptography library OK')"
```

---

## Task Breakdown

### Task 1: Basic REST Server/Client
**Goal**: Plain communication without security
**Files**: `server.py`, `client.py`
**Key Points**:
- HTTP GET request to `/weather` endpoint
- JSON response with hardcoded weather data
- Port: `5081` (for XY=81)
- No encryption or authentication

### Task 2: Symmetric Encryption & Integrity
**Parts**:
1. **2.1-2.2**: AES-CBC Encryption (`serverp2S2.py`, `Clientp2s2.py`)
   - Confidentiality only (no authentication)
   
2. **2.3**: HMAC Authentication (`serverp2S3.py`, `clientp2S3.py`)
   - Integrity only (no confidentiality)
   
3. **2.5-2.6**: AES-GCM (Authenticated Encryption) (`serverpart2step6.py`, `clienpart2step6.py`)
   - Both confidentiality and authenticity
   
4. **2.7**: Replay Attack Vulnerability (`step7replay.py`)
   - Same GCM message replayed multiple times
   
5. **2.8**: Replay Attack Countermeasure (`server_upd.py`, `client_upd.py`)
   - Sequence numbers prevent replays

### Task 3: RSA Key Exchange
**Goal**: Establish session key without pre-shared secrets
**Files**: `keygen.py`, `server_upd.py`, `client_upd.py`
**Key Points**:
1. Server generates RSA-2048 key pair
2. Client fetches server's public key
3. Client encrypts random session key with RSA
4. Server decrypts to recover session key
5. Use session key for AES-GCM encryption

### Task 4: Public Key Certificates
**Goal**: Verify server identity via trusted CA
**Files**: `keygen_ca.py`, `cert_key.py`, `server_upd.py`, `client_upd.py`
**Key Points**:
1. CA generates its own RSA key pair
2. CA signs server's public key with certificate
3. Server sends certificate with public key
4. Client verifies certificate using CA's public key
5. Prevents man-in-the-middle attacks

---

## Step-by-Step Execution

### Part 1: Task 1 - Basic Communication
```bash
# Terminal 1: Start basic server
python3 server.py

# Terminal 2: Run basic client
python3 client.py

# Expected Output:
# Status: 200
# Response JSON:
# {'location': 'Denton, TX', 'temperature_c': 10, ...}
```

### Part 2: Task 2 - Symmetric Encryption

#### Step 2.2: Encryption with Confidentiality
```bash
# Terminal 1: Start encrypted server
python3 serverp2S2.py

# Terminal 2: Run client (decrypts response)
python3 Clientp2s2.py

# Expected Output:
# Decrypted data:
# {'location': 'Denton, TX', 'temperature_c': 10, ...}
```

#### Step 2.3: Integrity with HMAC
```bash
# Terminal 1: Start HMAC server
python3 serverp2S3.py

# Terminal 2: Run client (verifies MAC)
python3 clientp2S3.py

# Expected Output:
# MAC is valid.
# {'location': 'Denton, TX', 'temperature_c': 10, ...}
```

#### Step 2.5-2.6: Authenticated Encryption (AES-GCM)
```bash
# Terminal 1: Start GCM server
python3 serverpart2step6.py

# Terminal 2: Run client (decrypt + verify)
python3 clienpart2step6.py

# Expected Output:
# ✅ Decrypted & authenticated:
# {'location': 'Denton, TX', 'temperature_c': 10, ...}
```

#### Step 2.7: Replay Attack Demonstration
```bash
# Terminal 1: Start server_superfake (replays response.bin)
python3 step7replay.py

# Terminal 2: Run client from step 2.6 against fake server
# Would accept replay (vulnerability)
```

### Part 3: Task 2.8 - Replay Protection

```bash
# Terminal 1: Start updated server with sequence numbers
python3 server_upd.py

# Terminal 2: Run updated client
python3 client_upd.py

# Expected Output:
# [STEP 1] Fetching server public key
# [STEP 2] RSA Key Exchange
#   ✓ Generated random session key
#   ✓ Session key encrypted
# [STEP 3] Fetching encrypted weather
#   ✓ Sequence number valid
#   ✓ GCM verification passed

# Try replay attack - should be REJECTED:
# ✗ REPLAY ATTACK DETECTED!
```

### Part 4: Task 3 - RSA Key Exchange

#### Step 3.1: Generate RSA Keys
```bash
python3 keygen.py

# Expected Output:
# ✅ Server private key saved: secret.key (1704 bytes)
# ✅ Server public key saved: public.key (294 bytes)

# Files created:
#   - secret.key
#   - public.key
```

#### Step 3.2 & 3.3: Key Exchange + Encrypted Communication
```bash
# Terminal 1: Start server (with key exchange support)
python3 server_upd.py

# Terminal 2: Run client (performs key exchange)
python3 client_upd.py

# Expected Output:
# [STEP 1] Fetching server public key
# [STEP 2] RSA Key Exchange
#   ✓ Generated random session key: ab12cd34...
#   → Encrypting session key with RSA-OAEP
#   ✓ Session key encrypted (256 bytes)
# [STEP 3] Fetching encrypted weather
#   ✓ Received response (seq=1)
#   ✓ Sequence number valid
#   ✓ GCM verification passed
# ✓ SUCCESS - Weather data retrieved and verified
```

### Part 5: Task 4 - Certificates

#### Step 4.1: Generate CA Keys
```bash
python3 keygen_ca.py

# Expected Output:
# ✅ CA Private key saved: secret_ca.key (1704 bytes)
# ✅ CA Public key saved: public_ca.key (294 bytes)

# Files created:
#   - secret_ca.key (CA's private key)
#   - public_ca.key (CA's public key - embed in clients)
```

#### Step 4.2: Create Certificate
```bash
python3 cert_key.py

# Expected Output:
# ✅ Server public key loaded
# ✅ CA private key loaded
# ✅ Message signed with CA (PSS)
# ✅ Certificate saved: pk.cert (1968 bytes)

# Files created:
#   - pk.cert (signed certificate)
```

#### Step 4.3: Client Verifies Certificate
```bash
# Terminal 1: Start server (sends certificate)
python3 server_upd.py

# Terminal 2: Run client (verifies certificate)
python3 client_upd.py

# Expected Output:
# [CA Key Loading]
# ✓ CA public key loaded from public_ca.key
# [STEP 1] Fetching server public key
#   ✓ Certificate received (1968 bytes)
# [CERTIFICATE VERIFICATION]
#   ✓ Certificate signature verified!
#   ✓ Message: This public key: abc123def... belongs to 81.
```

---

## Files Reference

### Core Files

| File | Purpose | Task |
|------|---------|------|
| `server.py` | Basic HTTP weather server | 1 |
| `client.py` | Basic HTTP client | 1 |
| `crypto_utils.py` | Cryptographic functions (AES, RSA, HMAC, etc.) | 2-4 |

### Task 2: Encryption & Authentication

| File | Purpose | Type |
|------|---------|------|
| `serverp2S2.py` | AES-CBC encrypted server | Variant |
| `Clientp2s2.py` | AES-CBC client | Variant |
| `serverp2S3.py` | HMAC-SHA256 MAC server | Variant |
| `clientp2S3.py` | HMAC client | Variant |
| `server_fake.py` | Fake server for attack demo | Variant |
| `clientp2S4.py` | Client testing fake server | Variant |
| `serverpart2step6.py` | AES-GCM authenticated encryption | Variant |
| `clienpart2step6.py` | GCM client | Variant |
| `step7replay.py` | Replay attack server | Variant |

### Task 2.8, 3, 4: Advanced Security

| File | Purpose | Task |
|------|---------|------|
| `keygen.py` | RSA key pair generation (server) | 3 |
| `keygen_ca.py` | RSA key pair generation (CA) | 4 |
| `cert_key.py` | Certificate generation | 4 |
| `server_upd.py` | Server with all features (Tasks 2.8, 3, 4) | 2.8-4 |
| `client_upd.py` | Client with all features (Tasks 2.8, 3, 4) | 2.8-4 |

### Generated Files

| File | Purpose | Security |
|------|---------|----------|
| `secret.key` | Server RSA private key | Keep secure! |
| `public.key` | Server RSA public key | Public distribution |
| `secret_ca.key` | CA RSA private key | Keep secure! |
| `public_ca.key` | CA RSA public key | Embed in clients |
| `pk.cert` | Certificate (signed) | Public/authenticated |
| `response.bin` | Encrypted weather response | Demo/testing |
| `tag.txt` | HMAC authentication tag | Demo/testing |

---

## Security Analysis

### Evolution of Security Properties

```
┌─────────────────┬───────────────┬──────────────┬───────────────┬──────────┐
│ Task            │ Confidentiality│ Integrity   │ Authenticity  │ Freshness│
├─────────────────┼───────────────┼──────────────┼───────────────┼──────────┤
│ Task 1 (Plain)  │      ❌       │      ❌     │      ❌       │    ❌    │
│ Task 2.2 (AES)  │      ✅       │      ❌     │      ❌       │    ❌    │
│ Task 2.3 (MAC)  │      ❌       │      ✅     │      ✅       │    ❌    │
│ Task 2.6 (GCM)  │      ✅       │      ✅     │      ✅       │    ❌    │
│ Task 2.8 (Seq)  │      ✅       │      ✅     │      ✅       │    ✅    │
│ Task 3 (KeyEx)  │      ✅       │      ✅     │      ✅ *     │    ✅    │
│ Task 4 (Certs)  │      ✅       │      ✅     │      ✅       │    ✅    │
└─────────────────┴───────────────┴──────────────┴───────────────┴──────────┘
* Task 3: Authenticity implied by key exchange, explicit in Task 4
```

### Cryptographic Algorithms Used

| Purpose | Algorithm | Parameters | Justification |
|---------|-----------|-----------|---|
| Encryption | AES | 128-bit key, GCM mode, 12-bit nonce | NIST standard, proven secure |
| Authentication | HMAC-SHA256 | 128-bit key, SHA256 hash | Standard, constant-time |
| Key Exchange | RSA-OAEP | 2048-bit modulus, SHA256, MGF1 | Prevents CCA attacks |
| Signatures | RSA-PSS | 2048-bit, SHA256, PSS padding | Probabilistic, stronger than PKCS1v15 |
| Randomness | os.urandom() | OS /dev/urandom (Linux/macOS) | Cryptographically secure |

### Attack Prevention

| Attack | Vulnerability | Defense | Task |
|--------|---|---|---|
| Eavesdropping | Plaintext transmission | AES-GCM encryption | 2.2+ |
| Tampering | No integrity protection | HMAC / GCM tag | 2.3, 2.6+ |
| Man-in-the-Middle | No authentication | Certificates + RSA signatures | 4 |
| Replay | Same message reused | Sequence numbers / nonces | 2.8+ |
| Keylogging | Hardcoded keys | RSA key exchange | 3+ |

---

## Testing Scenarios

### Scenario 1: Normal Operation
```bash
# Both client and server running correctly
Expected: ✓ All security checks pass
```

### Scenario 2: Tampering (GCM)
```bash
# Modify ciphertext after interception (Wireshark)
Expected: ✗ GCM tag verification fails (data rejected)
```

### Scenario 3: Replay Attack
```bash
# Replay same response multiple times
Expected (Task 2.6): ✓ Accepted (vulnerability)
Expected (Task 2.8+): ✗ Rejected (sequence number < current)
```

### Scenario 4: Man-in-the-Middle
```bash
# Attacker intercepts and modifies public key
Expected (Task 3): ✓ Vulnerable (ciphertext accepted)
Expected (Task 4): ✗ Certificate verification fails
```

### Scenario 5: Fake Server
```bash
# Attacker runs fake_server.py with modified data
Expected (Task 2.3): ✗ MAC doesn't match
Expected (Task 2.6): ✗ GCM tag doesn't match
```

---

## Wireshark Analysis

### What to Look For

1. **Task 1 (Plain)**: 
   - JSON visible in plaintext
   - Port 5081 shows readable weather data

2. **Task 2.2 (AES-CBC)**:
   - Binary ciphertext visible
   - IV sent with each response
   - No plaintext recovery

3. **Task 2.3 (HMAC)**:
   - Data in plaintext (by design)
   - 64-character hex MAC tag visible
   - Cannot compute valid tag without key

4. **Task 2.6 (AES-GCM)**:
   - 12-byte nonce
   - Ciphertext (encrypted binary)
   - 16-byte authentication tag
   - Nonce different for each response

5. **Task 3 (RSA Key Exchange)**:
   - /get_public_key returns base64-encoded PEM
   - /exchange_key POST with 256-byte encrypted key
   - No plaintext keys visible

6. **Task 4 (Certificates)**:
   - /get_public_key also returns base64-encoded certificate
   - Certificate structure: message + signature
   - Only CA can verify signature

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'cryptography'"
```bash
pip install cryptography flask requests
```

### "Address already in use" (port 5081)
```bash
# Find process using port
lsof -i :5081  # macOS/Linux
netstat -ano | findstr :5081  # Windows

# Kill process or use different XY value
```

### "Connection refused" (client can't reach server)
- Ensure server is running in another terminal
- Check port matches (5081 for XY=81)
- Verify localhost IP is 127.0.0.1

### "Certificate verification failed"
- Ensure keygen_ca.py, cert_key.py, keygen.py ran in order
- Check public_ca.key exists and is readable
- Verify certificates haven't expired (no expiry in this demo)

---

## References

### Cryptographic Standards
- NIST SP 800-38D: GCM mode
- NIST SP 800-38A: CBC mode  
- RFC 8017: PKCS #1 RSA Cryptography Specifications
- RFC 2104: HMAC

### Python Cryptography
- cryptography.io documentation
- https://docs.python-requests.org/

### Security References
- OWASP Top 10
- CWE: Common Weakness Enumeration (tampering, replay, MITM)

---

## Notes

- **Student ID**: XY = 81 (replace with actual last two digits)
- **Lab Environment**: Private keys stored unencrypted (change in production)
- **Clock**: No time-based freshness (only sequence numbers)
- **Session Management**: Simple global variable (use database in production)

---

**Last Updated**: 2024
**Status**: Complete implementation with comprehensive documentation
