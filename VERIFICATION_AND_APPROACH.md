# Cryptographic System Development: Verification & Technical Approach

---

## PHASE 1: VERIFICATION OF TASK 1 & TASK 2

### TASK 1: REST Server/Client Basic Communication

#### Requirement 1.1: REST Server with `/weather` Endpoint (Port 50XY)
**File: `server.py`**
```python
@app.get("/weather")
def weather():
    data = {
        "location": "Denton, TX",
        "temperature_c": 10,
        "temperature_f": 50,
        "condition": "Partly Cloudy",
        "humidity_percent": XY  # XY = 81
    }
    return jsonify(data)
```
- **Port**: `127.0.0.1:5081` ✅ 
- **JSON Structure**: Matches specification exactly ✅
- **Endpoint**: `/weather` GET method ✅

**Status: ✅ COMPLETED**

#### Requirement 1.2: Client Sends Request and Prints Response
**File: `client.py`**
```python
r = requests.get(url, timeout=5)
print("Status:", r.status_code)
print("Response JSON:")
print(r.json())
```
- **HTTP Client**: Uses `requests` library ✅
- **Response Handling**: Parses JSON and prints correctly ✅
- **Error Handling**: Includes timeout ✅

**Status: ✅ COMPLETED**

**Task 1 Overall: ✅ FULLY COMPLETED**

---

### TASK 2: Symmetric Encryption & Integrity

#### Requirement 2.1: Hardcoded Pre-Shared Secret Key
**File: `crypto_utils.py`**
```python
KEY = b"mohammed_5050key"  # Length: 16 bytes (128 bits) ✅
```
- **Key Size**: 128 bits (standard for AES-128) ✅
- **Pre-shared**: Both server and client hardcode this ✅

**Status: ✅ COMPLETED**

---

#### Requirement 2.2: Symmetric Encryption with Confidentiality
**Variant Files: `serverp2S2.py` & `Clientp2s2.py`**

**Encryption Implementation (crypto_utils.py):**
```python
def encrypt_data(data):
    iv = os.urandom(16)  # Random 128-bit IV ✅
    plaintext = json.dumps(data).encode()
    
    padder = padding.PKCS7(128).padder()
    padded_plaintext = padder.update(plaintext) + padder.finalize()
    
    cipher = Cipher(algorithms.AES(KEY), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
    
    return iv, ciphertext
```

**Cryptographic Analysis:**
- **Cipher**: AES-128-CBC ✅
- **Mode**: CBC (Cipher Block Chaining) 
  - ✅ Provides confidentiality
  - ❌ Does NOT provide authentication (covered in 2.3)
- **Nonce/IV**: 128-bit random IV ✅
  - ✅ IV is random for each encryption (using `os.urandom()`)
  - ✅ IV is sent in plaintext alongside ciphertext (standard practice)
- **Padding**: PKCS7 ✅
- **Key Derivation**: Hardcoded (appropriate for test phase)

**Decryption Implementation:**
```python
def decrypt_data(iv, ciphertext):
    cipher = Cipher(algorithms.AES(KEY), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    return json.loads(plaintext.decode())
```

**Security Properties Achieved:**
- ✅ **Confidentiality**: Eavesdropper cannot read plaintext (cannot decrypt without KEY)
- ✅ **IND-CPA**: Indistinguishability under Chosen Plaintext Attack (CBC mode with random IV)
- ✅ **Nonce Handling**: New IV per message ensures different ciphertexts for same plaintext

**Status: ✅ COMPLETED** (Confidentiality verified)

---

#### Requirement 2.3: Data Integrity Using MAC (Unencrypted)
**Variant Files: `serverp2S3.py` & `clientp2S3.py`**

**MAC Implementation (crypto_utils.py):**
```python
def make_tag(data_bytes):
    return hmac.new(KEY, data_bytes, hashlib.sha256).hexdigest()

def check_tag(data_bytes, tag):
    expected_tag = make_tag(data_bytes)
    return hmac.compare_digest(expected_tag, tag)
```

**Cryptographic Analysis:**
- **MAC Scheme**: HMAC-SHA256 ✅
- **Key**: 128-bit shared key ✅
- **Hash Function**: SHA256 (cryptographically secure) ✅
- **Tag Verification**: Constant-time comparison using `hmac.compare_digest()` ✅
  - ❌ Prevents timing attacks in verification
  - ✅ Server returns data in plaintext (demonstrates confidentiality is separate from integrity)
