# Integer Overflow & Type Confusion

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
