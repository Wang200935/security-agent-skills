# Blockchain & Cryptocurrency Crypto

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
