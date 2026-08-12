# Advanced RSA Attacks

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
