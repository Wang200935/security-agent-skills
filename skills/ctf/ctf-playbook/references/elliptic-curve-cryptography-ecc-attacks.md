# Elliptic Curve Cryptography (ECC) Attacks

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
