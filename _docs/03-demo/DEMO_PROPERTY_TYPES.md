# Demo Property Types Guide

## How It Works

The system **automatically generates** demo property data based on the **filename** you upload. You don't need special files - just name your file with keywords!

## Property Types

### 1. Flat Terrain (Default)
**How to trigger:** Upload any file that doesn't contain "hilly" or "constrained" in the name

**Example filenames:**
- `property.kmz`
- `flat_site.kmz`
- `demo.kmz`
- `test.kml`
- `site_layout.geojson`

**Characteristics:**
- ~150 acres
- Minimal elevation variation (1000-1002 ft)
- No exclusion zones
- Best for: Simple layouts, warehouses, solar farms

---

### 2. Hilly Terrain
**How to trigger:** Include "hilly" or "hill" in the filename

**Example filenames:**
- `hilly_property.kmz`
- `hill_site.kmz`
- `hilly_terrain.kml`
- `mountainous_area.kmz` (won't work - needs "hilly" or "hill")

**Characteristics:**
- ~250 acres
- Significant elevation changes (1000-1030 ft)
- Some steep slope exclusion zones
- Best for: Challenging terrain, demonstrating pathfinding

---

### 3. Constrained Site
**How to trigger:** Include "constrained" or "constraint" in the filename

**Example filenames:**
- `constrained_property.kmz`
- `constraint_site.kmz`
- `constrained_area.kml`
- `site_with_constraints.kmz` (won't work - needs "constrained" or "constraint")

**Characteristics:**
- ~350 acres
- Multiple exclusion zones (wetlands, flood zones)
- Moderate terrain variation (1000-1020 ft)
- Best for: Complex scenarios, regulatory compliance

---

## Quick Test

1. **Create empty files** (or use any existing files):
   ```powershell
   # In your project root or any folder
   echo "" > flat_property.kmz
   echo "" > hilly_site.kmz
   echo "" > constrained_property.kmz
   ```

2. **Upload them** in the app:
   - Upload `flat_property.kmz` → See flat terrain
   - Upload `hilly_site.kmz` → See hilly terrain
   - Upload `constrained_property.kmz` → See constrained site

3. **Notice the differences:**
   - **Flat:** Simple boundary, no exclusion zones
   - **Hilly:** More elevation variation, some exclusion zones
   - **Constrained:** Multiple exclusion zones (wetlands, flood zones)

---

## Where the Code Lives

The property generation logic is in:
- **File:** `backend/src/handlers/upload_mock.py`
- **Function:** `generate_demo_property(property_type)`
- **Detection:** Lines 212-218 (filename parsing)

---

## Tips

- **Any file works** - The content doesn't matter, only the filename
- **Case insensitive** - "HILLY" or "hilly" both work
- **Partial match** - "hilly_site" contains "hilly", so it works
- **Default is flat** - If no keywords found, defaults to flat terrain

---

## For Your Demo

**Recommended approach:**
1. Create three empty files with descriptive names:
   - `flat_demo.kmz`
   - `hilly_demo.kmz`
   - `constrained_demo.kmz`

2. Upload them one by one to show different scenarios

3. Point out the differences:
   - Terrain complexity
   - Exclusion zones
   - How the AI handles different constraints

This demonstrates the system's versatility! 🚀

