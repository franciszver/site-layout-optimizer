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