- **Server Response**: 
  ```python
  return jsonify({
      "data": data,           # Plaintext!
      "tag": tag              # Full 64-char hex MAC
  })
  ```

**Security Properties:**
- ✅ **Integrity**: Guarantees data was not modified (attacker cannot forge without KEY)
- ✅ **Authenticity**: Only holder of shared KEY can create valid MAC
- ✅ **MAC Saved**: `tag.txt` file contains the MAC from legitimate server

**Status: ✅ COMPLETED** (Note: Data is in plaintext by design, showing MAC is separate from encryption)

---

#### Requirement 2.4: Fake Server Attack (Port 50XY+1)
**Attacker Implementation: `server_fake.py`**
```python
@app.route("/weather", methods=["GET"])
def weather():
    fake_data = {
        "humidity_percent": XY + 1  # 82 instead of 81
    }
    
    with open("tag.txt", "r") as f:
        old_tag = f.read().strip()  # Reuse intercepted tag
    
    return jsonify({
        "data": fake_data,
        "tag": old_tag  # ❌ Invalid for fake_data!
    })
```

**Attack Scenario:**
1. Attacker intercepts response from legitimate server
2. Attacker reads `tag.txt` containing HMAC of legitimate data
3. Attacker creates fake server on port 5082 with different humidity (82)
4. Attacker reuses the old tag

**Defense Test: `clientp2S4.py`**
```python
if check_tag(data_bytes, tag):
    print("Fake server response accepted.")  # ❌ Would suggest vulnerability
else:
    print("Fake server response rejected.")   # ✅ Expected result
```

**Why Attack Fails:**
- MAC is computed over `json.dumps(data, separators=(",", ":"))` with exact formatting
- Changing humidity from 81 to 82 changes JSON bytes
- Old tag was computed over old JSON
- `hmac.compare_digest(old_tag, new_tag)` returns False
- **Attack is prevented** ✅

**Status: ✅ COMPLETED** (Fake server attack is correctly prevented)

---

#### Requirement 2.5-2.6: Authenticated Encryption (AES-GCM)
**Variant Files: `serverpart2step6.py` & `clienpart2step6.py`**

**Implementation (using pycryptodome):**
```python
# Server
from Crypto.Cipher import AES

cipher = AES.new(KEY, AES.MODE_GCM)
ciphertext, tag = cipher.encrypt_and_digest(plaintext)

response = {
    "nonce": base64.b64encode(cipher.nonce).decode(),
    "ciphertext": base64.b64encode(ciphertext).decode(),
    "tag": base64.b64encode(tag).decode()
}
```

**Cryptographic Analysis:**
- **Cipher**: AES-128-GCM ✅
- **Mode**: GCM (Galois/Counter Mode)
  - ✅ Provides confidentiality (encryption)
  - ✅ Provides authenticity (authentication tag)
  - ✅ Authenticated Encryption with Associated Data (AEAD)
- **Nonce**: 12-byte random nonce ✅
  - ✅ Generated by `AES.new(KEY, AES.MODE_GCM)` automatically
  - ✅ Different nonce for each message (new cipher instance)
- **Authentication Tag**: 16-byte GCM tag ✅
  - ✅ Covers both ciphertext and nonce
  - ✅ Prevents tampering with either

**Client Decryption:**
```python
cipher = AES.new(KEY, AES.MODE_GCM, nonce=nonce)
try:
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    print("✅ Decrypted & authenticated:")
except:
    print("❌ Authentication failed")
```

**Security Properties Achieved:**
- ✅ **Confidentiality**: Ciphertext reveals nothing about plaintext
- ✅ **Integrity**: Any modification to ciphertext/nonce/tag causes decryption failure
- ✅ **Authenticity**: Only holder of KEY can create valid GCM tag
- ✅ **No Replay Prevention**: Same plaintext with same nonce would produce identical output
  - This is addressed in requirement 2.8

**Response Storage:**
```python
with open("response.bin", "wb") as f:
    f.write(json.dumps(response).encode())
```

**Status: ✅ COMPLETED** (Authenticated encryption working)

---

#### Requirement 2.7: Replay Attack (Server Superfake)
**Attacker Implementation: `step7replay.py`**
```python
@app.route("/weather", methods=["GET"])
def weather():
    with open("response.bin", "rb") as f:
        data = f.read()  # Replay exact response bytes
    
    return Response(data, mimetype="application/json")
```

