# One-Shot AI Agent Prompt: Site Layout Optimization System

```
# PROJECT: Site Layout Optimization System - Geospatial AI-Powered Real Estate Due Diligence

## GIT REPOSITORY

**Repository Name:** `site-layout-optimizer`

**Repository Description:** AI-powered geospatial site layout optimizer for real estate due diligence. Processes KMZ/KML and topographic data to generate optimized layouts with asset placement, road networks, and cut/fill estimation. Uses OpenAI for constraint analysis. Built with Python, React, and AWS.

## PHASE 1: INITIAL CREDENTIALS COLLECTION (HUMAN INTERACTION REQUIRED)

Before beginning implementation, collect the following from the human:

1. **AWS Credentials:**
   - AWS Access Key ID
   - AWS Secret Access Key
   - Preferred AWS Region (default: us-east-1)
   - S3 bucket name for geospatial data storage

2. **OpenAI/OpenRouter:**
   - OpenAI API Key (or OpenRouter API Key)
   - Preferred model (default: gpt-4o or gpt-4-turbo)

3. **Project Configuration:**
   - Project name/identifier
   - Domain name (if custom, otherwise use AWS-generated)
   - Maximum file upload size for KMZ/KML files
   - Default buffer distances and constraints

4. **Optional External APIs:**
   - USGS API access for topographic data (if needed)
   - FEMA flood zone API access (if available)
   - Any other regulatory data API credentials

Once credentials are collected, proceed with FULL AUTONOMOUS IMPLEMENTATION.

## PHASE 2: AUTONOMOUS IMPLEMENTATION

### Project Overview
Build a web application that automates site layout generation for early real estate due diligence:
- Import and validate KMZ/KML files and topographic contour data (P0)
- Compute terrain metrics (slope, aspect, elevation differentials) (P0)
- Auto-place infrastructure assets within property boundaries, respecting exclusion zones and buffers (P0)
- Generate road networks connecting property entry to all major assets (P0)
- Estimate cut/fill volumes and produce layout maps and reports (PDF, KMZ, GeoJSON) (P0)
- Integrate regulatory and environmental constraints dynamically (P1)
- Enable user-defined asset placement adjustments with real-time visualization (P1)
- Use AI to optimize asset placement considering all constraints
- Support alternative energy asset placement (solar panels, wind turbines) (P2)
- Integration capabilities with third-party GIS systems (P2)

**Design Principles (from PRD):**
- Modular, config-driven architecture for flexibility
- Quick layout generation for preliminary analysis (target: <2 minutes for typical parcels)
- Real-time feedback during user interactions
- Support for multiple sites and large datasets concurrently
- Focus on early due diligence (preliminary accuracy acceptable: ±10% for volumes, ±5ft for elevations)
- Optimize for site utilization efficiency (20% improvement target)

### Technical Stack
- **Frontend:** React (TypeScript) with Mapbox GL JS or Leaflet for geospatial visualization
- **Backend:** Python (FastAPI) with geospatial libraries
- **Geospatial Libraries:** GDAL/OGR, Shapely, GeoPandas, Rasterio, PostGIS (via RDS)
- **Storage:** AWS S3 (geospatial files), RDS PostgreSQL with PostGIS extension
- **Compute:** AWS Lambda for API endpoints, ECS Fargate for heavy geospatial processing
- **AI:** OpenAI API via OpenRouter (for constraint analysis and optimization)
- **Deployment:** AWS SAM or Serverless Framework, Docker for geospatial processing
- **Configuration:** YAML/JSON config files for asset types, constraints, and rules (modular design)
- **Caching:** Redis/ElastiCache for session data and frequently accessed calculations

### Implementation Steps

#### Step 1: Project Structure
Create the following structure:
```
site-layout-optimizer/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── MapViewer.tsx
│   │   │   ├── FileUpload.tsx
│   │   │   ├── LayoutCanvas.tsx
│   │   │   ├── AssetPlacement.tsx
│   │   │   ├── RoadNetwork.tsx
│   │   │   ├── ReportExport.tsx
│   │   │   └── LayoutComparison.tsx
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── LayoutEditor.tsx
│   │   │   └── LayoutLibrary.tsx
│   │   └── services/
│   │       └── api.ts
│   └── package.json
├── backend/
│   ├── src/
│   │   ├── handlers/
│   │   │   ├── upload.py
│   │   │   ├── analyze.py
│   │   │   ├── optimize.py
│   │   │   ├── generate_roads.py
│   │   │   ├── calculate_cutfill.py
│   │   │   ├── export.py
│   │   │   └── constraints.py
│   │   ├── services/
│   │   │   ├── geospatial_processor.py
│   │   │   ├── terrain_analyzer.py
│   │   │   ├── asset_placer.py
│   │   │   ├── road_generator.py
│   │   │   ├── cutfill_calculator.py
│   │   │   ├── ai_optimizer.py
│   │   │   └── regulatory_fetcher.py
│   │   ├── models/
│   │   │   └── site_models.py
│   │   ├── config/
│   │   │   ├── asset_templates.yaml
│   │   │   ├── constraints.yaml
│   │   │   └── optimization_rules.yaml
│   │   └── utils/
│   │       ├── kml_parser.py
│   │       ├── validators.py
│   │       └── config_loader.py
│   └── requirements.txt
├── infrastructure/
│   ├── template.yaml
│   ├── docker/
│   │   └── Dockerfile.geospatial
│   └── deploy.sh
├── tests/
│   ├── sample_data/
│   │   └── sample_parcels/
│   └── test_geospatial.py
└── README.md
```

#### Step 2: Backend Services

**Geospatial Processor (geospatial_processor.py)**
- Parse and validate KMZ/KML files using GDAL/OGR
- Extract property boundaries, exclusion zones, and constraints
- Validate coordinate systems and auto-reproject to common CRS (WGS84 or UTM)
- Validate geometry quality (check for self-intersections, invalid polygons)
- Store processed geometries in PostGIS database with spatial indexing
- Handle multiple file formats (KMZ, KML, Shapefile, GeoJSON, GeoPackage)
- Extract metadata from files (property name, description, attributes)
- Support multi-layer files (extract all relevant layers)
- Validate file size and complexity (prevent processing of overly complex geometries)

**Terrain Analyzer (terrain_analyzer.py)**
- Process topographic contour data (from KMZ/KML or fetch from USGS if not provided)
- Auto-fetch topographic data from USGS National Map API if contours not in uploaded file
- Generate Digital Elevation Model (DEM) from contours using interpolation
- Calculate terrain metrics:
  - Slope (degrees/percent)
  - Aspect (direction)
  - Elevation differentials
  - Hillshade for visualization
- Identify optimal areas based on terrain characteristics
- Use Rasterio for raster processing
- Cache DEM generation for performance (preliminary accuracy: ±5ft elevation acceptable)

**Asset Placer (asset_placer.py)**
- Define flexible asset types and requirements (config-driven):
  - Generic infrastructure assets (buildings, facilities, structures)
  - Predefined asset templates for common types (configurable library)
  - Custom asset definitions with configurable footprint dimensions (length, width, height)
  - Asset-specific requirements (access needs, utility connections, spacing)
  - Alternative energy assets: solar arrays, wind turbines (P2)
  - Asset library stored in configuration files for easy modification
- Implement comprehensive constraint checking:
  - Property boundaries (hard constraint)
  - Exclusion zones (environmental, regulatory, user-defined)
  - Buffer distances (configurable: default 50ft from boundaries, 100ft from exclusion zones)
  - Minimum spacing between assets (configurable)
  - Terrain constraints (max slope, aspect preferences)
  - Regulatory constraints (zoning, setbacks, easements)
- Use Shapely for geometric operations
- Generate candidate placement locations using grid-based or optimization algorithms
- Rank locations based on multi-criteria scoring:
  - Terrain suitability (slope, aspect, elevation)
  - Distance to property entry
  - Constraint compliance
  - Access requirements
- Support user-defined placement overrides (P1)
- Enable real-time constraint validation during manual adjustments

**AI Optimizer (ai_optimizer.py)**
- Use OpenAI via OpenRouter to analyze constraints and requirements
- Dynamically integrate regulatory and environmental constraints (P1):
  - Fetch regulatory data from external APIs (FEMA flood zones, wetlands, zoning)
  - Analyze environmental constraints (slope stability, drainage, vegetation)
  - Consider local building codes and setbacks
- Generate optimization recommendations:
  - Best asset placement locations with reasoning
  - Constraint violations to avoid
  - Trade-offs between different layout options
  - Cost-benefit analysis (cut/fill minimization, road length optimization)
- Analyze multiple layout scenarios
- Suggest layout improvements based on civil engineering best practices
- Provide explanations for recommendations
- Support iterative optimization with user feedback

**Road Generator (road_generator.py)**
- Auto-detect or accept user-specified property entry point
- Generate road network connecting:
  - Property entry point (primary connection)
  - All major assets (secondary connections)
  - Create hierarchical network (main access roads, secondary roads)
- Constraints (best practices):
  - Maximum grade: 8% (standard for access roads, configurable)
  - Minimum width: 20ft for access roads, 12ft for secondary (configurable)
  - Minimum turning radius: 25ft (configurable)
  - Avoid steep slopes (>15% grade)
  - Avoid exclusion zones with buffer
  - Maintain safe distances from property boundaries
- Use pathfinding algorithms (A* with terrain cost weighting)
- Consider terrain difficulty when routing (prefer flatter routes)
- Generate road centerlines and right-of-way polygons
- Support user editing of road paths with real-time validation (P1)
- Optimize for minimum total road length while maintaining connectivity

**Cut/Fill Calculator (cutfill_calculator.py)**
- Calculate earthwork volumes (preliminary accuracy: ±10% acceptable for due diligence):
  - Cut volume (material to remove)
  - Fill volume (material to add)
  - Net volume (cut - fill)
- Use DEM and proposed grade elevations
- Implement grid method (faster, suitable for preliminary analysis) or TIN (more accurate, optional)
- Provide volume reports by area with summary statistics
- Export cut/fill maps with visualization
- Optimize for speed over precision (preliminary due diligence focus)

#### Step 3: API Endpoints

**POST /api/upload**
- Accept KMZ/KML file uploads
- Validate file format and structure
- Process and store in S3
- Return file ID and metadata

**POST /api/analyze**
- Accept file ID and analysis parameters
- Process terrain data
- Calculate terrain metrics
- Return analysis results

**POST /api/optimize**
- Accept property data, asset requirements, constraints
- Fetch regulatory/environmental constraints dynamically (P1)
- Generate optimized layout (prioritize: site utilization, minimize cut/fill, minimize road length)
- Use AI for constraint analysis and optimization
- Return layout with asset placements and optimization scores
- Support multiple optimization scenarios for comparison

**POST /api/compare-layouts**
- Accept multiple layout IDs
- Compare layouts side-by-side
- Return comparison metrics (utilization, cut/fill, road length, constraint compliance)

**PUT /api/layouts/{id}/assets/{assetId}**
- Update asset placement (user-defined adjustments) (P1)
- Real-time constraint validation
- Return updated layout with validation results

**GET /api/layouts/{id}**
- Retrieve saved layout
- Return full layout data with all components

**POST /api/layouts**
- Save layout for future reference
- Store layout configuration and metadata

**GET /api/constraints**
- Fetch regulatory constraints for property location
- Integrate environmental data (flood zones, wetlands, zoning) (P1)
- Priority: Flood zones (FEMA), wetlands (EPA), zoning (local APIs if available)
- Return constraint data for visualization

**POST /api/generate-roads**
- Accept layout with asset locations
- Generate road network
- Return road network geometry

**POST /api/calculate-cutfill**
- Accept layout and proposed grades
- Calculate cut/fill volumes
- Return volume reports and maps

**POST /api/export**
- Accept layout ID and export format (PDF, KMZ, GeoJSON, Shapefile)
- Generate export files with comprehensive metadata
- Include summary statistics in exports
- Return download URL (presigned S3 URL, expires in 1 hour)

**GET /api/layouts**
- List all saved layouts for user
- Support filtering and search
- Return layout metadata and previews

**DELETE /api/layouts/{id}**
- Delete saved layout
- Soft delete with retention period (30 days)

**POST /api/batch-process**
- Accept multiple property files
- Process layouts in batch
- Return job ID for tracking
- Support concurrent processing
- Store job status in database

**GET /api/batch-jobs/{jobId}**
- Get batch job status
- Return progress percentage and estimated completion time
- Return results when complete

**GET /api/layouts/{id}/versions**
- Get version history for layout
- Return list of versions with metadata

**POST /api/layouts/{id}/share**
- Share layout with other users
- Set sharing permissions (view, edit)
- Generate shareable link (optional)

**GET /api/audit-logs**
- Get audit logs for layouts (who created/modified, when)
- Support filtering by user, date, action

#### Step 4: Frontend Components

**MapViewer Component:**
- Interactive map using Mapbox GL JS or Leaflet
- Display property boundaries
- Show terrain (hillshade, contours)
- Display assets and road network
- Toggle layers (terrain, assets, roads, constraints)

**FileUpload Component:**
- Drag-and-drop file upload
- Support KMZ, KML, GeoJSON
- File validation and preview
- Progress indicator

**LayoutCanvas Component:**
- Visual layout editor with real-time updates (P1)
- Primary workflow: Automated generation with interactive review and adjustment
- Drag-and-drop asset placement with user-defined adjustments (P1)
- Real-time constraint checking and validation
- Visual feedback for violations (color-coded warnings)
- Interactive property entry point selection
- Real-time terrain visualization updates
- Undo/redo functionality for layout changes
- Layer toggling (terrain, assets, roads, constraints, regulatory data)
- Side-by-side layout comparison view (multiple scenarios)
- Save/load layout templates and scenarios
- Quick preview of optimization metrics

**AssetPlacement Component:**
- Define asset types and requirements (config-driven):
  - Generic infrastructure assets
  - Predefined asset library (common building types, facility sizes)
  - Custom asset definitions with dimensions
  - Alternative energy assets (solar panels, wind turbines) (P2)
- Set constraints and buffers (configurable, stored in config files)
- Configure placement rules and preferences
- Preview placement options with suitability scores
- Enable manual placement with real-time validation (P1)
- Show constraint violations in real-time (P1)
- Asset template management (create, edit, save templates)

**RoadNetwork Component:**
- Configure road requirements
- Set entry point (auto-detect or manual selection)
- Generate and preview road network
- Edit road paths with real-time validation
- Show road metrics (length, grade, cost estimate)

**LayoutLibrary Component:**
- View saved layouts (user's and shared)
- Search and filter layouts
- Open saved layouts for editing
- Share layouts with other users
- View layout version history
- Compare layout versions
- Batch job status monitoring

**ReportExport Component:**
- Select export format (PDF, KMZ, GeoJSON, Shapefile)
- Configure report options:
  - Include/exclude layers
  - Report detail level
  - Include statistics and metrics
  - Custom branding/title
- Generate and download reports
- Show export progress
- Preview report before download

**LayoutComparison Component:**
- Side-by-side view of multiple layouts
- Compare metrics (utilization, cut/fill, road length)
- Highlight differences between layouts
- Export comparison report

#### Step 5: AWS Infrastructure

**S3 Buckets:**
- geospatial-data/ - Uploaded KMZ/KML files
- processed-data/ - Processed geospatial data
- exports/ - Generated reports and exports
- terrain-cache/ - Cached terrain analysis

**RDS PostgreSQL with PostGIS:**
- Database for geospatial data storage
- PostGIS extension for spatial operations
- Tables:
  - properties - Property boundaries
  - assets - Asset placements (with versioning for undo/redo)
  - roads - Road networks
  - terrain - Terrain data (cached for performance)
  - constraints - Exclusion zones and constraints
  - regulatory_data - Fetched regulatory constraints (P1)
  - layout_versions - Version history for layouts
  - user_adjustments - User-defined placement overrides (P1)
  - users - User accounts and roles
  - layout_shares - Shared layout access (for collaboration)
  - audit_logs - Activity logging (who, what, when)
  - batch_jobs - Batch processing job tracking

**Lambda Functions:**
- upload-handler - File upload processing
- analyze-handler - Terrain analysis
- optimize-handler - Layout optimization
- road-handler - Road network generation
- cutfill-handler - Cut/fill calculations
- export-handler - Report generation

**ECS/Fargate (for heavy processing):**
- Docker container with GDAL and geospatial libraries
- Handle large file processing
- Terrain analysis tasks
- Batch processing jobs

**ElastiCache/Redis:**
- Session data caching
- Frequently accessed calculations
- Job status tracking for batch processing
- Real-time update subscriptions (P1)

**API Gateway:**
- REST API with CORS
- File upload support
- Authentication (API keys or Cognito)

#### Step 6: Geospatial Processing Details

**KMZ/KML Processing:**
- Use GDAL/OGR Python bindings
- Extract:
  - Property boundaries (Polygon)
  - Exclusion zones (Polygon)
  - Contour lines (LineString)
  - Asset locations (Point/Polygon)
- Validate coordinate reference systems
- Reproject to common CRS (WGS84 or UTM)

**Terrain Analysis:**
- Convert contour lines to DEM using interpolation
- Calculate slope using gradient
- Calculate aspect using direction of steepest slope
- Generate hillshade for visualization
- Identify flat areas suitable for development

**Asset Placement Algorithm:**
1. Generate grid of candidate locations
2. Filter by constraints (boundaries, exclusion zones, buffers)
3. Calculate terrain suitability score (slope, aspect, elevation)
4. Rank locations
5. Place assets using greedy algorithm or optimization
6. Use AI to refine placement considering all constraints

**Road Network Generation:**
1. Create graph of possible road segments
2. Weight edges by:
   - Distance
   - Terrain difficulty (slope)
   - Constraint violations
3. Use pathfinding to connect entry to assets
4. Optimize for minimum total cost
5. Generate road geometry with proper width

**Cut/Fill Calculation:**
1. Create grid over site area (configurable resolution: default 10ft x 10ft)
2. Calculate existing elevation (from DEM)
3. Calculate proposed elevation (from layout and proposed grades)
4. Account for road grading and asset pad elevations
5. Calculate volume for each grid cell using average end area method
6. Apply compaction factors if specified (default: 1.0 for preliminary estimates)
7. Sum volumes for total cut/fill with area breakdowns
8. Generate visualization maps (cut areas, fill areas, balanced zones)
9. Provide volume reports by area and total summary

#### Step 7: AI Integration and Regulatory Data

**Regulatory Constraint Integration (P1):**
- Dynamically fetch regulatory data from public APIs (priority order):
  1. FEMA Flood Map Service Center API (flood zones - critical for due diligence)
  2. EPA EnviroAtlas/Wetlands Mapper (wetlands, environmental constraints)
  3. USGS National Map API (topographic data if not in upload)
  4. State/local zoning APIs (if available, with fallback to manual input)
- Cache regulatory data in database for performance (daily refresh)
- Update constraints when property location changes
- Visualize regulatory constraints on map with clear labeling
- Validate layouts against building codes (flag violations for review, not hard blocks)
- Support manual constraint entry for local regulations not available via API

**AI Constraint Analysis:**
- Use OpenAI via OpenRouter to analyze:
  - Regulatory constraints (fetched dynamically)
  - Environmental considerations
  - Civil engineering best practices for site layout
  - Optimization opportunities
  - Cost-benefit analysis of layout options

**Prompt Template:**
```
Analyze the following site layout for real estate due diligence:

