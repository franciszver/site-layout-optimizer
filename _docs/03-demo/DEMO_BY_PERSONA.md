
# Demo Guide by Persona

This guide provides tailored demo scripts for different stakeholders at Pacifico Energy Group, highlighting features most relevant to each persona.

---

## 🎯 Quick Reference

| Persona | Focus Areas | Demo Time | Key Features |
|---------|------------|-----------|--------------|
| **Site Planner/Engineer** | Accuracy, Efficiency, Technical Details | 15-20 min | Terrain analysis, constraint validation, drag-and-drop |
| **Project Manager** | Speed, Decision-Making, Reports | 10-15 min | Quick workflow, feasibility analysis, export formats |
| **Civil Engineer** | Cut/Fill, Cost Estimation, Precision | 15-20 min | Terrain metrics, cut/fill calculations, road networks |
| **Executive** | ROI, Competitive Advantage, Scalability | 10-12 min | Time savings, throughput, professional output |

---

## 1. Site Planner / Engineer Demo

**Audience:** Technical users who need accurate, efficient layouts  
**Goal:** Show precision, automation, and technical capabilities  
**Time:** 15-20 minutes

### Opening (2 min)
**Say:** *"As a site planner, you know how time-consuming manual layout generation can be. This tool automates the process while maintaining the accuracy and precision you need. Let me show you how it handles complex terrain and constraints."*

### Key Features to Highlight

#### 1. Terrain Analysis (3 min)
**Do:**
- Upload `hilly_demo.kmz` (shows terrain complexity)
- Point to terrain stats: "Min/Max Elevation, Average Slope, Aspect Analysis"
- Show exclusion zones: "The system automatically identifies steep slopes and other constraints"

**Say:** *"Notice the detailed terrain metrics - elevation differentials, slope analysis, aspect calculations. This is the same data you'd get from manual analysis, but generated automatically."*

#### 2. Constraint Validation (3 min)
**Do:**
- Show exclusion zones on map
- Toggle layer visibility: "You can see exactly what constraints are being applied"
- Point out: "Wetlands, flood zones, steep slopes - all automatically detected"

**Say:** *"The system respects all regulatory constraints - FEMA flood zones, EPA wetlands, USGS geological data. No manual checking required."*

#### 3. Asset Placement & Optimization (4 min)
**Do:**
- Select multiple asset types (Warehouse, Solar Panel Array, Wind Turbine)
- Click "Optimize Layout"
- **Drag-and-Drop Demo:** Drag an asset to a new location
- Show real-time validation: "Green = valid, Red = violates constraints"

**Say:** *"The AI optimization engine considers terrain, constraints, spacing requirements, and best practices. But you have full control - drag assets to adjust, and the system validates in real-time."*

#### 4. Road Network Generation (3 min)
**Do:**
- Set entry point on map
- Show road network generation
- Point to road stats: "Total length, segment count, grade analysis"

**Say:** *"The pathfinding algorithm respects grade limits, avoids exclusion zones, and minimizes cut/fill. This is critical for cost estimation."*

#### 5. Export & Integration (3 min)
**Do:**
- Export as GeoJSON: "Standard GIS format for your workflows"
- Export as KMZ: "Works with Google Earth for field verification"
- Show PDF report: "Complete documentation with all metrics"

**Say:** *"All exports are GIS-compatible. You can import directly into ArcGIS, QGIS, or your existing tools. The PDF includes all technical details you need for documentation."*

### Closing Points
- **Accuracy:** "Industry-standard algorithms, same precision as manual analysis"
- **Efficiency:** "What takes hours manually, done in minutes"
- **Control:** "AI suggests, you decide - full drag-and-drop control"
- **Integration:** "Works with your existing GIS tools"

---

## 2. Project Manager Demo

**Audience:** Decision-makers who need fast, reliable data  
**Goal:** Show speed, ease of use, and decision support  
**Time:** 10-15 minutes

### Opening (2 min)
**Say:** *"As a project manager, you need to make go/no-go decisions quickly. This tool gives you professional feasibility analysis in minutes, not days. Let me show you the complete workflow."*

### Key Features to Highlight

