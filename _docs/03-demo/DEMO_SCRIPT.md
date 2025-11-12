# Demo Script for Pacifico Energy Group

## Pre-Demo Checklist
- [ ] Backend server running on `http://localhost:8000`
- [ ] Frontend server running on `http://localhost:3001`
- [ ] Mapbox token configured in `frontend/.env`
- [ ] OpenRouter API key configured (optional, for AI features)
- [ ] Browser ready with `http://localhost:3001` open

## Demo Flow (15-20 minutes)

### 1. Introduction (2 minutes)
**Say:** "Today I'll demonstrate our AI-powered Site Layout Optimizer, designed specifically for real estate due diligence. This tool helps you quickly analyze properties, optimize asset placement, and generate professional reports."

**Show:** Home page with Pacifico Energy Group branding

### 2. Upload & Analyze (3 minutes)
**Say:** "Let's start by uploading a property file. The system supports KMZ, KML, and GeoJSON formats."

**Do:**
- Click "Create New Layout"
- Drag and drop any file (or click to browse)
- **Point out:** "Notice the automatic terrain analysis - this happens in the background"

**Say:** "The system automatically extracts property boundaries, exclusion zones, and contour data. For this demo, we're using realistic mock data that demonstrates all features."

**Show:** Property boundary and exclusion zones on the map

### 3. Asset Placement (4 minutes)
**Say:** "Now let's configure what we want to place on this property. The system supports various asset types - warehouses, solar panels, wind turbines, battery storage, and more."

**Do:**
- Select "Warehouse" from asset list
- Set count to 3-4
- Select "Solar Panel Array"
- Set count to 2
- Click "Add to Selection"

**Say:** "Each asset type has specific requirements - dimensions, spacing, terrain constraints. The system knows these and will optimize placement accordingly."

### 4. Optimize Layout (3 minutes)
**Say:** "Now the AI optimization engine takes over. It considers terrain, constraints, regulatory data, and best practices to find optimal locations."

**Do:**
- Click "Optimize Layout"
- **Point out:** Loading animation and progress
- **Show:** Assets appearing on the map

**Say:** "The AI has analyzed the terrain, checked all constraints, and placed assets in optimal locations. Notice how it avoids exclusion zones and considers slope, aspect, and elevation."

**Show:** Asset markers on the map, optimization results panel

### 5. Road Network Generation (3 minutes)
**Say:** "Next, we need to connect these assets with a road network. The system uses pathfinding algorithms to find efficient routes while respecting terrain constraints."

**Do:**
- Click on the map to set an entry point (or let it auto-generate)
- **Show:** Roads appearing in red/orange

**Say:** "The road network considers grade limits, avoids exclusion zones, and minimizes cut/fill volumes. This is critical for cost estimation."

**Show:** Road statistics (total length, segment count)

### 6. Export & Reports (3 minutes)
**Say:** "Finally, let's export this layout in multiple formats for your team and stakeholders."

**Do:**
- Scroll to Export section
- Select "PDF Report"
- Click "Export Layout"
- **Show:** PDF opens with professional report

**Say:** "The PDF includes all layout details, statistics, terrain analysis, and asset breakdown - perfect for presentations and documentation."

**Do:**
- Select "KMZ (Google Earth)"
- Click "Export Layout"
- **Say:** "KMZ format works with Google Earth and other GIS tools - great for field teams."

**Do:**
- Select "GeoJSON"
- Click "Export Layout"
- **Say:** "GeoJSON is standard for GIS workflows and can be imported into ArcGIS, QGIS, or other platforms."

### 7. Key Differentiators (2 minutes)
**Highlight:**
1. **AI-Powered Optimization** - Not just placement, but intelligent recommendations
2. **Real-Time Visualization** - See results immediately on interactive map
3. **Regulatory Integration** - FEMA, EPA, USGS data automatically considered
4. **Multiple Export Formats** - PDF, KMZ, GeoJSON for different workflows
5. **Cost-Effective** - Caching and optimization reduce API costs
6. **Professional Output** - Report-ready documentation

### 8. Q&A Preparation
**Be ready to discuss:**
- **Performance:** "Processing typically takes 30-90 seconds depending on property size"
- **Accuracy:** "Terrain analysis uses industry-standard algorithms, and AI recommendations are based on best practices"
- **Scalability:** "Designed for AWS cloud deployment with Lambda and ECS Fargate"
- **Cost:** "Caching and request deduplication minimize API costs"
- **Integration:** "RESTful API allows integration with existing workflows"

## Demo Tips

### Do's ✅
- **Emphasize speed** - Show how fast the workflow is
- **Highlight AI** - Mention AI recommendations and optimization
- **Show professionalism** - Point out polished UI and export quality
- **Demonstrate versatility** - Try different property types if time allows
- **Be confident** - This is a complete, working system

### Don'ts ❌
- Don't apologize for demo data - it's realistic and shows all features
- Don't get stuck on errors - have backup plans
- Don't rush - let features speak for themselves
- Don't over-explain technical details - focus on business value

## Backup Plans

**If something breaks:**
1. Refresh the page
2. Check browser console (F12) for errors
3. Verify backend is running
4. Try a different property type (flat/hilly/constrained)

**If AI is slow:**
- Mention caching reduces repeat calls
- Show that results are cached for 1 hour

**If map doesn't load:**
- Check Mapbox token
- Show that other features work independently

## Closing Statement

**Say:** "This system is ready for deployment and can be customized for your specific needs. The combination of AI intelligence, real-time visualization, and professional reporting gives you a significant advantage in due diligence workflows. We're ready to move forward with implementation."

---

**Total Demo Time:** 15-20 minutes
**Q&A Time:** 10-15 minutes
**Total:** 25-35 minutes

