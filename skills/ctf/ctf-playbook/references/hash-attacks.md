# Hash Attacks

### Hash Length Extension Attack

```python
import struct

def md_pad(message: bytes, key_len_hint: int = 0) -> bytes:
    """MD construction padding (MD5, SHA1, SHA256)."""
    ml = (key_len_hint + len(message)) * 8  # message length in bits
    message += b'\x80'
    while (len(message) + key_len_hint) % 64 != 56:
        message += b'\x00'
    message += struct.pack('>Q', ml)  # big-endian for SHA256
    return message

def hash_length_extension(original_hash: bytes, original_message: bytes, 
                         append_data: bytes, key_len: int, hash_func) -> bytes:
    """Extend a hash without knowing the secret key.
    Works for: MD5, SHA1, SHA256, SHA512 (all Merkle-Damgård constructions).
    NOT for: SHA3, BLAKE2, HMAC (immune).
    
    Example: hash = SHA256(key || message)
    → We can compute SHA256(key || message || padding || append_data)
    without knowing key!
    """
    # 1. Pad original message as if key_len + message_len
    padded = md_pad(original_message, key_len)
    
    # 2. Set internal state to original hash
    # 3. Process append_data + new padding
    # 4. Return new hash
    # (Implementation depends on hash library)
    pass

# HMAC length extension doesn't work because HMAC uses double hashing:
# HMAC(k, m) = H((k ⊕ opad) || H((k ⊕ ipad) || m))
```

### Hash Collision Attacks

```python
# MD5 collisions (broken since 2004, Wang et al.)
# SHA1 collisions (SHAttered, 2017 — 2^63 work)
# Both should NEVER be used for security

# Multicollisions via Joux's attack (2004):
# Find 2-block collisions iteratively → 2^k-way collision in k * cost of one collision
# Does not apply to wide-pipe hashes (SHA-512/256) or tree constructions (SHA3)

# Chosen-prefix collision: even more powerful
# MD5: practical (used for Flame malware cert, ~2009)
# SHA1: 2^63.4 operations (Leurent & Peyrin, 2020)
```

### PRNG / Random Number Generator Attacks

```python
# Mersenne Twister (MT19937) — fully predictable after 624 consecutive outputs

class MT19937Cracker:
    """Crack the Mersenne Twister PRNG given 624 consecutive 32-bit outputs."""
    
    def __init__(self):
        self.state = [0] * 624
        self.index = 0
    
    def feed(self, output: int):
        """Feed one observed output to reconstruct internal state."""
        # Untemper the output to recover internal state word
        y = output
        y ^= (y >> 18)
        y ^= (y << 15) & 0xEFC60000
        
        # More tempering reversal...
        y ^= (y << 7) & 0x9D2C5680
        y ^= (y >> 11)
        
        self.state[self.index] = y
        self.index += 1
        return self.index >= 624
    
    def predict(self) -> int:
        """Predict the next random output."""
        if self.index < 624:
            return None  # Not enough data
        
        # Twist and generate
        # ...
        pass

# LCG (Linear Congruential Generator) — breaks with 3-6 outputs
def crack_lcg(observed: list, modulus: int = None):
    """Recover LCG parameters from outputs.
    LCG: X_{n+1} = (a * X_n + c) mod m
    """
    if modulus is None:
        # Recover modulus from consecutive differences
        # m = gcd of (Xₙ₊₂ - Xₙ₊₁)² - (Xₙ₊₁ - Xₙ)(Xₙ₊₃ - Xₙ₊₂) over several windows
        diffs = [observed[i+1] - observed[i] for i in range(len(observed)-1)]
        # m divides gcd of (t_{n+1}² - t_n * t_{n+2})
        # ...
    pass

# Java Random — breaks with 2 consecutive ints
# C rand() — breaks with ~5 outputs
# PHP mt_rand() — breaks with 2 outputs (seeded with PID + time)
```

### Bleichenbacher PKCS#1 v1.5 Padding Oracle

```python
def bleichenbacher_oracle(ct, n, e, oracle_fn, max_queries=1000000):
    """
    Classic Bleichenbacher attack on RSA PKCS#1 v1.5.
    PKCS#1 v1.5 format: 00 || 02 || PS || 00 || D
    (PS = random non-zero padding bytes, minimum 8 bytes)
    oracle_fn(ct) -> bool: True if decryption has valid PKCS#1 padding
    """
    B = 2 ** (n.bit_length() - 16)  # 2^(8*(k-2))
    M = [(2*B, 3*B - 1)]  # intervals where plaintext could be
    
    # Step 1: Blinding (find s₀ such that c * s₀^e mod n is PKCS conforming)
    s = 1
    while True:
        c_new = (ct * pow(s, e, n)) % n
        if oracle_fn(c_new):
            break
        s += 1
    
    # Step 2: Narrow intervals
    for _ in range(max_queries):
        # Step 2a: Find smallest s > previous s
        # Step 2b: If multiple intervals, try each
        # Step 2c: Narrow M based on oracle responses
        # Continue until |M| == 1 and interval length == 1
        pass
```

### Key Recovery from Weak RSA Parameters

