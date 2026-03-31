# Code Coverage and Test Results

Date: 2026-03-30

## Summary
A robust pytest suite was added to validate Task 1 through Task 4 behavior.

- Total tests: 13
- Result: 13 passed
- Command used:

```bash
.venv/bin/python -m pytest -q
```

Observed output:

```text
.............                                                            [100%]
```

## Coverage Commands Used

Full project coverage:

```bash
.venv/bin/python -m coverage run -m pytest -q
.venv/bin/python -m coverage report
```

Task-focused core coverage:

```bash
.venv/bin/python -m coverage report server.py crypto_utils.py keygen.py keygen_ca.py cert_key.py server_upd.py
```

## Full Project Coverage Snapshot

```text
Name                  Stmts   Miss  Cover
-----------------------------------------
TOTAL                   571    336    41%
```

Why total is lower: this repository contains many alternate step/variant scripts (for different lab stages) that are intentionally not all executed by one path.

## Task-Focused Coverage (Core Files)

```text
Name              Stmts   Miss  Cover
-------------------------------------
cert_key.py          44      4    91%
crypto_utils.py      96     16    83%
keygen.py            26      0   100%
keygen_ca.py         18      0   100%
server.py            10      2    80%
server_upd.py        89     26    71%
-------------------------------------
TOTAL               283     48    83%
```

This 83% task-focused coverage is the best indicator for Tasks 1-4 implementation quality.

## What Was Tested by Task

## Task 1
- /weather endpoint returns expected JSON schema and values.
- Verified status code 200 and field correctness.

Tests:
- tests/test_task1_rest.py

## Task 2
- AES-CBC encrypt/decrypt round-trip works.
- HMAC-SHA256 validates correct message and rejects tampered message.
- AES-GCM decrypt/verify succeeds for valid payload and rejects tampered ciphertext.
- Sequence-based replay protection accepts increasing sequence and rejects stale/replayed sequence.

Tests:
- tests/test_task2_crypto.py

## Task 3
- keygen.py generates RSA key files (secret.key/public.key).
- Generated keys load correctly and are 2048-bit.
- RSA-OAEP session key exchange succeeds (encrypt/decrypt session key).
- AES-GCM payload encryption/decryption works using exchanged session key.
- server_upd key-exchange routes work end-to-end via Flask test client:
  - GET /get_public_key
  - POST /exchange_key
  - GET /weather with decryptable GCM response

Tests:
- tests/test_task3_key_exchange.py
- tests/test_task34_server_routes.py

## Task 4
- keygen_ca.py generates CA keys.
- cert_key.py generates certificate using CA private key.
- Certificate verification passes with CA public key.
- Certificate tampering is detected and rejected.
- server_upd includes certificate in /get_public_key response when available.

Tests:
- tests/test_task4_certificates.py
- tests/test_task34_server_routes.py

## Robustness Notes
- Tests execute both unit-level crypto checks and integration-level route flows.
- Script-style setup files (keygen.py, keygen_ca.py, cert_key.py) are tested in-process and via subprocess paths.
- Security-relevant negative cases are covered:
  - Tampered GCM ciphertext rejection
  - Replayed sequence rejection
  - Tampered certificate rejection

## Important Fix Found During Testing
During test development, a bug was discovered and fixed in crypto_utils.py:
- AES-GCM nonce handling was corrected to return the generated nonce directly.

This fix was validated by passing Task 2/3 encryption tests.

## Test Files Added
- tests/test_task1_rest.py
- tests/test_task2_crypto.py
- tests/test_task3_key_exchange.py
- tests/test_task4_certificates.py
- tests/test_task34_server_routes.py

## Test Configuration Added
- pytest.ini
- .coveragerc

## Conclusion
The project now has repeatable, automated tests that demonstrate each task objective with strong task-focused coverage and passing security validations.