**Attack Scenario:**
1. Attacker captures encrypted response: `{nonce, ciphertext, tag}`
2. Attacker stores it in `response.bin`
3. Attacker replays the EXACT same encrypted message
4. Client decrypts with the same nonce → same plaintext ✓
5. Client verifies GCM tag with same nonce → tag is valid ✓
6. **Replay succeeds** ❌

**Why This Is a Real Attack:**
- GCM with same nonce is deterministic
- Replayed message is cryptographically identical to original
- No freshness guarantee exists
- Only prevents tampering, not replay

**Status: ❌ INCOMPLETE** - Vulnerability exists, needs countermeasure

---

#### Requirement 2.8: Replay Attack Countermeasure
**Required Files: `server_upd.py` & `client_upd.py`**
**Status: ❌ MISSING** - These files do not exist

**What Should Be Implemented:**
- **Counter/Sequence Number**: Track message count from server
- **Timestamp-based**: Include timestamp in auth data (with clock drift allowance)
- **Challenge-response**: Client sends nonce, server uses it in response

**Countermeasure Design (Sequence Number):**
```
Client → Server: GET /weather + sequence=0
Server → Client: {nonce, ciphertext, tag, sequence=1} (authenticated)
Client stores: last_sequence=1
Next request:
Client → Server: GET /weather + sequence=1  
Server → Client: {nonce, ciphertext, tag, sequence=2}
Client checks: sequence=2 > last_sequence=1 ✓
Client accepts, stores: last_sequence=2
Replayed message with sequence=1 < last_sequence=2 → REJECTED ✓
```

---

### SUMMARY: TASK 1 & 2 COMPLETION STATUS

| Task | Component | Status | Notes |
|------|-----------|--------|-------|
| 1.1 | REST Server /weather endpoint | ✅ | Correct port, JSON structure |
| 1.2 | REST Client | ✅ | Requests HTTP, prints response |
| 2.1 | Pre-shared symmetric key | ✅ | 128-bit AES key |
| 2.2 | Encryption (Confidentiality) | ✅ | AES-128-CBC with random IV |
| 2.3 | MAC (Integrity) | ✅ | HMAC-SHA256 with constant-time verification |
| 2.4 | Fake server attack prevention | ✅ | MAC binds data to specific content |
| 2.5-2.6 | Authenticated encryption | ✅ | AES-128-GCM provides AEAD |
| 2.7 | Replay attack scenario | ✅ | Vulnerability demonstrated |
| 2.8 | Replay attack countermeasure | ❌ | Missing `server_upd.py` & `client_upd.py` |

**Overall Status: 87.5% Complete** (7/8 requirements met)

---

## PHASE 2: TECHNICAL APPROACH & SYSTEM EVOLUTION

### 2.1: Plain Communication (Task 1)

**Architecture:**
```
Client                                Server
  |                                     |
  |-------- GET /weather ------>|       |
  |                             |-------|
  |<----- JSON Response -------|       |
  |                                     |
```

**Communication Flow:**
1. Client initiates HTTP GET request to `http://127.0.0.1:5081/weather`
2. Server receives request on Flask `@app.get("/weather")`
3. Server constructs static JSON dictionary with hardcoded weather data
4. Server serializes JSON and sends as HTTP response
5. Client receives response, parses JSON, prints to stdout

**Security Properties:**
- **Confidentiality**: ❌ NONE - All data sent in plaintext
- **Integrity**: ❌ NONE - No integrity protection
- **Authenticity**: ❌ NONE - No authentication
- **Freshness**: ❌ NONE - Same response every request (no nonce)

**Threat Model:**
- ✅ Vulnerable to: Eavesdropping (plaintext sniffing with Wireshark)
- ✅ Vulnerable to: Man-in-the-middle attacks (impersonation)
- ✅ Vulnerable to: Replay attacks (static content)

---

### 2.2: Confidentiality Only - Symmetric Encryption (Task 2.2)

**Upgrade: AES-128-CBC Encryption**

**Why AES?**
- Industry standard (NIST-approved)
- Fast and efficient
- Well-vetted cryptanalysis
- Hardware acceleration available (AES-NI on modern CPUs)