#### 1. Fast Workflow (3 min)
**Do:**
- Upload `flat_demo.kmz`
- Show automatic terrain analysis: "Happens in seconds"
- Click through steps: "Upload → Analyze → Optimize → Export"

**Say:** *"The entire process takes 2-3 minutes. Upload a property file, and you get a complete feasibility analysis with layout recommendations."*

#### 2. Quick Feasibility Analysis (3 min)
**Do:**
- Show optimization results panel
- Point to metrics: "Site utilization, asset count, constraint compliance"
- Show map with assets: "Visual representation of feasibility"

**Say:** *"At a glance, you can see: Can we fit what we need? What are the constraints? What's the optimal layout? This is everything you need for a go/no-go decision."*

#### 3. Professional Reports (3 min)
**Do:**
- Export PDF report
- Show sections: "Executive summary, terrain analysis, asset breakdown, statistics"
- Point out: "Ready for stakeholder presentations"

**Say:** *"The PDF report includes everything stakeholders need - no additional documentation required. Professional, comprehensive, and ready to share."*

#### 4. Multiple Property Comparison (2 min)
**Say:** *"You can evaluate multiple properties quickly. Upload, analyze, compare - all in the same session. This lets you evaluate more sites per quarter."*

### Closing Points
- **Speed:** "Minutes, not days - 50% faster than manual process"
- **Reliability:** "Consistent, data-driven analysis - no subjective judgment"
- **Throughput:** "Evaluate 2x more sites per quarter"
- **Decision Support:** "All the data you need for go/no-go decisions"

---

## 3. Civil Engineer Demo

**Audience:** Technical users focused on cost estimation and precision  
**Goal:** Show cut/fill calculations, terrain metrics, and accuracy  
**Time:** 15-20 minutes

### Opening (2 min)
**Say:** *"As a civil engineer, you know that accurate cut/fill estimates are critical for cost forecasting. This tool provides precise terrain analysis and volume calculations automatically. Let me show you the technical details."*

### Key Features to Highlight

#### 1. Detailed Terrain Metrics (4 min)
**Do:**
- Upload `hilly_demo.kmz` (shows terrain variation)
- Show terrain stats panel:
  - "Min Elevation: 1000 ft"
  - "Max Elevation: 1030 ft"
  - "Average Slope: 8.5%"
  - "Aspect Analysis: North-facing slopes identified"

**Say:** *"The system calculates all standard terrain metrics - elevation differentials, slope percentages, aspect analysis. This is the foundation for accurate cost estimation."*

#### 2. Cut/Fill Volume Calculation (4 min)
**Do:**
- After road generation, show cut/fill section
- Point to calculations: "Cut volume, Fill volume, Net balance"
- Explain: "Based on road network and asset placement"

**Say:** *"The system calculates cut/fill volumes based on the road network and asset placement. This is critical for earthwork cost estimation. The calculations use industry-standard methods."*

#### 3. Road Network Engineering (4 min)
**Do:**
- Generate road network
- Show road statistics: "Total length, segment count, grade analysis"
- Point to map: "Roads respect grade limits and terrain constraints"

**Say:** *"The road network generation considers grade limits, avoids steep slopes, and minimizes earthwork. This directly impacts construction costs."*

#### 4. Export for Engineering Tools (3 min)
**Do:**
- Export as GeoJSON: "Import into CAD or engineering software"
- Export as KMZ: "Field verification in Google Earth"
- Show PDF: "Complete engineering documentation"

**Say:** *"All exports are compatible with standard engineering tools. GeoJSON works with CAD software, KMZ for field teams, PDF for documentation."*

### Closing Points
- **Precision:** "Industry-standard algorithms, same accuracy as manual calculations"
- **Efficiency:** "30% reduction in engineering hours"
- **Cost Estimation:** "Accurate cut/fill volumes for earthwork costing"
- **Documentation:** "Complete engineering reports ready for stakeholders"

---

## 4. Executive Demo

**Audience:** Strategic decision-makers focused on ROI and competitive advantage  
**Goal:** Show business value, scalability, and competitive edge  
**Time:** 10-12 minutes

