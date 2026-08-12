# Symmetric Cryptanalysis

### Differential Cryptanalysis (on reduced-round ciphers)

```python
# Core concept: Find input difference ΔX that produces predictable output
# difference ΔY with high probability p >> 2^{-n}

# For CTF reduced-round ciphers:
def differential_attack_simple():
    """
    1. Find high-probability differential trail through N-1 rounds
    2. Encrypt many plaintext pairs (P, P ⊕ ΔX)
    3. For last round, guess subkey bits
    4. Count how many pairs produce expected difference after partial decrypt
    5. Correct subkey maximizes count (wrong ≈ uniform)
    
    Common in CTF: 4-8 round custom Feistel/SPN with known S-box
    """
    pass

# Impossible Differential: Differential with probability 0
# Truncated Differential: Only predict partial output difference
```

### Linear Cryptanalysis (Matsui's Algorithm)

```python
def linear_cryptanalysis_overview():
    """
    Find linear approximation: Σ(plaintext bits) ⊕ Σ(ciphertext bits) = Σ(key bits)
    with bias ε = |p - 1/2| significantly > 0
    
    Piling-up lemma: total bias = 2^{n-1} * Π ε_i
    
    Attack complexity: ~ 1/ε² known plaintexts
    
    CTF scenario: given 10K-100K plaintext-ciphertext pairs for 4-8 round cipher
    → find linear approximation, recover last round key
    """
    pass
```

### Meet-in-the-Middle (MITM)

```python
def mitm_2des():
    """Double-DES: E_k2(E_k1(P)) = C
    MITM: 2^56 space, 2^57 time (vs 2^112 brute force)"""
    
    # Phase 1: Encrypt P with all k1, store (E_k1(P), k1)
    # Phase 2: Decrypt C with all k2, look up result in table
    
    forward = {}
    for k1 in range(2**56):  # simplified
        forward[encrypt(P, k1)] = k1
    
    for k2 in range(2**56):
        mid = decrypt(C, k2)
        if mid in forward:
            return forward[mid], k2  # possible key pair
    return None

# 3DES MITM: 2^112 attack vs 2^168 brute force
# Splice-and-cut MITM: apply to AES (Biryukov et al.)
```

### Slide Attack (on self-similar ciphers)

```python
def slide_attack_concept():
    """
    Applies when all rounds use SAME subkey (self-similarity).
    
    Key insight: If (P, C) and (P', C') satisfy P' = F(P) and C' = F(C),
    then the cipher "slides" by one round.
    
    Birthday paradox: among 2^{n/2} known PT/CT pairs,
    expect to find a "slid pair" with P' = F(P).
    
    Common target: ciphers with periodic key schedule
    (classic Feistel with identical round keys)
    """
    pass
```

### Related-Key Attacks

```python
def related_key_attack_aes256():
    """
    AES-256 is MORE vulnerable to related-key than AES-128!
    (Irony: longer key = more key schedule rounds = more relations to exploit)
    
    Biryukov-Khovratovich attack on AES-256:
    - Full 14-round related-key recovery: 2^99.5 time, 2^70.5 data
    - 2024 improvement: 13-round attack with lower complexity
    
    Not practical for CTF, but illustrates: longer keys ≠ always better
    """
    pass
```

---
