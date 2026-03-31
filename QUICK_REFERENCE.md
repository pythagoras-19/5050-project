# Quick Reference Guide

## 🎯 What This Project Demonstrates

A complete progression from **plain HTTP communication → fully-secured cryptographic system**

```
Task 1: Plain HTTP
   ↓
Task 2: Symmetric Encryption + Authentication
   ↓
Task 2.8: Replay Attack Prevention
   ↓
Task 3: RSA Key Exchange (no hardcoded keys)
   ↓
Task 4: Digital Certificates (prevent MITM)
```

---

## 📋 Quick Start

### Run Basic Communication (Task 1)
```bash
# Terminal 1
python3 server.py

# Terminal 2
python3 client.py
```

### Run Secure System (Task 2.8 + 3 + 4)

**Setup (once)**:
```bash
python3 keygen.py      # Creates: secret.key, public.key
python3 keygen_ca.py   # Creates: secret_ca.key, public_ca.key
python3 cert_key.py    # Creates: pk.cert
```

**Run System**:
```bash
# Terminal 1
python3 server_upd.py

# Terminal 2
python3 client_upd.py
```

---

## 🔐 Security Levels Explained

| Level | Method | What's Protected |
|-------|--------|---|
| **1** | Plain HTTP | ❌ Nothing |
| **2.1** | Hardcoded Key + AES | ✅ Confidentiality |
| **2.3** | Pre-shared Secret + HMAC | ✅ Integrity |
| **2.6** | Pre-shared Secret + GCM | ✅ Confidentiality + Integrity |
| **2.8** | GCM + Sequence Numbers | ✅ + Prevents Replay Attacks |
| **3** | RSA Key Exchange + GCM | ✅ + No Hardcoded Secrets |
| **4** | Certificates + RSA + GCM | ✅ + Prevents Man-in-the-Middle |

---

## 🛡️ Attack Prevention Matrix

```
                    Plain   AES-CBC  HMAC   GCM   Seq#   RSA    Certs
Eavesdropping       ❌      ✅       ❌     ✅    ✅     ✅     ✅
Tampering           ❌      ❌       ✅     ✅    ✅     ✅     ✅
Fake Server         ❌      ❌       ✅     ✅    ✅     ✅     ✅
Replay Attack       ❌      ❌       ❌     ❌    ✅     ✅     ✅
MITM / Spoofing     ❌      ❌       ❌     ❌    ❌     ⚠️*    ✅
Keylogger           ❌      ✅       ✅     ✅    ✅     ✅     ✅
```
*RSA alone: needs session key, no way to verify server. Certificates solve this.

---

## 📁 File Structure

### Core Implementation
```
server.py              → Plain HTTP server (Task 1)
client.py             → Plain HTTP client (Task 1)
crypto_utils.py       → All encryption functions (ENHANCED)
```

### Key Generation
```
keygen.py             → Generate server RSA keys
keygen_ca.py          → Generate CA RSA keys
cert_key.py           → Generate signed certificate
```

### Task 2 Variants (Educational)
```
serverp2S2.py         → AES-CBC (encryption only)
serverp2S3.py         → HMAC (integrity only)
serverpart2step6.py   → AES-GCM (both)
step7replay.py        → Replay attack demo
```

### Integrated Systems
```
server_upd.py         → Task 2.8+3+4 server (full features)
client_upd.py         → Task 2.8+3+4 client (full features)
```

---

## 🔑 Key Concepts

### Confidentiality = Only intended recipient can read
- **Provider**: Encryption (AES)
- **Attack**: Eavesdropping (solved by AES)

### Integrity = Data hasn't been modified
- **Provider**: MAC or GCM tag (HMAC, SHA256)
- **Attack**: Tampering (solved by MAC/GCM)

### Authenticity = Data came from claimed sender
- **Provider**: MAC key ownership or signature
- **Attack**: Forgery (solved by authentication)

### Freshness = Data is recent, not replayed
- **Provider**: Sequence numbers, timestamps, nonces
- **Attack**: Replay (solved by sequence numbers)

### Non-repudiation = Sender can't deny sending
- **Provider**: Digital signatures
- **Attack**: Denial (solved by certificates)

---

## 🚀 Protocol Comparison

### Without Certificates (Task 3)
```
Client              Server
  |                  |
  ├→ Get pub key ←─┤  (INSECURE: could be attacker's key)
  |                  |
  ├→ Encrypt K with ←┤  (Attacker intercepts, replaces key)
     pub key
  |                  |
  └→ Use exchanged K ← (Both sides have different keys!)
```
**Problem**: No way to verify server's key is authentic

### With Certificates (Task 4)
```
Client              CA              Server
  |                 |                |
  |              (trust)             |
  |←─ CA pub key ─→|                |
  |                 |                |
  |                 |           (trust)
  |                 |←─ CA signs pub key ←┤
  |                 |      (certificate)   |
  |←─────────────── cert + pub key ←┤
  |                 |                |
  | Verify sig with CA pub key   |
  | ✓ Server is legitimate!      |
  |                 |                |
  | Encrypt K with verified pub key
  |───→ Use exchanged K ───────→ |
```
**Solution**: Certificate proves server's public key

