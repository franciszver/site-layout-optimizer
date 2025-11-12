# Quick Start Guide - Demo Ready!

## Current Status

✅ **Backend is ready to run** - Most features work without GDAL
✅ **Frontend is fully functional** - All components implemented
⚠️ **GDAL not installed** - Using mock data for file uploads (demo-ready!)

## Start the System

### 1. Start Backend (Terminal 1)
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn src.main:app --reload
```

Server will start at: `http://localhost:8000`

### 2. Start Frontend (Terminal 2)
```powershell
cd frontend
npm install
npm run dev
```

Frontend will start at: `http://localhost:5173`

### 3. Set Environment Variables

Create `frontend/.env`:
```
VITE_API_BASE_URL=http://localhost:8000/api
VITE_MAPBOX_TOKEN=your_mapbox_token_here
```

Get a free Mapbox token: https://account.mapbox.com/access-tokens/

## Test the Demo

1. **Go to**: http://localhost:5173/editor
2. **Upload a file**: Click upload (will use demo data)
3. **Select assets**: Choose asset types and counts
4. **Set entry point**: Click on map
5. **Optimize**: Click "Optimize Layout"
6. **View results**: See assets and roads on map
7. **Export**: Download layout in PDF/KMZ/GeoJSON

## What Works Without GDAL

✅ All API endpoints (health, analyze, optimize, roads, cut/fill, export, constraints)
✅ Frontend UI and interactions
✅ Asset placement and optimization
✅ Road network generation
✅ Cut/fill calculations
✅ Export functionality
✅ AI optimization (if OpenRouter API key is set)
✅ Regulatory constraint fetching

## What Requires GDAL

⚠️ **File Upload**: Currently uses mock/demo data
- Real KMZ/KML parsing requires GDAL
- Mock data works perfectly for demo purposes
- See `GDAL_INSTALL_WINDOWS.md` to add full support

## Install GDAL Later (Optional)

When ready for production:

1. **Option A**: Download pre-built wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal
2. **Option B**: Install Miniconda and use `conda install -c conda-forge gdal`
3. **Option C**: Install GDAL binaries first, then `pip install gdal`

See `GDAL_INSTALL_WINDOWS.md` for detailed instructions.

## Demo Data

The system includes mock property data that demonstrates:
- Property boundaries
- Exclusion zones
- Contour data
- All features work with this demo data

## Next Steps

1. ✅ Start both servers
2. ✅ Test the workflow
3. ✅ Set Mapbox token
4. ⏭️ Install GDAL when ready for real file processing
5. ⏭️ Set up AWS credentials for cloud deployment
6. ⏭️ Configure OpenRouter API key for AI features

**You're ready to demo!** 🚀



