# Testing Checklist - Site Layout Optimizer

## Pre-Testing Setup ✅

- [ ] Backend server running on `http://localhost:8000`
- [ ] Frontend server running on `http://localhost:3001`
- [ ] Mapbox token configured
- [ ] Browser console open (F12) to monitor logs

---

## Test 1: File Upload - All Property Types

### Test 1.1: Flat Terrain Property
- [ ] Upload file named `flat_demo.kmz` (or any file without "hilly"/"constrained")
- [ ] Verify: "✓ [filename] uploaded" message appears
- [ ] Verify: Property boundary appears on map (blue polygon)
- [ ] Verify: No exclusion zones (flat terrain has none)
- [ ] Verify: Map centers on property
- [ ] Check console: No errors

### Test 1.2: Hilly Terrain Property
- [ ] Upload file named `hilly_demo.kmz` (must contain "hilly" or "hill")
- [ ] Verify: Property boundary appears
- [ ] Verify: Some exclusion zones may appear (steep slopes)
- [ ] Verify: Terrain analysis completes
- [ ] Check console: No errors

### Test 1.3: Constrained Site Property
- [ ] Upload file named `constrained_demo.kmz` (must contain "constrained" or "constraint")
- [ ] Verify: Property boundary appears
- [ ] Verify: Multiple exclusion zones appear (wetlands, flood zones)
- [ ] Verify: Terrain analysis completes
- [ ] Check console: No errors

### Test 1.4: Invalid File Handling
- [ ] Try uploading non-KMZ/KML file (e.g., `.txt`, `.pdf`)
- [ ] Verify: Error message appears
- [ ] Verify: Error is user-friendly
- [ ] Check console: Error logged properly

---

## Test 2: Terrain Analysis

### Test 2.1: Automatic Analysis
- [ ] Upload any property file
- [ ] Verify: Terrain analysis runs automatically
- [ ] Verify: No "Analyze Terrain" button appears (already analyzed)
- [ ] Check console: Analysis completes without errors

### Test 2.2: Analysis Results
- [ ] After upload, check terrain data in console
- [ ] Verify: Elevation stats present
- [ ] Verify: Slope/aspect data available
- [ ] Verify: Bounds are valid

---

## Test 3: Asset Placement

### Test 3.1: Single Asset Type
- [ ] Upload property
- [ ] Select "Warehouse" asset
- [ ] Set count to 2
- [ ] Click "Add to Selection"
- [ ] Verify: Asset appears in selected assets list
- [ ] Click "Optimize Layout"
- [ ] Verify: 2 warehouses placed on map
- [ ] Verify: Assets visible (orange circles)
- [ ] Check console: No errors

### Test 3.2: Multiple Asset Types
- [ ] Upload property
- [ ] Select "Warehouse" (count: 2)
- [ ] Select "Solar Panel Array" (count: 3)
- [ ] Select "Battery Storage" (count: 1)
- [ ] Click "Optimize Layout"
- [ ] Verify: All assets placed (total: 6)
- [ ] Verify: Assets distributed across property
- [ ] Verify: Assets avoid exclusion zones
- [ ] Check console: No errors

### Test 3.3: Edge Cases
- [ ] Try optimizing without selecting assets
- [ ] Verify: Error message "Please select at least one asset type"
- [ ] Try optimizing without uploading property
- [ ] Verify: Error message "Please upload a property file first"

---

## Test 4: Road Generation

### Test 4.1: Auto-Generated Entry Point
- [ ] Complete asset placement
- [ ] Verify: Roads generate automatically
- [ ] Verify: Roads appear on map (red/orange lines)
- [ ] Verify: Roads connect entry to assets
- [ ] Check console: Road generation successful

### Test 4.2: Manual Entry Point
- [ ] Complete asset placement
- [ ] Click on map to set entry point
- [ ] Verify: Entry point marker appears
- [ ] Verify: Roads regenerate from new entry point
- [ ] Verify: Roads visible and connected
- [ ] Check console: No errors

### Test 4.3: Road Statistics
- [ ] After road generation, check road stats
- [ ] Verify: Total length displayed
- [ ] Verify: Road count displayed
- [ ] Verify: Numbers are reasonable

---

## Test 5: Export Functionality

### Test 5.1: PDF Export
- [ ] Complete full workflow (upload → optimize → roads)
- [ ] Scroll to Export section
- [ ] Select "PDF Report"
- [ ] Click "Export Layout"
- [ ] Verify: PDF downloads
- [ ] Open PDF
- [ ] Verify: Title page with branding
- [ ] Verify: Layout information included
- [ ] Verify: Statistics present
- [ ] Verify: Asset breakdown included

