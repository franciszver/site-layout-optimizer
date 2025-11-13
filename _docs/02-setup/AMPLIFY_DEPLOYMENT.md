# AWS Amplify Deployment Guide

Quick reference for deploying the frontend to AWS Amplify.

## Prerequisites

- ✅ GitHub repository pushed to remote
- ✅ AWS account with Amplify access
- ✅ Backend API URL (when backend is deployed) or use localhost for testing
- ✅ Mapbox access token

## Quick Setup Steps

### 1. Connect Repository

1. Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify/)
2. Click **"New app"** → **"Host web app"**
3. Select **"GitHub"** and authorize AWS to access your repositories
4. Select your repository: `site-layout-optimizer`
5. Select branch: `main` (or your default branch)

### 2. Build Settings

Amplify will automatically detect `amplify.yml` in the root directory. Verify:

- **Build command**: `npm run build` (handled by amplify.yml)
- **Output directory**: `frontend/dist`
- **Base directory**: Leave empty (or set to `frontend/` if needed)

### 3. Environment Variables

Go to **App settings** → **Environment variables** and add:

| Variable | Value | Notes |
|----------|-------|-------|
| `VITE_API_BASE_URL` | `https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/dev/api` | Your deployed backend API URL |
| `VITE_MAPBOX_TOKEN` | `pk.eyJ...` | Your Mapbox access token |

**Note**: 
- If backend is not deployed yet, you can set `VITE_API_BASE_URL` to `http://localhost:8000/api` for testing (though this won't work from Amplify domain - you'll need the actual API Gateway URL)
- Get your Mapbox token from: https://account.mapbox.com/access-tokens/

### 4. Deploy

1. Click **"Save and deploy"**
2. Amplify will:
   - Install dependencies
   - Build the React app
   - Deploy to CDN
3. Your app will be available at: `https://[app-id].amplifyapp.com`

## After Deployment

### Get Your App URL

1. Go to Amplify Console
2. Click on your app
3. Copy the app URL from the top (e.g., `https://main.d1234567890.amplifyapp.com`)

### Update Backend CORS (If Needed)

If you haven't already, update `backend/src/main.py` to include your Amplify domain:

```python
allow_origins=[
    # ... existing localhost origins ...
    "https://*.amplifyapp.com",  # Already added in the code
    "https://main.d1234567890.amplifyapp.com",  # Your specific domain (optional)
]
```

## Automatic Deployments

Amplify automatically deploys when you:
- Push to the connected branch
- Merge pull requests (if configured)
- Manually trigger a deployment

## Local Development

**Important**: Local development continues to work independently:

- ✅ `npm run dev` still works
- ✅ Uses `http://localhost:8000/api` automatically
- ✅ No dependency on Amplify
- ✅ Can demo offline

## Troubleshooting

### Build Fails

1. Check build logs in Amplify Console
2. Verify `frontend/amplify.yml` is correct
3. Ensure `package.json` has all dependencies
4. Check Node.js version (Amplify uses Node 18 by default)

### API Calls Fail

1. Verify `VITE_API_BASE_URL` is set correctly
2. Check backend CORS configuration includes Amplify domain
3. Verify backend is deployed and accessible
4. Check browser console for CORS errors

### Mapbox Not Loading

1. Verify `VITE_MAPBOX_TOKEN` is set
2. Check token has correct permissions
3. Verify token is not expired
4. Check browser console for errors

## Cost

- **Free Tier**: 1000 build minutes/month, 15 GB storage
- **After Free Tier**: Pay-as-you-go pricing
- **Typical Cost**: $0-5/month for demo usage

## Next Steps

1. ✅ Frontend deployed to Amplify
2. ⏭️ Deploy backend to AWS (Lambda/ECS)
3. ⏭️ Update `VITE_API_BASE_URL` with actual API Gateway URL
4. ⏭️ Test full integration
5. ⏭️ Configure custom domain (optional)

