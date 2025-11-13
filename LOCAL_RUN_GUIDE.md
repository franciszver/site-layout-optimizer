# Local Development Walkthrough

This guide will walk you through running the Site Layout Optimizer locally on your machine.

## Prerequisites Check

Before starting, make sure you have:

- ✅ **Python 3.11+** installed
  - Check: `python --version` or `py --version`
- ✅ **Node.js 18+** and npm installed
  - Check: `node --version` and `npm --version`
- ✅ **Git** (if cloning from repository)

**Optional but recommended:**
- Mapbox Access Token (for map visualization)
  - Get one free at: https://account.mapbox.com/access-tokens/
- OpenRouter API Key (for AI optimization features)
  - Get one at: https://openrouter.ai/

---

## Step 1: Backend Setup

### 1.1 Navigate to Backend Directory

```powershell
cd backend
```

### 1.2 Create Virtual Environment

```powershell
python -m venv venv
```

Or if you have multiple Python versions:
```powershell
py -3.11 -m venv venv
```

### 1.3 Activate Virtual Environment

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**
```cmd
venv\Scripts\activate.bat
```

You should see `(venv)` in your prompt.

### 1.4 Install Dependencies

```powershell
pip install -r requirements.txt
```

This may take a few minutes. If you encounter errors with `numpy` or `pandas`, try:
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 1.5 Set Up Environment Variables (Optional)

Create a `.env` file in the `backend` directory:

```powershell
# Create .env file
New-Item -Path .env -ItemType File
```

Add these variables (if you have them):
```env
OPENROUTER_API_KEY=your_openrouter_key_here
AWS_ACCESS_KEY_ID=your_aws_key (optional)
AWS_SECRET_ACCESS_KEY=your_aws_secret (optional)
```

**Note:** The backend will work without these for basic functionality. AI features require OpenRouter API key.

### 1.6 Start the Backend Server

```powershell
uvicorn src.main:app --reload
```

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **Backend is running at:** http://localhost:8000

**Keep this terminal open!** The server will auto-reload when you make code changes.

---

## Step 2: Frontend Setup

### 2.1 Open a New Terminal

Open a **new PowerShell/Command Prompt window** (keep the backend terminal running).

### 2.2 Navigate to Frontend Directory

```powershell
cd frontend
```

### 2.3 Install Dependencies

```powershell
npm install
```

This may take a few minutes on first run.

### 2.4 Set Up Environment Variables

Create a `.env` file in the `frontend` directory:

```powershell
# Create .env file
New-Item -Path .env -ItemType File
```

Add these variables:
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_MAPBOX_TOKEN=your_mapbox_token_here
```

**Important:**
- `VITE_API_BASE_URL` should point to your local backend
- `VITE_MAPBOX_TOKEN` is required for the map to display
  - Get a free token: https://account.mapbox.com/access-tokens/
  - Create a new token with "Public" scope

### 2.5 Start the Frontend Development Server

```powershell
npm run dev
```

You should see output like:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

✅ **Frontend is running at:** http://localhost:5173

**Note:** The frontend may also run on `http://localhost:3001` depending on your Vite configuration.

---

## Step 3: Access the Application

### 3.1 Open in Browser

Navigate to: **http://localhost:5173/editor**

Or if it's on port 3001: **http://localhost:3001/editor**

### 3.2 Verify Backend Connection

- Open browser DevTools (F12)
- Check the Console tab
- You should see API calls to `http://localhost:8000/api`
- No CORS errors should appear

---

## Step 4: Test the Application

### 4.1 Test Workflow

1. **Upload Property File**
   - Click "Upload Property File" in Step 1
   - Upload any file (or use demo data)
   - The system will use mock data if GDAL is not installed

2. **Terrain Analysis** (Step 2)
   - Should auto-complete after upload
   - Shows terrain statistics

3. **Asset Placement** (Step 3)
   - Select asset types (e.g., "Solar Panel", "Wind Turbine")
   - Set counts
   - Click "Optimize Layout"
   - Wait for optimization (may take 30-90 seconds)

4. **Road Network** (Step 4)
   - Click on the map to set entry point
   - Roads should auto-generate
   - Or click "Generate Roads" button

5. **Export** (Step 5)
   - Choose export format (PDF, KMZ, GeoJSON)
   - Click "Export"
   - File should download

### 4.2 Test New Features

**Drag-and-Drop Assets:**
- After assets are placed, try dragging them on the map
- Valid positions show green, invalid show red
- Asset positions update in real-time

**Layer Panel:**
- Use checkboxes in the left sidebar to toggle layer visibility
- Try hiding/showing property boundary, exclusion zones, assets, roads

**Step Navigation:**
- Use "Next →" and "← Previous" buttons to navigate between steps
- Steps show completion status with checkmarks

---

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or use a different port
uvicorn src.main:app --reload --port 8001
```

**Module not found errors:**
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

**GDAL errors:**
- The app works without GDAL using mock data
- File uploads will use demo data automatically
- See `_docs/02-setup/GDAL_INSTALL_WINDOWS.md` if you need real KMZ/KML parsing

### Frontend Issues

**Port 5173 or 3001 already in use:**
```powershell
# Find process using the port
netstat -ano | findstr :5173

# Kill the process
taskkill /PID <PID> /F

# Or use a different port (edit vite.config.ts)
```

**Map not displaying:**
- Check that `VITE_MAPBOX_TOKEN` is set in `frontend/.env`
- Verify the token is valid at https://account.mapbox.com/access-tokens/
- Check browser console for errors

**API connection errors:**
- Verify backend is running on `http://localhost:8000`
- Check `VITE_API_BASE_URL` in `frontend/.env`
- Check CORS settings in backend (should allow `localhost:5173` and `localhost:3001`)

**Build errors:**
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again
- Check Node.js version: `node --version` (should be 18+)

### General Issues

**Both servers won't start:**
- Check if ports are available
- Restart your computer if needed
- Check firewall settings

**Changes not reflecting:**
- Backend: Should auto-reload with `--reload` flag
- Frontend: Should auto-reload with Vite
- Hard refresh browser: `Ctrl+Shift+R` or `Ctrl+F5`

---

## Quick Reference

### Start Both Servers (Two Terminals)

**Terminal 1 - Backend:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn src.main:app --reload
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

### Stop Servers

- Press `Ctrl+C` in each terminal
- Deactivate virtual environment: `deactivate` (backend terminal)

### Check API Health

Visit: http://localhost:8000/health

Should return: `{"status": "healthy"}`

### View API Documentation

Visit: http://localhost:8000/docs

Interactive Swagger UI with all endpoints.

---

## Next Steps

Once everything is running:

1. ✅ Test the complete workflow
2. ✅ Try drag-and-drop asset placement
3. ✅ Test layer visibility toggles
4. ✅ Export layouts in different formats
5. ✅ Check GIS integration endpoints at `/api/gis/layouts`

**You're all set!** 🚀

For deployment instructions, see:
- Frontend: `_docs/02-setup/AMPLIFY_DEPLOYMENT.md`
- Backend: `_docs/02-setup/BACKEND_DEPLOYMENT.md`

