# Backend Deployment Guide - AWS App Runner

This guide walks you through deploying the FastAPI backend to AWS App Runner.

## Prerequisites

- AWS CLI installed and configured
- Docker installed and running
- AWS account with appropriate permissions
- Environment variables ready (OpenRouter API key, etc.)

## Quick Start

### Option 1: Automated Deployment Script

1. **Make the script executable:**
   ```bash
   chmod +x infrastructure/deploy-backend.sh
   ```

2. **Run the deployment:**
   ```bash
   ./infrastructure/deploy-backend.sh dev us-east-1
   ```

3. **Create App Runner service (first time only):**
   - Go to [AWS App Runner Console](https://console.aws.amazon.com/apprunner/)
   - Click "Create service"
   - Follow the steps below

### Option 2: Manual Deployment

#### Step 1: Create ECR Repository

```bash
aws ecr create-repository \
  --repository-name site-layout-optimizer-backend \
  --region us-east-1 \
  --image-scanning-configuration scanOnPush=true
```

#### Step 2: Build and Push Docker Image

```bash
# Login to ECR
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t site-layout-optimizer-backend:latest -f backend/Dockerfile .

# Tag image
docker tag site-layout-optimizer-backend:latest \
  ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/site-layout-optimizer-backend:latest

# Push image
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/site-layout-optimizer-backend:latest
```

#### Step 3: Create App Runner Service

1. **Go to AWS App Runner Console:**
   - Navigate to: https://console.aws.amazon.com/apprunner/

2. **Click "Create service"**

3. **Configure source:**
   - **Source type**: Container registry
   - **Provider**: Amazon ECR
   - **Container image URI**: Select your ECR repository and image
   - **Deployment trigger**: Automatic (or manual)

4. **Configure service:**
   - **Service name**: `site-layout-optimizer-backend-dev`
   - **Virtual CPU**: 1 vCPU
   - **Memory**: 2 GB
   - **Port**: 8000

5. **Set environment variables:**
   ```
   ENVIRONMENT=production
   OPENROUTER_API_KEY=your_openrouter_key_here
   AWS_REGION=us-east-1
   DATABASE_URL=postgresql://user:pass@host:5432/dbname (if using RDS)
   S3_BUCKET_GEOSPATIAL=dev-site-layout-geospatial
   S3_BUCKET_PROCESSED=dev-site-layout-processed
   S3_BUCKET_EXPORTS=dev-site-layout-exports
   S3_BUCKET_TERRAIN_CACHE=dev-site-layout-terrain-cache
   ```

6. **Configure health check:**
   - **Path**: `/health`
   - **Interval**: 10 seconds
   - **Timeout**: 5 seconds

7. **Review and create**

#### Step 4: Get Service URL

After deployment, App Runner will provide a service URL like:
```
https://xxxxxxxxxx.us-east-1.awsapprunner.com
```

Copy this URL - you'll need it for the frontend configuration.

## Update Frontend Configuration

1. **Update Amplify environment variables:**
   - Go to Amplify Console → Your App → Environment variables
   - Set `VITE_API_BASE_URL` to your App Runner service URL + `/api`
   - Example: `https://xxxxxxxxxx.us-east-1.awsapprunner.com/api`

2. **Update backend CORS (if needed):**
   - The backend CORS is already configured to allow Amplify domains
   - If you have a custom domain, add it to `backend/src/main.py`

## Updating the Deployment

### Automatic Updates (if enabled)
- Push new image to ECR
- App Runner will automatically detect and deploy

### Manual Updates
```bash
# Rebuild and push
./infrastructure/deploy-backend.sh dev us-east-1

# Or manually trigger deployment
aws apprunner start-deployment \
  --service-arn arn:aws:apprunner:us-east-1:ACCOUNT_ID:service/SERVICE_NAME \
  --region us-east-1
```

## Cost Considerations

**App Runner Pricing (us-east-1):**
- **Compute**: ~$0.007 per vCPU-hour, ~$0.0008 per GB-hour
- **Example**: 1 vCPU, 2 GB, running 24/7 = ~$0.20/day = ~$6/month
- **Free tier**: None (but very cost-effective for demos)

**ECR Pricing:**
- **Storage**: $0.10 per GB/month
- **Data transfer**: First 1 GB/month free, then $0.09/GB

**Total estimated cost for demo**: ~$10-20/month (depending on usage)

## Troubleshooting

### Image build fails
- Check Docker is running
- Verify `backend/Dockerfile` exists
- Check `backend/requirements.txt` is valid

### ECR push fails
- Verify AWS credentials are configured
- Check ECR repository exists
- Verify you're logged in to ECR

### App Runner service fails to start
- Check environment variables are set correctly
- Verify health check path `/health` is accessible
- Check CloudWatch logs for errors

### CORS errors from frontend
- Verify App Runner URL is added to CORS in `backend/src/main.py`
- Check frontend `VITE_API_BASE_URL` is correct

## Next Steps

1. ✅ Backend deployed to App Runner
2. ⏭️ Update Amplify environment variables with App Runner URL
3. ⏭️ Test end-to-end: Frontend → Backend → Database
4. ⏭️ Set up monitoring and alerts (optional)

## Additional Resources

- [AWS App Runner Documentation](https://docs.aws.amazon.com/apprunner/)
- [ECR Documentation](https://docs.aws.amazon.com/ecr/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)

