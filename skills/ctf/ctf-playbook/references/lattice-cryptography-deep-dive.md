# Lattice Cryptography Deep Dive

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
