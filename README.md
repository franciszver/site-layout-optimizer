# Site Layout Optimizer - Pacifico Energy Group

AI-powered geospatial site layout optimization system for real estate due diligence. This system processes KMZ/KML files and topographic data to generate optimized layouts with asset placement, road networks, and cut/fill estimation.

## 🚀 Quick Start

```bash
# Backend
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3001` to use the application.

## ✨ Features

- **Geospatial Processing**: Import and validate KMZ/KML files with automatic coordinate system detection
- **Terrain Analysis**: Compute slope, aspect, and elevation differentials from topographic data
- **AI-Powered Optimization**: Automated asset placement with constraint analysis using GPT-4o
- **Road Network Generation**: Automatic road network generation connecting property entry to assets
- **Cut/Fill Estimation**: Volume calculations with visualization maps
- **Regulatory Integration**: Dynamic integration of FEMA, EPA, and USGS regulatory constraints
- **Interactive Editor**: Real-time visualization with drag-and-drop asset placement
- **Export Capabilities**: PDF, KMZ, and GeoJSON export formats

## 📁 Project Structure

```
site-layout-optimizer/
├── frontend/          # React TypeScript frontend
├── backend/           # FastAPI Python backend
├── infrastructure/    # AWS infrastructure templates
├── _docs/             # All documentation (organized)
└── tests/             # Test files and sample data
```

## 📚 Documentation

All documentation is organized in the `_docs/` folder. See `_docs/README.md` for the complete index.

- **Getting Started**: `_docs/01-getting-started/`
- **Setup Guides**: `_docs/02-setup/`
- **Demo Materials**: `_docs/03-demo/`
- **Development**: `_docs/04-development/`
- **Reference**: `_docs/05-reference/`

## 🛠️ Tech Stack

- **Frontend**: React (TypeScript) with Mapbox GL JS
- **Backend**: Python FastAPI with geospatial libraries (GDAL, Shapely, GeoPandas, Rasterio)
- **Database**: PostgreSQL with PostGIS extension
- **Storage**: AWS S3
- **Compute**: AWS Lambda + ECS Fargate
- **AI**: OpenAI GPT-4o via OpenRouter

## ⚙️ Configuration

### Required Environment Variables

**Frontend** (`frontend/.env`):
```
VITE_API_BASE_URL=http://localhost:8000/api
VITE_MAPBOX_TOKEN=your_mapbox_token_here
```

**Backend** (`backend/.env`):
```
OPENROUTER_API_KEY=your_openrouter_key_here
AWS_ACCESS_KEY_ID=your_aws_key (optional)
AWS_SECRET_ACCESS_KEY=your_aws_secret (optional)
```

See `_docs/02-setup/ENV_SETUP.md` for detailed setup instructions.

## 🧪 Testing

Use the testing checklist: `_docs/03-demo/TESTING_CHECKLIST.md`

## 📖 API Documentation

When the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🚢 Deployment

### Frontend (AWS Amplify)
The React frontend can be deployed to AWS Amplify for automatic hosting, HTTPS, and CI/CD:
- Connect GitHub repository in Amplify Console
- Configure environment variables (`VITE_API_BASE_URL`, `VITE_MAPBOX_TOKEN`)
- Automatic deployments on git push
- See `_docs/02-setup/SETUP.md` for detailed instructions

**Note**: Local development continues to work independently - you can demo locally even if Amplify is down.

### Backend (AWS App Runner)
The FastAPI backend can be deployed to AWS App Runner for automatic scaling and HTTPS:
- Build and push Docker image to ECR
- Deploy to App Runner using provided scripts
- See `_docs/02-setup/BACKEND_DEPLOYMENT.md` for detailed instructions

**Quick deploy:**
```bash
# Windows PowerShell
.\infrastructure\deploy-backend.ps1 dev us-east-1

# Linux/Mac
./infrastructure/deploy-backend.sh dev us-east-1
```

## 📄 License

Proprietary - Pacifico Energy Group

## 👥 Contributing

This is a proprietary project for Pacifico Energy Group.

---

**Status**: ✅ Ready for Demo
**Last Updated**: 2025-01-XX