Property: [property description with location]
Property Boundaries: [boundary coordinates]
Assets to place: [asset list with requirements and dimensions]
Existing Constraints: [exclusion zones, buffers from KMZ/KML]
Regulatory Constraints: [flood zones, wetlands, zoning from APIs]
Terrain Analysis: [slope ranges, aspect, elevation differentials]
Proposed Layout: [current asset placements and road network]

Provide comprehensive recommendations:
1. Optimal asset placement locations with reasoning
2. Constraint violations to avoid (regulatory, environmental, terrain)
3. Road network optimization (minimize length, avoid steep grades)
4. Cut/fill optimization strategies (minimize earthwork)
5. Regulatory compliance check (zoning, setbacks, environmental)
6. Alternative layout options with trade-offs
7. Risk assessment for proposed layout
```

**Optimization Suggestions:**
- Use AI to suggest layout improvements iteratively
- Analyze trade-offs between different layout options
- Provide detailed explanations for recommendations
- Consider multiple optimization objectives (cost, efficiency, compliance)
- Generate alternative scenarios for comparison

#### Step 8: Export Formats and Third-Party Integration

**PDF Export (P0):**
- Professional layout map with assets and roads
- Terrain visualization (hillshade, contours)
- Cut/fill maps with volume annotations
- Summary statistics (areas, volumes, metrics, utilization percentage)
- Constraint visualization with legend
- Property information header (name, location, date)
- Layout metadata and assumptions
- Use reportlab or WeasyPrint for high-quality output
- Multi-page support for large properties
- Include disclaimers for preliminary analysis

**KMZ Export (P0):**
- Property boundaries with metadata
- Asset placements with attributes
- Road network with centerlines and right-of-way
- Exclusion zones and constraints
- Terrain layers (contours, DEM)
- Regulatory data overlays (P1)
- Use GDAL/OGR to generate with proper styling

**GeoJSON Export (P0):**
- All geometries in GeoJSON format
- Include comprehensive metadata
- Compatible with GIS software (QGIS, ArcGIS)
- Support for third-party GIS system integration (P2)

**Third-Party GIS Integration (P2):**
- Export in standard formats (Shapefile, GeoPackage, GeoJSON)
- Priority integration targets: QGIS (open-source), ArcGIS (commercial)
- API endpoints for integration with external GIS systems
- Web Map Service (WMS) support for map visualization
- REST API for programmatic access
- Support importing existing layouts from common GIS formats
- OGC-compliant services for interoperability

#### Step 9: Testing

**Unit Tests:**
1. Test KMZ/KML file parsing with various formats and coordinate systems
2. Test geometry validation and reprojection
3. Test terrain analysis algorithms (slope, aspect calculations)
4. Test asset placement algorithms with various constraints
5. Test road network pathfinding algorithms
6. Test cut/fill calculation methods
7. Test config file loading and validation

**Integration Tests:**
1. Test terrain analysis accuracy (validate against known DEMs)
2. Test asset placement with different constraints and scenarios
3. Test road network generation with various terrain conditions
4. Test cut/fill calculations (validate against manual calculations)
5. Test regulatory constraint integration (FEMA, USGS APIs)
6. Test export formats (PDF, KMZ, GeoJSON, Shapefile)
7. Test third-party GIS integration (P2)
8. Test batch processing of multiple properties

**User Experience Tests:**
1. Test user-defined asset placement adjustments (P1)
2. Test real-time visualization updates (P1)
3. Test layout comparison functionality
4. Test save/load of layouts and templates
5. Test undo/redo functionality

**Performance Tests:**
1. Test with sample real estate parcels of various sizes (10-1000 acres)
2. Test performance with large datasets (complex geometries, many assets)
3. Test concurrent processing of multiple sites
4. Test processing time targets (<2 minutes for typical parcels)
5. Test memory usage with large DEMs

**End-to-End Tests:**
1. Complete workflow: Upload → Analyze → Optimize → Generate Roads → Calculate Cut/Fill → Export
2. Multiple layout scenario generation and comparison
3. Error handling and edge cases:
   - Invalid file formats
   - Missing coordinate systems
   - Invalid geometries
   - API failures
   - Large file handling
   - Network timeouts
4. Data validation and sanitization
5. Security testing (file upload validation, injection prevention)

#### Step 10: Deployment

1. Set up RDS PostgreSQL with PostGIS
2. Deploy Lambda functions
3. Deploy ECS/Fargate for heavy processing
4. Deploy frontend to S3/CloudFront
5. Configure API Gateway
6. Set up environment variables
7. Test deployed application
8. Generate deployment summary

### Deliverables

1. **Working Application:**
   - Frontend URL (S3/CloudFront)
   - API endpoints
   - All features functional

2. **Documentation:**
   - User guide
   - API documentation
   - Geospatial data format requirements
   - Deployment guide
   - Architecture diagram

3. **Code Repository:**
   - Complete source code
   - Infrastructure as code
   - Docker configurations
   - README with setup instructions

### Success Criteria

**P0 Requirements (Must-have):**
- ✅ Accepts and processes KMZ/KML files with validation
- ✅ Computes terrain metrics (slope, aspect, elevation differentials) accurately
- ✅ Auto-places assets within property boundaries respecting exclusion zones and buffers
- ✅ Generates road networks connecting property entry to all major assets
- ✅ Estimates cut/fill volumes and produces layout maps
- ✅ Exports reports in PDF, KMZ, and GeoJSON formats

**P1 Requirements (Should-have):**
- ✅ Integrates regulatory and environmental constraints dynamically
- ✅ Enables user-defined asset placement adjustments
- ✅ Provides real-time visualization of layout changes

**P2 Requirements (Nice-to-have):**
- ✅ Supports alternative energy asset placement (solar panels, wind turbines)
- ✅ Integration capabilities with third-party GIS systems

**General Requirements:**
- ✅ Uses AI for optimization recommendations and constraint analysis
- ✅ Handles errors gracefully with informative messages
- ✅ Processes layouts quickly (target: <2 minutes for typical parcels 10-1000 acres)
- ✅ Supports multiple sites processed concurrently (scalability)
- ✅ Modular, config-driven architecture for flexibility
- ✅ Fully deployed and accessible on AWS
- ✅ Secure file handling and data validation
- ✅ Preliminary accuracy acceptable (±10% volumes, ±5ft elevations) for early due diligence
- ✅ Optimizes for site utilization efficiency (20% improvement target)
- ✅ Enables rapid site evaluation (double evaluation rate target)

### Notes

**Best Practices (Aligned with PRD Requirements):**

**Architecture:**
- Modular, config-driven design (all asset types, constraints, rules in config files)
- Use AWS Secrets Manager for API keys and credentials
- Support concurrent processing of multiple sites (scalability requirement)
- Use AWS Step Functions for complex multi-step workflows
- Implement proper error recovery and partial result handling

**Performance (Quick Layout Generation):**
- Target: <2 minutes for typical parcels (10-1000 acres)
- Cache terrain analysis results in S3 and database for performance
- Use AWS Batch or ECS Fargate for large processing jobs
- Optimize geospatial queries with proper spatial indexes in PostGIS
- Use connection pooling for database connections
- Implement caching strategy for regulatory data (update daily, not per-request)

**Data Handling:**
- Implement file size limits (100MB max for KMZ/KML files)
- Auto-fetch topographic data from USGS if not in upload (open-source data focus)
- Add validation for coordinate reference systems (auto-detect and reproject)
- Support multiple coordinate reference systems (WGS84, UTM, State Plane)
- Use presigned URLs for S3 file access
- Add comprehensive input validation and sanitization

**User Experience (Real-time Feedback):**
- Implement progress tracking for long-running operations (WebSocket or polling)
- Add WebSocket support for real-time updates (P1)
- Consider using AWS AppSync for real-time subscriptions (P1)
- Implement layout versioning for undo/redo functionality
- Support save/load of layout templates and scenarios

**Integration:**
- Implement retry logic with exponential backoff for external API calls
- Priority regulatory APIs: FEMA (flood zones), EPA (wetlands), USGS (topography)
- Support third-party GIS integration (QGIS, ArcGIS) via standard formats
- Add support for batch processing multiple properties

**Monitoring & Quality:**
- Use structured logging (JSON format) for CloudWatch
- Add comprehensive CloudWatch monitoring and alarms
- Implement rate limiting for API endpoints
- Add comprehensive unit and integration tests
- Document all API endpoints with OpenAPI/Swagger
- Provide sample KMZ/KML files and mock datasets for testing (PRD requirement)

**Accuracy (Preliminary Due Diligence Focus):**
- Acceptable accuracy: ±10% for cut/fill volumes, ±5ft for elevations
- Prioritize speed over precision for early-stage analysis
- Use grid method for cut/fill (faster) with option for TIN (more accurate)
- Flag potential issues for review rather than hard blocking
- Include accuracy disclaimers in exports (preliminary analysis notice)
- Document assumptions and limitations in reports

**Data Quality & Validation:**
- Validate all input geometries (check for validity, self-intersections)
- Sanitize file inputs to prevent security issues
- Validate coordinate reference systems
- Check for reasonable property sizes and dimensions
- Validate asset dimensions and requirements
- Quality checks on generated layouts (verify constraints, connectivity)
- Standard AWS encryption at rest (S3, RDS) - sufficient for MVP
- Data retention: 90 days active, then archive to S3 Glacier
- Basic backup: RDS automated backups (7-day retention)

**User Management & Collaboration:**
- Simple standalone authentication (AWS Cognito - simplest option)
- Basic roles: Admin, User (no complex permissions)
- Layout sharing with simple permissions (view, edit)
- Shareable links for layouts (private by default, optional public)
- Basic audit logging (who created/modified layouts, when)
- No real-time collaboration for MVP (sequential editing only)

**Job Tracking & Notifications:**
- Batch job status tracking (progress, estimated time)
- Job completion notifications (in-app, optional email)
- Support for long-running operations with status polling
- Job result storage and retrieval

**Version Management:**
- Auto-save layout versions on significant changes
- Manual version creation (snapshot)
- Version comparison (current vs. previous)
- Simple version history (not full branching)

**Cost Estimation (Future Enhancement):**
- MVP focuses on volumes only (cut/fill, road length)
- Cost estimation can be added later (P2) with configurable unit costs
- Export volumes in standard formats for external cost estimation tools

**Mobile/Tablet Support:**
- Responsive web design (works on tablets)
- Mobile view-optimized interface
- View-only mode for mobile (full editing on desktop)
- No native mobile app required for MVP

**Integration & API:**
- RESTful API design for external integration
- Webhook support for job completion events (optional)
- Standard export formats for integration with CAD/GIS tools
- API-first architecture for future integrations

**Performance Targets (Simple Scaling):**
- Support 10-50 concurrent users (start small, scale as needed)
- Handle 50-100 properties processed per day
- Maximum property size: 5000 acres (with performance notice)
- Typical property: 10-1000 acres processes in <2 minutes
- Use AWS auto-scaling for ECS tasks (simple configuration)
- No complex load balancing needed initially

**Simplified Approach Summary:**
- Standalone authentication (AWS Cognito) - no SSO complexity
- Config files for customization (YAML/JSON) - no complex UI config
- Standard AWS security (encryption at rest) - no special requirements
- Simple error handling with fallbacks - rule-based if AI fails
- Standard report formats - no custom templates
- Basic scaling - start small, auto-scale as needed
- Simple onboarding - tooltips and sample data only
```

---

## Final Clarifying Questions

Before implementation, please confirm:

1. **Coordinate System Preference:**
   - Should the system default to a specific coordinate system? (WGS84 for global, or UTM for regional accuracy)
   - Any specific UTM zone requirements?

2. **Sample Data:**
   - Do you have sample KMZ/KML files with typical property data that should be included for testing?
   - Or should the system generate mock test data?

3. **Regulatory Data Priority:**
   - Which regulatory constraints are most critical for your use case? (This helps prioritize API integration)
   - Are there specific states/regions where this will be used initially?

4. **Initial Deployment:**
   - Should this be deployed to a specific AWS region, or is us-east-1 acceptable?
   - Any specific domain/subdomain requirements?

If no specific requirements, the system will use best-practice defaults:
- WGS84 coordinate system (with auto-detection and reprojection)
- Generated mock test data
- All major regulatory APIs (FEMA, EPA, USGS)
- AWS us-east-1 region
- Auto-generated domain

---

**Document Version:** 1.0  
**Last Updated:** November 2025

