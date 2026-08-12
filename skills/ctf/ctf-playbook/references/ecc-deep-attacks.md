# ECC Deep Attacks

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
