# STEGANOGRAPHY

### Image Steganography

```python
# LSB extraction
from PIL import Image

def extract_lsb(image_path: str) -> bytes:
    """Extract LSB from each color channel."""
    img = Image.open(image_path)
    pixels = list(img.getdata())
    
    bits = []
    for pixel in pixels:
        for channel in pixel[:3]:  # R, G, B
            bits.append(str(channel & 1))
    
    # Convert bits to bytes
    data = bytearray()
    for i in range(0, len(bits) - 7, 8):
        byte = int(''.join(bits[i:i+8]), 2)
        data.append(byte)
    
    return bytes(data)

# Common stego tools
STEGO_TOOLS = {
    'steghide': 'steghide extract -sf image.jpg',
    'zsteg': 'zsteg -a image.png',  # PNG/BMP LSB analysis
    'stegsolve': 'Visual analysis with bit plane filters',
    'exiftool': 'exiftool image.jpg',  # metadata
    'binwalk': 'binwalk -e image.jpg',  # embedded files
    'strings': 'strings image.png | grep flag',
    'pngcheck': 'pngcheck -v image.png',  # PNG chunk analysis
}
```

### Audio Steganography

```bash
# Spectrogram analysis
sox audio.wav -n spectrogram -o spectrogram.png

# LSB extraction from WAV
# Python: wave module to read samples, extract LSBs

# DTMF tones (phone keypad tones)
multimon-ng -t wav audio.wav

# SSTV (Slow Scan TV — radio CTF)
# Use QSSTV or mmsstv
```

### Other Stego Techniques

```python
STEGO_CHECKS = [
    'Check file size — can embed data by appending after EOF',
    'Check for multiple files (binwalk, foremost, 7z l)',
    'Check color palette (PNG palette stego)',
    'Check for zero-width characters in text',
    'Check for whitespace steganography (tabs vs spaces)',
    'Check for custom font encoding',
    'Check for Braille/Unicode hidden messages',
    'Check pixel value differences between similar images',
]
```

---
