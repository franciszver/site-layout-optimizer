# Next Steps - Get Your System Running! 🚀

## Step 1: Start the Backend Server

Open a terminal and run:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn src.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

✅ **Server is ready when you see "Application startup complete"**

## Step 2: Start the Frontend

Open a **NEW terminal** and run:

```powershell
cd frontend
npm install
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

✅ **Frontend is ready when you see the local URL**

## Step 3: Set Up Environment Variables

### Frontend (.env file)

Create `frontend/.env`:
```
VITE_API_BASE_URL=http://localhost:8000/api
VITE_MAPBOX_TOKEN=your_mapbox_token_here
```

**Get a free Mapbox token:**
1. Go to: https://account.mapbox.com/access-tokens/
2. Sign up (free) or log in
3. Copy your default public token
4. Paste it in `frontend/.env`

### Backend (.env file) - Optional for now

Create `backend/.env` (only needed for AWS/OpenRouter):
```
OPENROUTER_API_KEY=your_key_here
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
```

**Note:** Backend works without these for basic demo features!

## Step 4: Test the System

1. **Open browser**: http://localhost:5173
2. **Click**: "Create New Layout"
3. **Upload a file**: Click the upload area (will use demo data)
4. **Select assets**: Choose asset types and counts
5. **Set entry point**: Click on the map
6. **Optimize**: Click "Optimize Layout" button
7. **View results**: See assets and roads appear on map!

## What Works Right Now

✅ File upload (uses demo data - no GDAL needed!)
✅ Asset placement and selection
✅ Layout optimization
✅ Road network generation
✅ Map visualization
✅ Export functionality
✅ All UI interactions

## Troubleshooting

### Server won't start?
- Make sure you're in the `backend` directory
- Check that virtual environment is activated
- Look for error messages in the terminal

### Frontend won't start?
- Run `npm install` first
- Check Node.js is installed: `node --version`
- Make sure port 5173 is not in use

### Map not showing?
- Check that `VITE_MAPBOX_TOKEN` is set in `frontend/.env`
- Restart the frontend after adding the token

### API errors?
- Make sure backend is running on port 8000
- Check browser console for errors
- Verify `VITE_API_BASE_URL` in frontend/.env

## Ready to Demo!

Once both servers are running:
- ✅ Backend: http://localhost:8000
- ✅ Frontend: http://localhost:5173
- ✅ API Docs: http://localhost:8000/docs

**You're all set!** 🎉



