#!/usr/bin/env python3
"""Lightweight CTF clue router.

Usage:
  python3 ctf_router.py 'challenge text or filename/url'
  python3 ctf_router.py --file notes.txt

It does not solve challenges; it suggests likely categories and first probes.
"""
from __future__ import annotations
import argparse
from pathlib import Path

RULES = {
    'web': ['http://', 'https://', 'cookie', 'jwt', 'login', 'register', 'csrf', 'admin bot', 'upload', 'ssti', 'sql', 'nosql', 'ssrf', 'xss', 'api'],
    'crypto': ['cipher', 'encrypt', 'decrypt', 'rsa', 'ecc', 'ecdsa', 'nonce', 'iv', 'cbc', 'ctr', 'gcm', 'hash', 'mac', 'signature', 'modulus', 'prime', 'xor'],
    'forensics': ['pcap', 'png', 'jpg', 'jpeg', 'wav', 'mp3', 'zip', 'memory', 'dump', 'disk', 'image', 'exif', 'stego', 'metadata', 'volatility'],
    'reverse': ['elf', 'exe', 'apk', 'jar', 'wasm', 'crackme', 'license', 'binary', 'decompile', 'ghidra', 'obfuscated', 'firmware'],
    'pwn': ['nc ', 'overflow', 'rop', 'libc', 'ld.so', 'heap', 'format string', 'canary', 'pie', 'seccomp', 'shellcode', 'ret2libc'],
    'misc_jail': ['jail', 'sandbox', 'pyjail', 'eval', 'escape', 'maze', 'game', 'protocol', 'encoding', 'morse', 'qr', 'barcode'],
    'osint': ['osint', 'username', 'geolocation', 'whois', 'wayback', 'archive', 'photo location'],
    'mobile': ['apk', 'ipa', 'android', 'ios', 'jadx', 'frida', 'mobile'],
    'cloud': ['s3', 'gcs', 'bucket', 'iam', 'metadata service', 'kubernetes', 'terraform', 'ci/cd', 'aws', 'gcp', 'azure'],
    'blockchain': ['solidity', 'vyper', 'contract', 'abi', 'web3', 'ether', 'reentrancy', 'storage slot'],
    'hardware_rf_ics': ['firmware', 'uart', 'spi', 'i2c', 'sdr', 'rf', 'modbus', 'can bus', 'logic analyzer'],
    'ai_ml': ['pickle', 'onnx', 'model', 'classifier', 'prompt injection', 'adversarial'],
}

FIRST_PROBES = {
    'web': ['curl -i target', 'map auth/cookies/routes', 'review source sinks if provided'],
    'crypto': ['extract constants/modes/nonces', 'check repeated blocks/nonces', 'try decode/gcd/iroot/XOR crib'],
    'forensics': ['sha256sum; file; xxd; strings', 'exiftool/binwalk', 'branch by artifact type'],
    'reverse': ['file; strings; imports/sections', 'locate compare/check/crypto routines', 'decompile or model constraints'],
    'pwn': ['file; checksec; run locally', 'reproduce crash', 'pwntools skeleton + cyclic offset'],
    'misc_jail': ['identify medium/filters', 'manual transcript', 'script enumeration/state machine'],
    'osint': ['metadata first', 'exact-string searches', 'archives/DNS/maps as needed'],
    'mobile': ['unzip/list APK/IPA', 'manifest/resources/strings', 'jadx/apktool'],
    'cloud': ['identify provider/service', 'read policy/config exactly', 'test only authorized lab paths'],
    'blockchain': ['read source/ABI/win condition', 'inspect access/storage/reentrancy/randomness', 'script with foundry/ethers'],
    'hardware_rf_ics': ['binwalk/strings firmware', 'inspect capture format', 'protocol/signal decode'],
    'ai_ml': ['inspect model safely', 'never blindly unpickle', 'probe prompt/classifier boundaries'],
}

def route(text: str):
    lower = text.lower()
    scores = []
    for cat, kws in RULES.items():
        hits = [kw for kw in kws if kw in lower]
        if hits:
            scores.append((len(hits), cat, hits))
    return sorted(scores, reverse=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('text', nargs='*')
    ap.add_argument('--file')
    args = ap.parse_args()
    if args.file:
        text = Path(args.file).read_text(errors='ignore')
    else:
        text = ' '.join(args.text)
    if not text.strip():
        ap.error('provide text or --file')
    results = route(text)
    if not results:
        print('No strong route. Start with universal artifact/service inventory.')
        return
    for score, cat, hits in results:
        print(f'[{cat}] score={score} hits={hits}')
        for p in FIRST_PROBES[cat]:
            print(f'  - {p}')

if __name__ == '__main__':
    main()
