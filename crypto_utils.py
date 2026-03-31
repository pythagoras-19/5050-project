"""
crypto_utils.py - Cryptographic Utilities for Secure Client-Server Communication

This module provides:
1. Authenticated Encryption (AES-128-GCM)
2. Data Integrity (HMAC-SHA256)
3. RSA Key Exchange (for Task 3+)
4. Certificate Verification (for Task 4+)

All operations use standard cryptographic libraries (cryptography.io) with:
- No hardcoded keys in final version (except for legacy Task 2 mode)
- Proper nonce handling
- Constant-time verification
- Standard padding schemes
"""

import os
import json
import hmac
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding

# ===== LEGACY: Task 2 Hardcoded Key (for backward compatibility) =====
KEY = b"mohammed_5050key"  # 128-bit key for Task 2


# ===== TASK 2: Symmetric Encryption (AES-CBC) =====

def encrypt_data(data):
    """
    Encrypt data using AES-128-CBC.
    
    Args:
        data: Dictionary or string to encrypt
        
    Returns:
        (iv, ciphertext) tuple, both as bytes
        
    Security Notes:
        - Random 128-bit IV generated for each encryption
        - PKCS7 padding applied automatically
        - IV must be sent with ciphertext (it's not secret)
        - Same plaintext + different IV = different ciphertext (IND-CPA)
    """
    iv = os.urandom(16)  # 128-bit random IV
    
    plaintext = json.dumps(data).encode()
    
    # Apply PKCS7 padding (required for block cipher)
    # - Pads to 16-byte multiple
    # - Padding value = number of padding bytes
    # - Prevents padding oracle attacks when combined with authentication
    padder = padding.PKCS7(128).padder()
    padded_plaintext = padder.update(plaintext) + padder.finalize()
    
    # AES-128-CBC encryption
    cipher = Cipher(algorithms.AES(KEY), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
    
    return iv, ciphertext


def decrypt_data(iv, ciphertext):
    """
    Decrypt data using AES-128-CBC.
    
    Args:
        iv: 16-byte initialization vector
        ciphertext: Encrypted bytes
        
    Returns:
        Decrypted dictionary
        
    Raises:
        ValueError: If padding is invalid (but does NOT protect against tampering)
    """
    cipher = Cipher(algorithms.AES(KEY), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    
    # Remove PKCS7 padding
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    
    return json.loads(plaintext.decode())


# ===== TASK 2: Message Authentication Code (HMAC-SHA256) =====

def make_tag(data_bytes):
    """
    Generate HMAC-SHA256 authentication tag.
    
    Args:
        data_bytes: Bytes to authenticate
        
    Returns:
        64-character hex string (256 bits as hex)
        
    Security Notes:
        - Uses hardcoded KEY for Task 2
        - SHA256 provides 256-bit security
        - Deterministic: same input = same output
    """
    return hmac.new(KEY, data_bytes, hashlib.sha256).hexdigest()


def check_tag(data_bytes, tag):
    """
    Verify HMAC-SHA256 authentication tag.
    
    Args:
        data_bytes: Bytes to verify
        tag: Received hex string tag
        
    Returns:
        True if tag is valid, False otherwise
        
    Security Notes:
        - Uses constant-time comparison (hmac.compare_digest)
        - Prevents timing attacks
        - Leaks tag length but unavoidable
    """
    expected_tag = make_tag(data_bytes)
    return hmac.compare_digest(expected_tag, tag)


# ===== TASK 2.8 & TASK 3: Authenticated Encryption (AES-GCM) =====

def encrypt_data_gcm(data, session_key=None):
    """
    Encrypt and authenticate data using AES-128-GCM.
    
    Args:
        data: Dictionary to encrypt and authenticate
        session_key: 16-byte session key (uses KEY if None)
        
    Returns:
        (nonce, ciphertext, tag) tuple as bytes
        
    Security Notes:
        - GCM provides authenticated encryption (AEAD)
        - 12-byte random nonce for each message
        - 16-byte authentication tag
        - NEVER reuse nonce with same key (would break security completely)
        - Each call creates new cipher instance → different nonce
    """
    if session_key is None:
        session_key = KEY
    
    plaintext = json.dumps(data).encode()
    nonce = os.urandom(12)
    
    # Create GCM cipher (automatically generates 12-byte nonce)
    cipher = Cipher(algorithms.AES(session_key), modes.GCM(nonce))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    tag = encryptor.tag
    
    return nonce, ciphertext, tag


def decrypt_data_gcm(nonce, ciphertext, tag, session_key=None):
    """
    Decrypt and verify data using AES-128-GCM.
    
    Args:
        nonce: 12-byte nonce (must match encryption nonce)
        ciphertext: Encrypted bytes
        tag: 16-byte authentication tag
        session_key: 16-byte session key (uses KEY if None)
        
    Returns:
        Decrypted dictionary
        
    Raises:
        cryptography.exceptions.InvalidTag: If tag verification fails
        
    Security Notes:
        - Tag verification prevents tampering with ciphertext or nonce
        - Fails atomically: no partial decryption on tag failure
        - Protects both confidentiality and authenticity
    """
    if session_key is None:
        session_key = KEY
    
    cipher = Cipher(algorithms.AES(session_key), modes.GCM(nonce, tag))
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    
    return json.loads(plaintext.decode())


# ===== TASK 3: RSA Key Exchange =====

def encrypt_key_with_public_key(session_key, server_public_key):
    """
    Encrypt a session key using RSA public key encryption.
    
    Args:
        session_key: 16-byte AES key to encrypt
        server_public_key: RSA public key (cryptography object or PEM bytes)
        
    Returns:
        Encrypted bytes (ciphertext)
        
    Encryption Scheme:
        RSA-OAEP (Optimal Asymmetric Encryption Padding)
        - Probabilistic: different ciphertext each time (even with same key)
        - Recommended by OAEP (RFC 8017)
        - Uses SHA256 for hash function and mask generation
        - Prevents chosen-ciphertext attacks
        
    Security Notes:
        - 2048-bit RSA key: Security equivalent to ~112-bit symmetric key
        - OAEP adds ~66 bytes of overhead
        - Session key (16 bytes) easily fits in RSA modulus
    """
    # Load key if given as PEM bytes
    if isinstance(server_public_key, bytes):
        server_public_key = serialization.load_pem_public_key(server_public_key)
    
    # Encrypt with RSA-OAEP using SHA256
    encrypted_session_key = server_public_key.encrypt(
        session_key,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return encrypted_session_key


def decrypt_key_with_private_key(encrypted_session_key, server_private_key):
    """
    Decrypt a session key using RSA private key.
    
    Args:
        encrypted_session_key: Encrypted bytes from client
        server_private_key: RSA private key (cryptography object or PEM bytes)
        
    Returns:
        16-byte session key
        
    Raises:
        cryptography.exceptions.InvalidKey: If decryption fails
    """
    # Load key if given as PEM bytes
    if isinstance(server_private_key, bytes):
        server_private_key = serialization.load_pem_private_key(
            server_private_key, password=None
        )
    
    # Decrypt with RSA-OAEP (must match encryption parameters)
    session_key = server_private_key.decrypt(
        encrypted_session_key,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return session_key


# ===== TASK 4: Certificate Verification =====

def verify_certificate(cert_data, ca_public_key):
    """
    Verify a server certificate signed by authorized CA.
    
    Certificate Format:
        [message bytes]\n[RSA-PSS signature bytes]
        
    Message Format:
        "This public key: [n_hex]:[e_hex] belongs to [student_id]."
        
    Args:
        cert_data: Raw certificate bytes (from pk.cert)
        ca_public_key: CA's public key (bytes in PEM format or cryptography object)
        
    Returns:
        (is_valid: bool, message: str, server_public_key: bytes)
        
    Raises:
        cryptography.exceptions.InvalidSignature: If signature verification fails
        
    Security Notes:
        - RSA-PSS signature verified with SHA256
        - Signature must be valid: only CA can create valid signatures
        - Message is extracted and returned for inspection
        - Server's public key is extracted from message
    """
    # Load CA public key if given as PEM bytes
    if isinstance(ca_public_key, bytes):
        ca_public_key = serialization.load_pem_public_key(ca_public_key)
    
    # Parse certificate: message and signature separated by newline
    parts = cert_data.split(b"\n", 1)
    if len(parts) != 2:
        return False, "Invalid certificate format", None
    
    message_bytes, signature = parts
    message_text = message_bytes.decode()
    
    try:
        # Verify RSA-PSS signature with SHA256
        ca_public_key.verify(
            signature,
            message_bytes,
            asym_padding.PSS(
                mgf=asym_padding.MGF1(hashes.SHA256()),
                salt_length=asym_padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Signature is valid
        return True, message_text, message_bytes
        
    except Exception as e:
        return False, f"Signature verification failed: {e}", None


def extract_public_key_from_message(message_text):
    """
    Extract server's public key hex from certificate message.
    
    Message Format:
        "This public key: [n_hex]:[e_hex] belongs to [student_id]."
        
    Args:
        message_text: Certificate message string
        
    Returns:
        (n_hex, e_hex) tuple or (None, None) if parsing fails
    """
    try:
        # Parse: "This public key: KEY_INFO belongs to ID."
        parts = message_text.split("This public key: ")
        if len(parts) < 2:
            return None, None
        
        rest = parts[1].split(" belongs to ")
        if len(rest) < 2:
            return None, None
        
        key_info = rest[0]  # "n_hex:e_hex"
        hex_parts = key_info.split(":")
        if len(hex_parts) != 2:
            return None, None
        
        n_hex, e_hex = hex_parts
        return n_hex, e_hex
        
    except:
        return None, None


# ===== TASK 2.8: Sequence Number Counter for Replay Prevention =====

class ReplayProtection:
    """
    Implements sequence number-based replay attack protection.
    
    Usage:
        server_proto = ReplayProtection()
        response = {..., "seq": server_proto.get_next_seq()}
        
        client_proto = ReplayProtection()
        if client_proto.accept_seq(response["seq"]):
            # Process response
        else:
            # Reject: replay attack detected
    """
    
    def __init__(self):
        """Initialize with sequence number 0."""
        self.sequence_number = 0
    
    def get_next_seq(self):
        """Get and increment sequence number (for server)."""
        self.sequence_number += 1
        return self.sequence_number
    
    def accept_seq(self, received_seq):
        """
        Check if received sequence number is valid (greater than last seen).
        
        Args:
            received_seq: Sequence number from received message
            
        Returns:
            True if seq > last_seq (fresh message), False otherwise (replay)
        """
        if received_seq > self.sequence_number:
            self.sequence_number = received_seq
            return True
        return False