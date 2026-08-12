# Side-Channel & Fault Attacks

### Differential Power Analysis (DPA) on AES

```python
def dpa_aes_theory():
    """
    Core principle: Power consumption correlates with Hamming weight of
    intermediate values during encryption.
    
    Attack on AES:
    1. Collect N power traces T_i[t] for known plaintexts P_i
    2. For each key byte guess k (0-255):
       a. Compute intermediate: S-box(P_i[byte] ⊕ k) after first round
       b. Predict power: Hamming weight of intermediate
       c. Correlate predicted power with actual traces at each time point
    3. Key byte with highest correlation peak is correct
    
    Number of traces needed: ~50-200 for unprotected AES-128 (SW),
    ~1K-10K for protected implementations.
    """
    pass

def cpa_vs_dpa():
    """
    Correlation Power Analysis (CPA) — more efficient than classic DPA:
    Uses Pearson correlation coefficient between predicted power model
    and actual measurements.
    
    Template Attack — strongest profiling attack:
    1. Profile phase: capture traces for known keys on IDENTICAL device
    2. Build multivariate Gaussian models per key value
    3. Attack phase: match new trace to closest template
    
    Single trace can recover key with good templates!
    """
    pass
```

### Differential Fault Analysis (DFA) on AES

```python
def dfa_aes():
    """
    Inject a fault (glitch/laser/EM pulse) during AES encryption,
    compare correct vs faulty ciphertext to recover key.
    
    Classic DFA on AES (Piret-Quisquater):
    1. Inject fault into state BEFORE MixColumns of round 8
    2. This affects exactly 1 byte of state → 4 bytes of round 9 output
    3. The differential propagates through MixColumns to 4 bytes of ciphertext
    
    Fault model: single byte flip at known/unknown position
    
    For a single fault:
    - If fault in diagonal 0: affects ciphertext bytes 0, 7, 10, 13
    - Known differential + inverse S-box → recover 4 key bytes
    - 4-8 faults → full key recovery
    
    Implementation:
    1. Get correct ciphertext C
    2. Get faulty ciphertext C' (same plaintext, fault injected)
    3. For each possible fault position (0-15):
       - Compute differential Δ = C ⊕ C'
       - Back-propagate through inverse ShiftRows, inverse MixColumns
       - Check which fault byte explains the differential
       - Recover round-10 key byte
    """
    pass

# RSA Fault Attack (Bellcore attack)
def rsa_bellcore_attack():
    """
    CRT-RSA: sign with both p and q using Chinese Remainder Theorem
    Fault one of the two exponentiations:
    
    Correct: S = CRT(S_p, S_q) where S_p = m^d mod p, S_q = m^d mod q
    Faulty: S' = CRT(S_p', S_q) where S_p' ≠ m^d mod p (fault injected)
    
    Then: S - S' is divisible by q but NOT by p
    → gcd(S - S', N) = q → factor N!
    
    SINGLE faulty signature can break RSA-CRT.
    Countermeasure: verify signature before output (S^e mod N == m)
    """
    pass

# Safe-Error Attack
def safe_error_attack():
    """
    Inject fault during dummy operations:
    - If operation was real → error detected → output suppressed
    - If operation was dummy → no error → normal output
    
    This reveals which operations are real vs dummy,
    breaking implementations with dummy operations for side-channel protection.
    """
    pass
```

---