**Why CBC Mode?**
- **Randomized**: Each encryption produces different ciphertext (due to random IV)
- **Provides IND-CPA**: Indistinguishable under Chosen Plaintext Attack
- **Chaining**: Plaintext block affects all subsequent ciphertext blocks
- **IV requirement**: Must send IV with ciphertext (standard practice)

**Why PKCS7 Padding?**
- Mandatory for block ciphers (AES needs 16-byte multiple)
- Prevents padding oracle attacks (when combined with proper authentication)

**Why Not Stream Ciphers (RC4)?**
- ❌ RC4 is broken (biased keystream)
- ❌ No nonce handling
- ❌ Deprecated

**Architecture:**
```
Client                                    Server
  |                                         |
  |-------- GET /weather ------>           |
  |                               |---------|
  |<-- {IV, Ciphertext} (AES) ----|         |
  |                                         |
```

**Encryption Flow (Server):**
1. Generate 128-bit random IV: `iv = os.urandom(16)` ✅
2. Serialize data to JSON bytes
3. Apply PKCS7 padding to reach 16-byte multiple
4. Encrypt with AES-128-CBC using KEY and IV
5. Return both IV and ciphertext (IV must be public)

**Decryption Flow (Client):**
1. Receive IV and ciphertext from server
2. Decrypt using AES-128-CBC with same KEY and IV
3. Remove PKCS7 padding
4. Deserialize JSON bytes to data dictionary

**Security Properties Achieved:**
- **Confidentiality**: ✅ ACHIEVED
  - Attacker with ciphertext cannot recover plaintext without KEY
  - Eavesdropper sees only binary ciphertext, no JSON structure
- **IND-CPA Security**: ✅ ACHIEVED
  - Same plaintext encrypts to different ciphertext each time (random IV)
  - Attacker cannot distinguish between two encryptions of different messages

**Attack Still Possible:**
- ❌ **Integrity**: No protection - attacker can flip ciphertext bits
- ❌ **Authenticity**: No proof message came from legitimate server
- ❌ **Replay**: Same encrypted message accepted multiple times

---

### 2.3: Integrity Only - HMAC (Task 2.3)

**Upgrade: Message Authentication Code**

**Why Fall Back to Unencrypted?**
- Demonstrates separation of concerns
- Shows integrity ≠ confidentiality
- Allows viewing MAC in Wireshark

**Why HMAC?**
- **Keyed algorithm**: Requires shared secret
- **Provably secure**: Security reduces to underlying hash function
- **Fast**: One-pass algorithm

**Why SHA256 (not SHA1)?**
- ✅ SHA256: 256-bit output, no collision vulnerabilities
- ❌ SHA1: Deprecated, collision attacks known
- ✅ SHA256 > CRC32, MD5 alternatives

**MAC Generation:**
```
MAC = HMAC-SHA256(KEY, message)
example: 
  KEY = b"mohammed_5050key" (128 bits)
  message = b'{"location":"Denton, TX","temperature_c":10,...}'
  HMAC = 64-char hex string (256 bits encoded)
```

**Constant-Time Verification:**
```python
hmac.compare_digest(computed_tag, received_tag)
```
- ✅ Prevents timing attacks
- ❌ Leaks tag length (unavoidable)
- Standard approach across all crypto libraries

**Response Format:**
```json
{
  "data": {"location": "Denton, TX", ...},
  "tag": "a3f4e2d1c5..."
}
```

**Security Properties:**
- **Integrity**: ✅ ACHIEVED
  - Attacker cannot modify data without recomputing MAC
  - MAC binds data precisely as serialized
- **Authenticity**: ✅ ACHIEVED
  - Only holder of KEY can produce valid MAC
- **Replay**: ✅ PARTIALLY - Same message always has same MAC (predictable)

**Why This Attack Works (Fake Server at 5082):**
- Any change to JSON (e.g., humidity 81→82) changes the data bytes
- Old MAC (computed on humidity=81) no longer matches
- New JSON with old MAC fails verification
- **Attack is prevented** ✓

---

### 2.4: Authenticated Encryption - AES-GCM (Task 2.5-2.6)

**Upgrade: AEAD (Authenticated Encryption with Associated Data)**

**Why GCM?**
- **Combines encryption + authentication**: Single operation
- **AEAD mode**: Protects ciphertext integrity
- **Nonce-based**: Supports large volume of messages with single key
- **Two-pass verification**: `decrypt_and_verify()` ensures both properties