### Opening (2 min)
**Say:** *"This tool gives Pacifico Energy Group a significant competitive advantage in real estate due diligence. It reduces time-to-decision, increases throughput, and improves accuracy - all while reducing costs. Let me show you the business impact."*

### Key Features to Highlight

#### 1. Speed & Efficiency (3 min)
**Do:**
- Quick demo: Upload → Analyze → Optimize → Export
- Show timer/clock: "Complete analysis in under 3 minutes"
- Compare: "Traditional process: 2-3 days. Our system: 3 minutes"

**Say:** *"What traditionally takes 2-3 days of manual work, we do in 3 minutes. This means you can evaluate more properties, make faster decisions, and capture opportunities your competitors miss."*

#### 2. Throughput & Scalability (2 min)
**Say:** *"The system is designed for cloud deployment on AWS. It can handle multiple properties simultaneously, scale automatically, and process hundreds of sites per quarter. This directly increases your evaluation capacity."*

**Show:** *"Multiple properties can be analyzed in parallel. The system scales automatically based on demand."*

#### 3. Cost Efficiency (2 min)
**Say:** *"Caching and optimization reduce API costs by 70%. The system is designed to be cost-effective while maintaining high performance. This means lower operational costs compared to manual processes."*

#### 4. Professional Output (2 min)
**Do:**
- Show PDF report: "Professional, presentation-ready documentation"
- Show map visualization: "Clear, visual communication for stakeholders"

**Say:** *"Every output is professional-grade - ready for client presentations, stakeholder meetings, or regulatory submissions. No additional documentation needed."*

#### 5. Competitive Advantage (1 min)
**Say:** *"This tool gives you three key advantages:*
- *Speed: Evaluate 2x more sites per quarter*
- *Accuracy: Data-driven decisions, not subjective judgment*
- *Cost: 30% reduction in engineering hours*

*In a competitive market, speed and accuracy win deals."*

### Closing Points
- **ROI:** "30% reduction in engineering hours, 50% faster analysis"
- **Competitive Edge:** "Evaluate more sites, make faster decisions"
- **Scalability:** "Cloud-ready, handles growth automatically"
- **Professional Quality:** "Presentation-ready output, no additional work"

---

## 🎬 Demo Tips by Persona

### Site Planner/Engineer
- ✅ Show technical details (terrain metrics, constraint validation)
- ✅ Demonstrate drag-and-drop control
- ✅ Highlight GIS integration
- ❌ Don't oversimplify - they want technical depth

### Project Manager
- ✅ Emphasize speed and ease of use
- ✅ Show decision support features
- ✅ Highlight professional reports
- ❌ Don't get too technical - focus on outcomes

### Civil Engineer
- ✅ Focus on cut/fill and terrain analysis
- ✅ Show precision and accuracy
- ✅ Highlight engineering tool compatibility
- ❌ Don't skip technical details - they need them

### Executive
- ✅ Lead with business value and ROI
- ✅ Show speed and scalability
- ✅ Highlight competitive advantage
- ❌ Don't get bogged down in technical details

---

## 📋 Pre-Demo Checklist (All Personas)

- [ ] Backend running on `http://127.0.0.1:8000`
- [ ] Frontend running on `http://localhost:3001` (or configured port)
- [ ] Mapbox token configured
- [ ] Demo files ready (`flat_demo.kmz`, `hilly_demo.kmz`, `constrained_demo.kmz`)
- [ ] Browser ready with application open
- [ ] Test upload/analyze/optimize workflow before demo
- [ ] Have backup plan if something breaks

---

## 🔄 Adapting the Demo

**If time is short:**
- Skip detailed terrain metrics (except for Civil Engineers)
- Focus on speed and results
- Show one export format instead of all three

**If audience is mixed:**
- Start with Executive-level overview (5 min)
- Then dive into technical details for engineers (10 min)
- End with business value summary (2 min)

**If technical issues occur:**
- Have screenshots/video backup ready
- Focus on explaining capabilities even if demo is limited
- Emphasize that system is production-ready

---

**Remember:** Tailor your language and depth to your audience. Engineers want technical details, executives want business value, project managers want speed and ease of use.

