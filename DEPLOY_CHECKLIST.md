# Deployment Checklist

## Pre-Deployment

- [ ] All changes committed to Git
- [ ] Changes pushed to GitHub (main branch)
- [ ] Backend and frontend tested locally
- [ ] Environment variables ready

## Frontend Deployment (AWS Amplify)

### Option 1: Automatic (Recommended)
1. **Push to GitHub** - Amplify will auto-deploy
   ```powershell
   git add .
   git commit -m "Fix terrain stats display and API URL for Windows"
   git push origin main
   ```

2. **Monitor deployment:**
   - Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify/)
   - Select your app
   - Watch the build progress

### Option 2: Manual Trigger
1. Go to Amplify Console → Your App
2. Click **"Redeploy this version"** (if needed)

### Verify Frontend
- [ ] Visit Amplify URL
- [ ] Check that terrain stats display correctly
- [ ] Test file upload
- [ ] Verify API connection

## Backend Deployment (AWS App Runner)

### Step 1: Build and Push Docker Image

**Windows:**
```powershell
.\infrastructure\deploy-backend.ps1 dev us-east-1
```

**Linux/Mac:**
```bash
./infrastructure/deploy-backend.sh dev us-east-1
```

This will:
- Build Docker image with latest code
- Push to ECR
- App Runner will auto-deploy (if auto-deploy enabled)

### Step 2: Verify Backend

1. **Check App Runner service:**
   - Go to [AWS App Runner Console](https://console.aws.amazon.com/apprunner/)
   - Verify service is "Running" and healthy

2. **Test health endpoint:**
   ```
   https://your-app-runner-url.us-east-1.awsapprunner.com/health
   ```
   Should return: `{"status":"healthy"}`

### Step 3: Update Frontend API URL (if backend URL changed)

1. Go to [Amplify Console](https://console.aws.amazon.com/amplify/)
2. Select your app → **Environment variables**
3. Update `VITE_API_BASE_URL` to: `https://your-app-runner-url.us-east-1.awsapprunner.com/api`
4. Save (will trigger redeploy)

## Post-Deployment Testing

- [ ] Frontend loads correctly
- [ ] File upload works
- [ ] Terrain analysis displays stats
- [ ] Asset optimization works
- [ ] Road generation works
- [ ] Export functionality works
- [ ] No console errors

## Troubleshooting

**Frontend build fails?**
- Check Amplify build logs
- Verify `amplify.yml` is correct
- Check environment variables

**Backend deployment fails?**
- Check Docker is running
- Verify AWS credentials: `aws sts get-caller-identity`
- Check ECR repository exists
- Review App Runner logs in CloudWatch

**API connection issues?**
- Verify `VITE_API_BASE_URL` in Amplify matches backend URL
- Check backend CORS settings
- Verify backend health endpoint works

## Quick Commands

```powershell
# Check Git status
git status

# Commit and push
git add .
git commit -m "Deploy latest changes"
git push origin main

# Deploy backend
.\infrastructure\deploy-backend.ps1 dev us-east-1

# Check AWS credentials
aws sts get-caller-identity
```