**Why Not Encrypt-Then-MAC Manually?**
- ✅ We COULD do MAC(ciphertext) separately, but
- ✅ GCM is standardized, vetted, and simpler  
- ✅ Parallelizable in hardware
- ✅ One authentication tag, not two

**Nonce vs IV:**
- **GCM Nonce**: 12 bytes (96 bits), NOT random per message ideally
  - ✅ AES-GCM.new() generates 12-byte random nonce by default
  - ⚠️ If nonce were reused: CATASTROPHIC (complete break)
- **CBC IV**: 16 bytes (128 bits), MUST be random (or XOR mode)
  - ✅ AES-CBC requires random IV always

**Nonce Reuse Risk:**
```
GCM Vulnerability: If nonce N repeats with same key K:
  1. Attacker gets: (M1, E(K, N, M1), tag1) and (M2, E(K, N, M2), tag2)
  2. XOR ciphertexts: E1 ⊕ E2 = M1 ⊕ M2 (nonce cancels out)
  3. Attacker recovers: M1 ⊕ M2 (devastating)
  4. Can forge arbitrary tags

Mitigation: NEVER reuse nonce with same key
```

**GCM Authentication Tag:**
- **16 bytes** (128 bits) of authentication power
- Computed over: plaintext + associated data (if used) + nonce
- Verifies: ciphertext integrity + nonce authenticity

**Architecture:**
```
Client                                      Server
  |                                           |
  |-------- GET /weather ------>              |
  |                                 |---------|
  |<-- {nonce, ciphertext, tag} ----|       |
  |<-- (all authenticated)                   |
```

**Server-Side GCM Encryption:**
```python
cipher = AES.new(KEY, AES.MODE_GCM)          # Creates new nonce automatically
ciphertext, tag = cipher.encrypt_and_digest(plaintext)
response = {
    "nonce": base64.b64encode(cipher.nonce).decode(),
    "ciphertext": base64.b64encode(ciphertext).decode(),
    "tag": base64.b64encode(tag).decode()
}
```

**Client-Side GCM Decryption:**
```python
cipher = AES.new(KEY, AES.MODE_GCM, nonce=nonce)
plaintext = cipher.decrypt_and_verify(ciphertext, tag)
```

**Security Properties:**
- **Confidentiality**: ✅ ACHIEVED - Ciphertext reveals nothing
- **Integrity**: ✅ ACHIEVED - Tag protects ciphertext
- **Authenticity**: ✅ ACHIEVED - Tag proves possession of KEY
- **Nonce Uniqueness**: ⚠️ ASSUMED - Implementation ensures unique nonce per message

---

### 2.5: Replay Attack Vulnerability (Task 2.7)

**Attack: Server-Superfake Replays Captured Response**

**Why GCM Alone Is Insufficient:**
```
Message 1: {nonce_1, ciphertext_1, tag_1} at time T
Message 2: {nonce_1, ciphertext_1, tag_1} at time T+10 (same!)

Cryptographically:
- Different nonces → Different tags ✓ (prevents this exact attack)
- SAME nonce → SAME tag ✓ (allows this attack if nonce repeats)

Current implementation: Nonce DIFFERS each time
- So replayed message would have DIFFERENT nonce than fresh message
- But: If attacker records full message {nonce, ciphertext, tag}
  Then: Replaying entire bundle is valid
  Why: GCM tag covers that specific nonce
```

**Replay Attack Flow:**
1. Client makes request at time T1: `GET /weather`
2. Server responds at T1: `{nonce_N, ciphertext_C, tag_T}`
3. Attacker captures this response, stores in `response.bin`
4. Client makes request at time T2
5. Attacker replays response: `{nonce_N, ciphertext_C, tag_T}` (IDENTICAL)
6. Client decrypts & verifies → ✓ Valid
7. **Problem**: Client cannot distinguish between fresh response and replay

**Why This Matters:**
- Application receives same data repeatedly
- No indication that response is stale
- Example: Weather shows "10°C" for 1 hour (was replaced by attacker)
- Example: Bank shows "Balance: $1000" repeatedly (attacker froze account view)

**Prevention Requires Freshness Mechanism:**
- Sequence numbers (stateful server validation)
- Timestamps (requires clock synchronization)
- Challenge-response (client sends nonce server must include)
- Expiration (short TTL on responses)