---

## 🧪 Testing Scenarios

### Scenario 1: Replay Attack (Task 2.7 vs 2.8)

**Without Protection (Task 2.6)**:
```bash
Server response: {nonce, ciphertext, tag, seq=NONE}
Attacker: Saves response, replays it multiple times
Client:   GCM tag still valid (no freshness check)
Result:   ❌ Same weather data shown 10 times
```

**With Protection (Task 2.8)**:
```bash
Server response 1: {nonce, ciphertext, tag, seq=1}
Client accepts:    seq=1 > last_seq=0 ✓

Server response 2: {nonce, ciphertext, tag, seq=2}
Client accepts:    seq=2 > last_seq=1 ✓

Replay attack:     {nonce, ciphertext, tag, seq=1}
Client rejects:    seq=1 !> last_seq=2 ✗
```

### Scenario 2: Man-in-the-Middle (Task 3 vs 4)

**Without Certificates (Task 3)**:
```bash
Client              Attacker              Server
  |                  |                      |
  ├─ Get pub key ──→ |  ← captures message
  |←─ fake_key ──    |
  |                  |                      |
  | Encrypts session key with attacker's key
  ├─ encrypted(K) ──→|  ← gets session key
  | ❌ Attacker now knows K!
```

**With Certificates (Task 4)**:
```bash
Client              Attacker              Server
  |                  |                      |
  ├─ Get pub key ──→ |  ← captures message
  |←─ fake_cert ──   |  (unsigned by CA)
  |                  |                      |
  | Verify cert signature with CA public key
  | ❌ Signature doesn't match!
  | Reject certificate
```

---

## 📊 Algorithm Choices & Security

| Algorithm | Choice | Why Not Alternative |
|-----------|--------|---|
| AES | ✅ | Not: RC4 (broken), DES (weak), Plaintext |
| 128-bit key | ✅ | Not: 64-bit (weak), too large overhead |
| GCM mode | ✅ | Not: ECB (deterministic), CBC alone (no auth) |
| RSA-2048 | ✅ | Not: 1024-bit (weak after 2013), ECC only |
| RSA-OAEP | ✅ | Not: PKCS1v15 (vulnerable to CCA) |
| RSA-PSS | ✅ | Not: PKCS1v15 (not probabilistic) |
| HMAC-SHA256 | ✅ | Not: MD5 (broken), SHA1 (weak), CRC |
| os.urandom() | ✅ | Not: random.random() (not cryptographic), time() |

---

## 🎓 Learning Path

1. **Task 1**: Understand HTTP and JSON
2. **Task 2.1-2.2**: Learn block cipher modes (CBC, IVs)
3. **Task 2.3**: Learn MAC and authentication
4. **Task 2.5-2.6**: Learn authenticated encryption (GCM)
5. **Task 2.7-2.8**: Learn replay attacks and prevention
6. **Task 3**: Learn RSA and public-key cryptography
7. **Task 4**: Learn digital certificates and PKI

---

## 📈 Performance

| Operation | Speed | When Used |
|-----------|-------|-----------|
| AES-128 encrypt/decrypt | <1ms | Every request |
| RSA-2048 encrypt | 10-20ms | Once per session |
| RSA-2048 decrypt | 10-20ms | Once per session |
| GCM auth tag | <1ms | Every request |
| Certificate verify | 5-10ms | Session setup |

**Throughput**: 1000+ messages/sec is typical

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: cryptography` | `pip install cryptography` |
| `Address already in use :5081` | Kill old process or use different XY |
| `Connection refused` | Check server is running in another terminal |
| `Certificate verification failed` | Run keygen.py → keygen_ca.py → cert_key.py in order |
| `Permission denied` secret.key | Check file permissions: `chmod 600 secret*.key` |

---

## 📚 References

### NIST Standards
- SP 800-38D: GCM mode specification
- SP 800-38A: CBC mode specification
- SP 800-57: Key management guidelines

### RFCs
- RFC 8017: PKCS #1 RSA (latest)
- RFC 2104: HMAC
- RFC 3394: AES Key Wrap

### Python Docs
- https://cryptography.io/ - Cryptography library
- https://docs.python-requests.org/ - Requests HTTP library
- https://flask.palletsprojects.com/ - Flask web framework

---

## ✅ Verification Checklist

Before submission, verify:

- [ ] All Python files run without errors
- [ ] keygen.py generates secret.key and public.key
- [ ] keygen_ca.py generates secret_ca.key and public_ca.key
- [ ] cert_key.py generates pk.cert
- [ ] server_upd.py starts on port 5081
- [ ] client_upd.py connects and verifies certificate
- [ ] Sequence numbers increment (no replay)
- [ ] README.md has clear setup instructions
- [ ] All code is commented with security notes
- [ ] Documentation files are complete

---

**Quick Links**:
- Full Docs: See `README.md`
- Verification: See `VERIFICATION_AND_APPROACH.md`
- Summary: See `IMPLEMENTATION_SUMMARY.md`

**Need Help?** Check the example scenarios above or review the documentation files.