### Test 5.2: KMZ Export
- [ ] Select "KMZ (Google Earth)"
- [ ] Click "Export Layout"
- [ ] Verify: KMZ file downloads
- [ ] Open in Google Earth (if available)
- [ ] Verify: Property boundary visible
- [ ] Verify: Assets visible (placemarks)
- [ ] Verify: Roads visible (lines)
- [ ] Verify: Exclusion zones visible (if any)

### Test 5.3: GeoJSON Export
- [ ] Select "GeoJSON"
- [ ] Click "Export Layout"
- [ ] Verify: GeoJSON file downloads
- [ ] Open in text editor
- [ ] Verify: Valid JSON structure
- [ ] Verify: FeatureCollection present
- [ ] Verify: All features included
- [ ] Verify: Metadata present
- [ ] Optional: Open in https://geojson.io
- [ ] Verify: All features display correctly

### Test 5.4: Export Edge Cases
- [ ] Try exporting without completing workflow
- [ ] Verify: Error message appears
- [ ] Try exporting with no assets
- [ ] Verify: Export still works (property only)

---

## Test 6: Error Handling

### Test 6.1: Network Errors
- [ ] Stop backend server
- [ ] Try uploading file
- [ ] Verify: Error message appears
- [ ] Verify: Error is user-friendly
- [ ] Restart backend
- [ ] Verify: System recovers

### Test 6.2: Invalid Data
- [ ] Upload property
- [ ] Try optimizing with invalid boundary (if possible)
- [ ] Verify: Validation error appears
- [ ] Verify: Error message is clear

### Test 6.3: Missing Data
- [ ] Try exporting without layout data
- [ ] Verify: Appropriate error message
- [ ] Verify: System doesn't crash

---

## Test 7: UI/UX Polish

### Test 7.1: Animations
- [ ] Upload file
- [ ] Verify: Sidebar sections animate in
- [ ] Verify: Smooth transitions
- [ ] Verify: No janky animations

### Test 7.2: Loading States
- [ ] Trigger optimize
- [ ] Verify: Loading overlay appears
- [ ] Verify: Spinner animates
- [ ] Verify: Loading text visible
- [ ] Verify: Buttons disabled during loading

### Test 7.3: Button Interactions
- [ ] Hover over "Optimize Layout" button
- [ ] Verify: Hover effect (gradient, lift)
- [ ] Click button
- [ ] Verify: Active state visible
- [ ] Verify: Disabled state when appropriate

### Test 7.4: Responsive Design
- [ ] Resize browser window
- [ ] Verify: Layout adapts
- [ ] Verify: Sidebar scrollable if needed
- [ ] Verify: Map remains functional

---

## Test 8: Complete Workflow

### Test 8.1: Full Happy Path
1. [ ] Upload `flat_demo.kmz`
2. [ ] Wait for terrain analysis
3. [ ] Select "Warehouse" (count: 3)
4. [ ] Select "Solar Panel Array" (count: 2)
5. [ ] Click "Optimize Layout"
6. [ ] Wait for assets to appear
7. [ ] Verify roads auto-generate
8. [ ] Export as PDF
9. [ ] Export as KMZ
10. [ ] Export as GeoJSON
11. [ ] Verify: All steps complete without errors

### Test 8.2: Different Property Types
- [ ] Repeat Test 8.1 with `hilly_demo.kmz`
- [ ] Repeat Test 8.1 with `constrained_demo.kmz`
- [ ] Verify: All work correctly

---

## Test 9: Performance

### Test 9.1: Response Times
- [ ] Upload file
- [ ] Time: Should complete in < 2 seconds
- [ ] Optimize layout
- [ ] Time: Should complete in < 90 seconds
- [ ] Generate roads
- [ ] Time: Should complete in < 30 seconds
- [ ] Export PDF
- [ ] Time: Should complete in < 5 seconds

### Test 9.2: Caching
- [ ] Optimize same layout twice
- [ ] Verify: Second request is faster (cached)
- [ ] Verify: Results are identical

---

## Test 10: Browser Compatibility

### Test 10.1: Chrome/Edge
- [ ] Test complete workflow
- [ ] Verify: All features work

### Test 10.2: Firefox
- [ ] Test complete workflow
- [ ] Verify: All features work

### Test 10.3: Safari (if available)
- [ ] Test complete workflow
- [ ] Verify: All features work

---

## Issues Found

Document any issues discovered during testing:

1. **Issue:** [Description]
   - **Steps to reproduce:** [Steps]
   - **Expected:** [Expected behavior]
   - **Actual:** [Actual behavior]
   - **Severity:** [High/Medium/Low]

---

## Test Results Summary

- **Total Tests:** [Count]
- **Passed:** [Count]
- **Failed:** [Count]
- **Blocked:** [Count]
- **Overall Status:** [✅ Ready / ⚠️ Issues Found / ❌ Not Ready]

---

**Last Updated:** [Date]
**Tested By:** [Name]