---

### 2.6: Replay Attack Countermeasure (Task 2.8)

**Design: Sequence Number Counter**

**Key Insight:**
- GCM verifies: "This message was encrypted with this key"
- GCM does NOT verify: "This message is fresh/new"
- Need additional mechanism for freshness

**Sequence Number Approach:**
```
Protocol Version 1:
  Server maintains: response_counter = 0

  Client Request:
    GET /weather?seq=0

  Server Response:
    {
      nonce: random_bytes,
      ciphertext: AES_GCM_encrypt(data || seq=1),
      tag: GCM_tag,
      sequence: 1          // NEW: Include seq in response
    }
    response_counter = 1

  Client-side:
    last_seq = 0          // Track received sequence
    {nonce, ct, tag, seq} = parse(response)
    
    plaintext = AES_GCM_decrypt(ct, tag, nonce)
    
    if seq <= last_seq:   // NEW: Check freshness
        REJECT("Replay attack!")
    else:
        last_seq = seq
        ACCEPT(plaintext)

  Replay Attack:
    Attacker sends captured response with seq=1
    Client compares: 1 <= 1 (last_seq still 1)
    Client REJECTS message ✓
```

**Alternative: Timestamp-Based Counter**
```
Server includes: timestamp + freshness_window (e.g., 5 seconds)
Client verifies: current_time - timestamp < freshness_window

Requires:
  - Clock synchronization (NTP)
  - Tolerance for clock drift
  - Rejection window
```

**Alternative: Challenge-Response**
```
Client → Server: GET /weather { challenge: random_N }
Server → Client: { nonce, ciphertext, tag, challenge_echo: N }
Client verifies: challenge_echo == challenge_sent

Prevents replay: Each client request generates new challenge
```

**Sequence Number Advantages:**
- ✅ Stateless from client perspective (no clock needed)
- ✅ Cryptographically sound
- ✅ No additional round-trips needed
- ❌ Server must maintain state per client
- ❌ Requires session management

---

## PHASE 3: TASK 3 & 4 - KEY EXCHANGE & CERTIFICATES

### Task 3: Public-Key Cryptography for Key Exchange

**Problem with Current Approach (Task 2):**
- Hardcoded symmetric key embedded in source code
- Key must be pre-shared out-of-band
- No scalability (different key per server needed)
- Key exposed if code is stolen

**Solution: RSA Key Exchange**
```
Client (no shared key)                Server (has RSA key pair)
                                      
                          ← Public key
Generate random session key K
Encrypt K with public key
Send encrypted(K) →

                        Decrypt with private key
                        Recover session key K
                        Both now share K
                        
Use K for AES-GCM ↔ Use K for AES-GCM
```

**Task 4: Certificates**

**Problem with Task 3:**
```
Attacker intercepts:
  Server → Client: "Here's my public key: ..."
  
Attacker replaces with:
  Attacker → Client: "Here's MY public key: ..."
  
Client encrypts session key with attacker's key (worthless)
Classic MITM attack
```

**Solution: Digital Certificates**
```
Trusted CA (you):
  1. Verify server identity
  2. Sign server's public key with CA's private key
  3. Create certificate: "Key X belongs to Server Y"

Client (has CA's public key):
  1. Receive certificate from server
  2. Verify signature using CA public key
  3. Now trust the public key
```

---

## System Evolution Summary

| Phase | Method | Confidentiality | Integrity | Authenticity | Freshness | Status |
|-------|--------|-----------------|-----------|--------------|-----------|--------|
| **Task 1** | Plaintext | ❌ | ❌ | ❌ | ❌ | Basic |
| **Task 2.2** | AES-CBC | ✅ | ❌ | ❌ | ❌ | Encrypted |
| **Task 2.3** | HMAC-SHA256 | ❌ | ✅ | ✅ | ✅ | Authenticated |
| **Task 2.5** | AES-GCM | ✅ | ✅ | ✅ | ❌ | AEAD |
| **Task 2.8** | AES-GCM + Seq | ✅ | ✅ | ✅ | ✅ | Anti-Replay |
| **Task 3** | RSA + AES-GCM | ✅ | ✅ | ✅ | ✅ | Key Exchange |
| **Task 4** | Certs + RSA + AES | ✅ | ✅ | ✅ | ✅ | **Complete** |

---

