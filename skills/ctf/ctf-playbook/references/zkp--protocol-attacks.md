# ZKP & Protocol Attacks

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
