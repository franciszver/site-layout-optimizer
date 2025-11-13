"""
Script to create minimal valid KMZ demo files for testing.
KMZ files are ZIP archives containing KML files.
"""
import zipfile
import os
from pathlib import Path

# Base location (Kansas, USA) - same as in upload_mock.py
BASE_LNG = -98.5795
BASE_LAT = 39.8283

def create_kml_content(property_type: str) -> str:
    """Create KML content for different property types"""
    
    if property_type == "flat":
        # Flat terrain - simple square
        size = 0.01
        coords = [
            [BASE_LNG - size/2, BASE_LAT - size/2],
            [BASE_LNG + size/2, BASE_LAT - size/2],
            [BASE_LNG + size/2, BASE_LAT + size/2],
            [BASE_LNG - size/2, BASE_LAT + size/2],
            [BASE_LNG - size/2, BASE_LAT - size/2]
        ]
    elif property_type == "hilly":
        # Hilly terrain - slightly larger with more variation
        size = 0.015
        coords = [
            [BASE_LNG - size/2, BASE_LAT - size/2],
            [BASE_LNG + size/2, BASE_LAT - size/2],
            [BASE_LNG + size/2, BASE_LAT + size/2],
            [BASE_LNG - size/2, BASE_LAT + size/2],
            [BASE_LNG - size/2, BASE_LAT - size/2]
        ]
    else:  # constrained
        # Constrained site - largest with exclusion zones
        size = 0.018
        coords = [
            [BASE_LNG - size/2, BASE_LAT - size/2],
            [BASE_LNG + size/2, BASE_LAT - size/2],
            [BASE_LNG + size/2, BASE_LAT + size/2],
            [BASE_LNG - size/2, BASE_LAT + size/2],
            [BASE_LNG - size/2, BASE_LAT - size/2]
        ]
    
    # Format coordinates as "lng,lat" pairs
    coord_string = " ".join([f"{c[0]},{c[1]}" for c in coords])
    
    kml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>{property_type.title()} Demo Property</name>
    <Placemark>
      <name>Property Boundary</name>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>{coord_string}</coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>"""
    return kml

def create_kmz_file(output_path: Path, property_type: str):
    """Create a KMZ file (ZIP archive with KML)"""
    kml_content = create_kml_content(property_type)
    
    # Create KMZ (ZIP file)
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as kmz:
        # Add KML file to the ZIP
        kmz.writestr('doc.kml', kml_content)
    
    print(f"Created {output_path} ({output_path.stat().st_size} bytes)")

def main():
    """Create all demo KMZ files"""
    # Get the project root (parent of backend)
    project_root = Path(__file__).parent.parent.parent
    demo_dir = project_root / "tests" / "sample_data" / "sample_parcels"
    
    # Ensure directory exists
    demo_dir.mkdir(parents=True, exist_ok=True)
    
    # Create demo files
    demo_files = [
        ("flat_demo.kmz", "flat"),
        ("hilly_demo.kmz", "hilly"),
        ("constrained_demo.kmz", "constrained"),
        ("demo_flat_property.kmz", "flat"),  # Alternative name
    ]
    
    print("Creating demo KMZ files...")
    for filename, property_type in demo_files:
        output_path = demo_dir / filename
        create_kmz_file(output_path, property_type)
    
    print("\nDone! Demo files created in:", demo_dir)

if __name__ == "__main__":
    main()

