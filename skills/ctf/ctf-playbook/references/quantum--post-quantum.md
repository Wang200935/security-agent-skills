# Quantum & Post-Quantum

### Shor's Algorithm Impact

```python
def shor_algorithm_impact():
    """
    Shor's algorithm factors N in O((log N)³) quantum operations.
    
    Broken by Shor:
    - RSA (reduces to factoring)
    - DSA/ECDSA (reduces to discrete log)
    - Diffie-Hellman / ECDH (discrete log)
    - ElGamal
    - All elliptic curve crypto (ECDSA, EdDSA, ECDH...)
    
    Key sizes needed for classical security vs quantum:
    | Classic Security | RSA Key | ECC Key | AES Key |
    |:-----------------|:--------|:--------|:--------|
    | 128-bit          | 3072    | 256     | 128     |
    | Post-quantum     | BROKEN  | BROKEN  | 256*    |
    
    * Grover's algorithm gives quadratic speedup: AES-128 → 64-bit security
      → Use AES-256 for 128-bit post-quantum security
    """
    pass

def grover_algorithm():
    """
    Grover's algorithm: search unsorted database of N items in O(√N) time.
    
    Impact on symmetric crypto:
    - AES-128: 2^64 quantum operations → 64-bit security margin (too low)
    - AES-256: 2^128 quantum operations → 128-bit security (acceptable)
    - SHA-256 preimage: 2^128 quantum → 128-bit (acceptable)
    
    NIST recommendation: AES-256 + SHA-384 for post-quantum security.
    """
    pass

def harvest_now_decrypt_later():
    """
    "Store now, decrypt later" attack:
    - Adversaries collect encrypted traffic TODAY
    - Store it until quantum computers are available
    - Decrypt it then
    
    Impact: Data with long-term secrecy (gov't, medical, financial) needs
    post-quantum protection NOW, not when quantum computers arrive.
    
    Estimated timeline: "Q-Day" 2030-2040 (controversial; 500K physical qubits needed).
    """
    pass
```

---
