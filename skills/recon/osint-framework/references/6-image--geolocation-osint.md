# 6. Image & Geolocation OSINT

### Reverse Image Search

```python
IMAGE_SEARCH_ENGINES = {
    'Google Images': 'https://images.google.com — most comprehensive',
    'Yandex Images': 'https://yandex.com/images — best for faces/Eastern Europe',
    'TinEye': 'https://tineye.com — oldest, best for copyright',
    'Bing Images': 'https://www.bing.com/images',
    'Baidu Images': 'https://image.baidu.com — Chinese web',
    'PimEyes': 'https://pimeyes.com — facial recognition (paid)',
}
```

### EXIF / Metadata Extraction

```python
# exiftool — extract all metadata
# exiftool -a -u -g1 image.jpg

EXIF_CHECKLIST = [
    'GPS coordinates (GPSLatitude, GPSLongitude)',
    'Camera make/model',
    'Timestamp (DateTimeOriginal, CreateDate)',
    'Software used (editing traces)',
    'Device serial number',
    'Thumbnail (may contain original uncropped image)',
    'XMP metadata (Lightroom edits, ratings)',
    'ICC profile (color space info)',
]

# Strip metadata (privacy)
# exiftool -all= image.jpg
```

### Satellite & Street View

```python
SATELLITE_TOOLS = {
    'Google Earth Pro': 'Historical imagery timeline (desktop app)',
    'Sentinel Hub': 'https://apps.sentinel-hub.com — ESA free satellite',
    'Zoom Earth': 'https://zoom.earth — live satellite/hurricane tracker',
    'Maxar': 'High-resolution commercial imagery (paid)',
    'Planet': 'Daily satellite imagery (paid)',
    'TerraServer': 'Historical US aerial photos',
    'OpenStreetCam': 'Crowdsourced street-level imagery',
    'Mapillary': 'Crowdsourced street-level photos (by Meta)',
    'Baidu Street View': 'China street view',
    'Yandex Panorama': 'Russia/CIS street view',
}

# Google Earth Pro — historical analysis
# 1. Navigate to location
# 2. Click clock icon → timeline slider
# 3. Compare images at different dates
# 4. Measure distances, areas, elevations

# Geolocation methodology (Bellingcat):
GEOLOCATION_METHOD = """
1. Identify key landmarks in image (buildings, signs, mountains)
2. Note: architectural style, vegetation, road markings, license plates
3. Check shadows for time-of-day + latitude estimation
4. Reverse image search to find original source
5. Cross-reference with satellite imagery for exact match
6. Verify with street view for confirmation
7. Document evidence: screenshots, coordinates, timestamps
"""
```

### Image Forensics & Verification

```python
IMAGE_FORENSICS = {
    'FotoForensics': 'https://fotoforensics.com — ELA (Error Level Analysis)',
    'Forensically': 'https://29a.ch/photo-forensics — clone detection, noise analysis',
    'InVID': 'Browser extension — video verification toolkit',
    'Jeffrey\'s EXIF': 'Web-based metadata viewer',
    'Ghiro': 'Automated image forensics (open source)',
    'Sherloq': 'SQLite-based image forensics GUI',
}

# Check image manipulation:
# 1. ELA (Error Level Analysis): different compression levels → edited regions
# 2. Clone detection: find duplicated pixel regions
# 3. Noise analysis: inconsistent noise patterns → spliced images
# 4. Metadata vs visual cross-check: timestamp vs shadows/weather
# 5. JPEG compression analysis: multiple compressions → edited
```

---
