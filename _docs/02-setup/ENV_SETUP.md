# Environment Variables Setup

## Overview

This project uses environment variables for all sensitive configuration. Never commit `.env` files to git!

## Quick Setup

1. **Backend**: Copy `backend/.env.example` to `backend/.env` and fill in values
2. **Frontend**: Copy `frontend/.env.example` to `frontend/.env` and fill in values

## Required Variables

### Backend (`backend/.env`)

**Required:**
- `OPENROUTER_API_KEY` - Your OpenRouter API key for AI features

**Optional (for cloud deployment):**
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `AWS_REGION` - AWS region (default: us-east-1)

**Optional (for database):**
- `DATABASE_URL` - Full PostgreSQL connection string
- `POSTGRES_USER` - Database user
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_DB` - Database name
- `POSTGRES_HOST` - Database host
- `POSTGRES_PORT` - Database port

### Frontend (`frontend/.env`)

**Required:**
- `VITE_MAPBOX_TOKEN` - Your Mapbox access token (get from https://account.mapbox.com/access-tokens/)
- `VITE_API_BASE_URL` - Backend API URL (default: http://localhost:8000/api)

## Getting API Keys

### OpenRouter API Key
1. Go to: https://openrouter.ai/
2. Sign up or log in
3. Create an API key
4. Copy to `OPENROUTER_API_KEY` in `backend/.env`

### Mapbox Token
1. Go to: https://account.mapbox.com/access-tokens/
2. Sign up (free tier available)
3. Copy your Default Public Token
4. Copy to `VITE_MAPBOX_TOKEN` in `frontend/.env`

## Security Notes

⚠️ **Never commit `.env` files!**
- `.env` files are in `.gitignore`
- Use `.env.example` files for documentation
- Keep real credentials local only

## Verification

After setting up `.env` files:
1. Restart backend server
2. Restart frontend server
3. Check console for any missing variable warnings

