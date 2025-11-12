# Mapbox Setup Guide

## Getting Your Access Token

1. **Go to Mapbox**: https://account.mapbox.com/access-tokens/
2. **Sign up** (free tier includes 50,000 map loads/month)
3. **Copy your Default Public Token** (starts with `pk.eyJ...`)

## Setting Up the Token

### Option 1: Environment Variable (Recommended)

Create `frontend/.env`:
```
VITE_MAPBOX_TOKEN=pk.eyJ...your_token_here
VITE_API_BASE_URL=http://localhost:8000/api
```

**Important:** 
- Never commit `.env` to git (it's in `.gitignore`)
- Restart the frontend server after adding the token

### Option 2: Hardcode (For Testing Only)

Edit `frontend/src/pages/LayoutEditor.tsx`:
```typescript
const [mapboxToken, setMapboxToken] = useState<string>('pk.eyJ...your_token_here')
```

## Troubleshooting

### Error: "Style is not valid"
- **Cause**: Token doesn't have access to the style
- **Fix**: Make sure you're using a valid public token

### Error: "401 Unauthorized"
- **Cause**: Invalid or expired token
- **Fix**: Get a new token from Mapbox account

### Error: "Failed to load style"
- **Cause**: Network issue or token permissions
- **Fix**: 
  1. Check token is correct
  2. Check browser console for detailed error
  3. Verify token has "Styles: Read" permission

### Map Not Showing
- Check browser console for errors
- Verify token is set in `.env` file
- Restart frontend after adding token
- Check network tab for failed API calls

## Token Permissions Needed

Your token needs:
- ✅ **Styles: Read** (to load map styles)
- ✅ **Fonts: Read** (for text rendering)
- ✅ **Sprites: Read** (for icons)

These are included by default in public tokens.

## Free Tier Limits

- **50,000 map loads/month** (free)
- Perfect for development and demos
- Upgrade if you need more

## Security Note

⚠️ **Never expose your token in:**
- Public repositories
- Client-side code (if using secret token)
- Screenshots or videos

For production, use:
- Environment variables
- Token restrictions (scoped tokens)
- Domain restrictions

## Testing Your Token

Test if your token works:
```
https://api.mapbox.com/styles/v1/mapbox/satellite-v9?access_token=YOUR_TOKEN
```

Should return JSON (not an error).