```python
# Common weak RSA scenarios
WEAK_RSA_CHECKS = {
    'small_exponent': 'e=3 → if m^3 < n, cube root attack. Also Håstad broadcast.',
    'small_d': 'd < n^0.25 → Wiener attack. d < n^0.292 → Boneh-Durfee.',
    'close_primes': '|p-q| small → Fermat factorization. sqrt(n) then scan up.',
    'common_factor': 'GCD attack across many public keys (batch GCD).',
    'factordb': 'Check if n is already factored in FactorDB.',
    'roca': 'Check if p,q generated by vulnerable Infineon library (CVE-2017-15361).',
    'small_q': 'If q < 2^50, brute force possible.',
    'reused_primes': 'If p from key A = p from key B, GCD reveals both.',
}

# Wiener's Attack (small private exponent)
def wiener_attack(n, e):
    """Recover d when d < n^0.25 using continued fractions."""
    def continued_fraction(num, den):
        cf = []
        while den:
            q = num // den
            cf.append(q)
            num, den = den, num - q * den
        return cf
    
    def convergents(cf):
        """Compute convergents from continued fraction."""
        convs = []
        p_minus_2, q_minus_2 = 0, 1
        p_minus_1, q_minus_1 = 1, 0
        for a in cf:
            p0 = a * p_minus_1 + p_minus_2
            q0 = a * q_minus_1 + q_minus_2
            convs.append((p0, q0))
            p_minus_2, p_minus_1 = p_minus_1, p0
            q_minus_2, q_minus_1 = q_minus_1, q0
        return convs
    
    cf = continued_fraction(e, n)
    for k, d in convergents(cf):
        if k == 0 or d % 2 == 0:
            continue
        phi = (e * d - 1) // k
        # Solve: x² - (n - phi + 1)x + n = 0
        b = n - phi + 1
        discriminant = b*b - 4*n
        if discriminant >= 0:
            sqrt_d = int(discriminant ** 0.5)
            if sqrt_d * sqrt_d == discriminant:
                p = (b + sqrt_d) // 2
                q = (b - sqrt_d) // 2
                if p * q == n:
                    return d, p, q
    return None

# Batch GCD — find common factors across many RSA moduli
def batch_gcd(moduli):
    """Given many RSA moduli, find pairs sharing factors."""
    from math import gcd
    
    # Product tree approach for efficient batch GCD
    # Build product tree, then compute remainders
    # O(n log n) instead of O(n²)
    
    # Simple pairwise check (slow but works for small sets)
    shared = []
    for i in range(len(moduli)):
        for j in range(i+1, len(moduli)):
            g = gcd(moduli[i], moduli[j])
            if g > 1:
                shared.append((i, j, g))
    return shared

# Discrete Log Attacks (over finite fields)
DLP_ATTACKS = {
    'bsgs': 'Baby-step Giant-step — O(sqrt(n)) time/space',
    'pollard_rho': 'Probabilistic, O(sqrt(pi*n/2)) time, O(1) space',
    'pohlig_hellman': 'If n-1 has small factors, attack each subgroup + CRT',
    'index_calculus': 'Subexponential for multiplicative groups of finite fields',
    'function_field_sieve': 'L_p(1/3) for small characteristic fields (Joux 2013)',
    'number_field_sieve': 'Best for prime fields, L_n(1/3, c)',
}

# SageMath quick helpers for CTF crypto
"""
# In SageMath, many attacks are one-liners:
n = 0x...
e = 0x...
c = 0x...

# Factor n (try online if small)
# factordb.com or alpertron.com.ar/ECM.HTM
p, q = factor(n)  # Sage

# Compute private key
phi = (p-1)*(q-1)
d = inverse_mod(e, phi)
m = pow(c, d, n)
print(bytes.fromhex(hex(m)[2:]))

# Discrete log in Sage:
F = GF(p)
g = F(generator)
h = F(target)
x = discrete_log(h, g)
"""
```

### Post-Quantum Cryptography (Overview for CTF)

```python
PQC_RELEVANT = {
    'lattice': 'Kyber (ML-KEM), Dilithium (ML-DSA), Falcon — based on LWE/SIS',
    'code': 'Classic McEliece — based on decoding random linear codes',
    'hash': 'SPHINCS+ — stateless hash-based signatures',
    'isogeny': 'SIKE (broken 2022, Castryck-Decru attack on SIDH)',
    'multivariate': 'Rainbow, GeMSS — solving multivariate quadratic equations',
}

# LWE (Learning With Errors) basics for CTF:
# Given: A (m×n matrix), b = A*s + e (mod q)
# Goal: recover secret s
# Attack: If error e is small, solve via lattice reduction (LLL/BKZ)
# A = [A | b]; Short vector in lattice reveals s

# Side-channel intro (for CTF with leaky oracles):
SIDE_CHANNEL_ATTACKS = {
    'timing': 'Measure response time differences → infer bit patterns (e.g., RSA square-and-multiply)',
    'padding_oracle': 'Server reveals padding validity → decrypt without key (CBC, PKCS#1)',
    'error_oracle': 'Server reveals error details → bit-by-bit decryption',
    'length_oracle': 'Compressed + encrypted length reveals plaintext (CRIME/BREACH)',
    'power_analysis': 'DPA/CPA on hardware implementations — out of scope for typical CTF',
}
```

---

# DEEP CRYPTOGRAPHY ATTACKS
