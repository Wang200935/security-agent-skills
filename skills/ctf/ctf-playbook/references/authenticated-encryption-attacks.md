# Authenticated Encryption Attacks

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
