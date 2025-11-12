# Mapbox Fix - Quick Solution

## The Problem

The Mapbox API call is failing. This is usually due to:
1. **Invalid or expired token**
2. **Version mismatch** (we're updating this)
3. **Token permissions**

## Quick Fix Steps

### Step 1: Update Dependencies

```powershell
cd frontend
npm install
```

This will install the updated `mapbox-gl@^3.6.0` version.

### Step 2: Get a Fresh Token

The token in your URL might be invalid. Get a new one:

1. **Go to**: https://account.mapbox.com/access-tokens/
2. **Log in** (or sign up - it's free)
3. **Copy your Default Public Token**
4. **Update** `frontend/.env`:
   ```
   VITE_MAPBOX_TOKEN=pk.eyJ...your_new_token_here
   VITE_API_BASE_URL=http://localhost:8000/api
   ```

### Step 3: Restart Frontend

```powershell
# Stop the frontend (Ctrl+C)
# Then restart:
npm run dev
```

## Verify Token Works

Test your token by opening this URL in browser:
```
https://api.mapbox.com/styles/v1/mapbox/satellite-v9?access_token=YOUR_TOKEN
```

**Should return:** JSON data (not an error)

## Common Errors & Solutions

### "401 Unauthorized"
- **Fix**: Get a new token from Mapbox account

### "Style is not valid"  
- **Fix**: Make sure token has "Styles: Read" permission (default for public tokens)

### "Failed to load"
- **Fix**: 
  1. Check token is in `.env` file
  2. Restart frontend after adding token
  3. Check browser console for detailed error

## What I Fixed

✅ Updated `mapbox-gl` from 3.0.1 to 3.6.0 (compatible with latest API)
✅ Added error handling in MapViewer component
✅ Added token validation
✅ Better error messages in console

## After Fixing

The map should:
- ✅ Load the satellite style
- ✅ Display property boundaries
- ✅ Show assets and roads
- ✅ Allow clicking to set entry point

If it still doesn't work, check the browser console (F12) for specific error messages.

