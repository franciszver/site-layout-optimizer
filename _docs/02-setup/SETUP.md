# Site Layout Optimizer - Setup Guide

## Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 14+ with PostGIS extension
- AWS Account (for deployment)
- OpenRouter API Key (for AI features)
- Mapbox Access Token (for frontend maps)

## Backend Setup

1. **Create virtual environment:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. **Set up PostgreSQL database:**
```bash
# Create database
createdb site_layout_optimizer

# Enable PostGIS extension
psql site_layout_optimizer -c "CREATE EXTENSION postgis;"

# Initialize tables
python src/utils/db_init.py
```

5. **Run backend:**
```bash
uvicorn src.main:app --reload
```

Backend will be available at http://localhost:8000

## Frontend Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your Mapbox token
```

3. **Run frontend:**
```bash
npm run dev
```

Frontend will be available at http://localhost:5173

## AWS Deployment

### Frontend Deployment (AWS Amplify)

AWS Amplify provides automatic hosting, HTTPS, and CI/CD for the React frontend.

#### Prerequisites
- GitHub repository pushed to remote
- AWS account with Amplify access
- Backend API deployed (or use localhost for testing)

#### Setup Steps

1. **Connect Repository in Amplify Console:**
   - Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify/)
   - Click "New app" → "Host web app"
   - Select "GitHub" and authorize
   - Select your repository and branch (usually `main` or `master`)

2. **Build Settings (Auto-detected):**
   - Amplify will automatically detect `amplify.yml` in the root directory
   - Verify settings:
     - Build command: `npm run build` (handled by amplify.yml)
     - Output directory: `frontend/dist`

3. **Environment Variables:**
   - Go to App settings → Environment variables
   - Add required variables:
     - `VITE_API_BASE_URL`: Your API Gateway URL (e.g., `https://abc123.execute-api.us-east-1.amazonaws.com/dev/api`)
     - `VITE_MAPBOX_TOKEN`: Your Mapbox access token

4. **Deploy:**
   - Click "Save and deploy"
   - Amplify will build and deploy automatically
   - Your app will be available at `https://[app-id].amplifyapp.com`

#### Local Development Safety
- ✅ Local development (`npm run dev`) continues to work independently
- ✅ No changes needed to local `.env` file
- ✅ Can demo locally even if Amplify is down
- ✅ Code automatically detects environment and uses correct API URL

### Backend Deployment (AWS SAM)

1. **Install AWS SAM CLI:**
```bash
# Follow AWS SAM installation guide
```

2. **Configure AWS credentials:**
```bash
aws configure
```

3. **Deploy infrastructure:**
```bash
cd infrastructure
chmod +x deploy.sh
./deploy.sh dev
```

## Testing

Run backend tests:
```bash
cd backend
pytest tests/
```

## Demo Data

Generate demo properties:
```python
from src.utils.demo_data_generator import DemoDataGenerator

generator = DemoDataGenerator()
flat_property = generator.generate_flat_terrain_property()
hilly_property = generator.generate_hilly_terrain_property()
constrained_property = generator.generate_constrained_property()
```

## API Documentation

Once backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### GDAL Installation Issues
On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install gdal-bin libgdal-dev python3-gdal
```

On macOS:
```bash
brew install gdal
```

### PostGIS Issues
Ensure PostgreSQL is installed with PostGIS:
```bash
# Ubuntu/Debian
sudo apt-get install postgresql-postgis

# macOS
brew install postgis
```

