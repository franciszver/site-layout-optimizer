# Installing GDAL on Windows

GDAL is required for KMZ/KML file processing. On Windows, it requires special installation.

## Option 1: Use Pre-built Wheels (Recommended)

1. Download GDAL wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal
   - Match your Python version (e.g., `GDAL‑3.8.0‑cp313‑cp313‑win_amd64.whl` for Python 3.13)
   - Download the appropriate wheel file

2. Install the wheel:
   ```bash
   pip install path/to/GDAL‑3.8.0‑cp313‑cp313‑win_amd64.whl
   ```

## Option 2: Install GDAL Binaries First

1. Download GDAL binaries from: https://www.gisinternals.com/release.php
   - Download the appropriate version for your system
   - Install to a path like `C:\OSGeo4W64`

2. Set environment variables:
   ```powershell
   $env:GDAL_DATA = "C:\OSGeo4W64\share\gdal"
   $env:PATH = "C:\OSGeo4W64\bin;$env:PATH"
   ```

3. Install Python GDAL:
   ```bash
   pip install gdal
   ```

## Option 3: Use Conda (Easiest)

If you have Anaconda/Miniconda:
```bash
conda install -c conda-forge gdal
```

## Temporary Workaround

For development, you can modify the code to handle missing GDAL gracefully. The KML parser will be disabled, but other features will work.

