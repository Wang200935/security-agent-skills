# Historical Ciphers & Specialized Attacks

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
