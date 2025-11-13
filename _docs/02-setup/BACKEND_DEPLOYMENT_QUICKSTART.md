# Backend Deployment - Quick Start

## Prerequisites Checklist

- [ ] AWS CLI installed and configured (`aws configure`)
- [ ] Docker installed and running
- [ ] OpenRouter API key ready
- [ ] AWS account with permissions for ECR and App Runner

## 5-Minute Deployment

### Step 1: Build and Push to ECR

**Windows:**
```powershell
.\infrastructure\deploy-backend.ps1 dev us-east-1
```

**Linux/Mac:**
```bash
chmod +x infrastructure/deploy-backend.sh
./infrastructure/deploy-backend.sh dev us-east-1
```

This will:
- Create ECR repository (if needed)
- Build Docker image
- Push to ECR

### Step 2: Create App Runner Service

1. Go to [AWS App Runner Console](https://console.aws.amazon.com/apprunner/)
2. Click **"Create service"**
3. Select **"Container registry"** → **"Amazon ECR"**
4. Choose your repository: `site-layout-optimizer-backend`
5. Select image: `latest`
6. Configure:
   - **Service name**: `site-layout-optimizer-backend-dev`
   - **Virtual CPU**: 1 vCPU
   - **Memory**: 2 GB
   - **Port**: 8000
7. Add environment variables:
   ```
   ENVIRONMENT=production
   OPENROUTER_API_KEY=your_key_here
   AWS_REGION=us-east-1
   ```
8. Health check:
   - **Path**: `/health`
   - **Interval**: 10 seconds
9. Click **"Create & deploy"**

### Step 3: Get Your API URL

After deployment (5-10 minutes), copy the service URL:
```
https://xxxxxxxxxx.us-east-1.awsapprunner.com
```

### Step 4: Update Frontend

1. Go to [Amplify Console](https://console.aws.amazon.com/amplify/)
2. Select your app → **Environment variables**
3. Set `VITE_API_BASE_URL` to: `https://xxxxxxxxxx.us-east-1.awsapprunner.com/api`
4. Redeploy (or wait for auto-deploy)

## Testing

1. Visit your Amplify frontend URL
2. Try uploading a KML file
3. Check browser console for errors
4. Check App Runner logs in CloudWatch if issues occur

## Troubleshooting

**Build fails?**
- Check Docker is running
- Verify `backend/Dockerfile` exists
- Check AWS credentials: `aws sts get-caller-identity`

**ECR push fails?**
- Verify you're logged in: `aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin`
- Check repository exists in ECR console

**App Runner service fails?**
- Check environment variables are set
- Verify health check path `/health` works
- Check CloudWatch logs

**CORS errors?**
- Backend CORS is already configured for Amplify and App Runner domains
- Verify `VITE_API_BASE_URL` in Amplify matches your App Runner URL

## Cost Estimate

- **App Runner**: ~$6/month (1 vCPU, 2 GB, 24/7)
- **ECR**: ~$1/month (storage)
- **Total**: ~$7-10/month for demo

## Next Steps

See `BACKEND_DEPLOYMENT.md` for detailed documentation.

