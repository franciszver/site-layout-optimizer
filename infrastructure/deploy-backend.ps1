# Site Layout Optimizer - Backend Deployment Script (PowerShell)
# Deploys FastAPI backend to AWS App Runner

param(
    [string]$Environment = "dev",
    [string]$Region = "us-east-1"
)

$ErrorActionPreference = "Stop"

# Validate parameters
if ([string]::IsNullOrWhiteSpace($Environment)) {
    Write-Host "Error: Environment parameter cannot be empty." -ForegroundColor Red
    exit 1
}

if ([string]::IsNullOrWhiteSpace($Region)) {
    Write-Host "Error: Region parameter cannot be empty." -ForegroundColor Red
    exit 1
}

$ECR_REPO_NAME = "site-layout-optimizer-backend"
$APP_RUNNER_SERVICE_NAME = "site-layout-optimizer-backend-$Environment"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Deploying Backend to AWS App Runner" -ForegroundColor Cyan
Write-Host "Environment: $Environment" -ForegroundColor Cyan
Write-Host "Region: $Region" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if AWS CLI is installed
if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    Write-Host "Error: AWS CLI is not installed. Please install it first." -ForegroundColor Red
    exit 1
}

# Check if Docker is installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Docker is not installed. Please install it first." -ForegroundColor Red
    exit 1
}

# Check if Docker is running
Write-Host "Checking if Docker is running..." -ForegroundColor Yellow
$ErrorActionPreference = "SilentlyContinue"
docker info 2>&1 | Out-Null
$ErrorActionPreference = "Stop"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    Write-Host "On Windows, make sure Docker Desktop is running and the whale icon appears in the system tray." -ForegroundColor Yellow
    exit 1
}
Write-Host "Docker is running." -ForegroundColor Green

# Get AWS account ID
Write-Host "Retrieving AWS account ID..." -ForegroundColor Yellow
$AWS_ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text).Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($AWS_ACCOUNT_ID)) {
    Write-Host "Error: Failed to retrieve AWS account ID. Please check AWS credentials." -ForegroundColor Red
    Write-Host "Run 'aws configure' to set up your credentials." -ForegroundColor Yellow
    exit 1
}
Write-Host "AWS Account ID: $AWS_ACCOUNT_ID" -ForegroundColor Green
$ECR_REPOSITORY_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${Region}.amazonaws.com/${ECR_REPO_NAME}"

Write-Host ""
Write-Host "Step 1: Creating ECR repository (if it doesn't exist)..." -ForegroundColor Yellow
$ErrorActionPreference = "SilentlyContinue"
aws ecr describe-repositories --repository-names $ECR_REPO_NAME --region $Region 2>&1 | Out-Null
$ErrorActionPreference = "Stop"
if ($LASTEXITCODE -eq 0) {
    Write-Host "Repository already exists." -ForegroundColor Green
} else {
    Write-Host "Repository does not exist. Creating..." -ForegroundColor Yellow
    aws ecr create-repository --repository-name $ECR_REPO_NAME --region $Region --image-scanning-configuration scanOnPush=true
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error creating repository. Please check AWS credentials and permissions." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Step 2: Logging in to ECR..." -ForegroundColor Yellow
$ecrPassword = aws ecr get-login-password --region $Region
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to get ECR login password. Please check AWS credentials and permissions." -ForegroundColor Red
    exit 1
}
$ecrPassword | docker login --username AWS --password-stdin $ECR_REPOSITORY_URI
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to login to ECR. Please check Docker is running and network connection." -ForegroundColor Red
    exit 1
}
Write-Host "Successfully logged in to ECR." -ForegroundColor Green

Write-Host ""
Write-Host "Step 3: Building Docker image..." -ForegroundColor Yellow
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
$dockerfilePath = Join-Path (Join-Path $projectRoot "backend") "Dockerfile"

# Validate paths
if (-not (Test-Path $projectRoot)) {
    Write-Host "Error: Project root directory not found: $projectRoot" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $dockerfilePath)) {
    Write-Host "Error: Dockerfile not found: $dockerfilePath" -ForegroundColor Red
    Write-Host "Please ensure you're running this script from the repository root." -ForegroundColor Yellow
    exit 1
}

$originalLocation = Get-Location
try {
    Set-Location $projectRoot
    Write-Host "Building from: $projectRoot" -ForegroundColor Gray
    Write-Host "Using Dockerfile: $dockerfilePath" -ForegroundColor Gray
    docker build -t ${ECR_REPO_NAME}:latest -f backend/Dockerfile .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Docker build failed. Please check the Dockerfile and Docker is running." -ForegroundColor Red
        Set-Location $originalLocation
        exit 1
    }
    Write-Host "Docker image built successfully." -ForegroundColor Green
} catch {
    Write-Host "Error: Failed to build Docker image: $_" -ForegroundColor Red
    Set-Location $originalLocation
    exit 1
} finally {
    Set-Location $originalLocation
}

Write-Host ""
Write-Host "Step 4: Tagging image for ECR..." -ForegroundColor Yellow
# Verify the image exists before tagging
$ErrorActionPreference = "SilentlyContinue"
$imageExists = docker images "${ECR_REPO_NAME}:latest" --format "{{.Repository}}:{{.Tag}}" 2>&1
$ErrorActionPreference = "Stop"
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($imageExists)) {
    Write-Host "Error: Docker image '${ECR_REPO_NAME}:latest' not found. Build may have failed." -ForegroundColor Red
    exit 1
}

docker tag "${ECR_REPO_NAME}:latest" "${ECR_REPOSITORY_URI}:latest"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to tag Docker image." -ForegroundColor Red
    exit 1
}
Write-Host "Image tagged successfully." -ForegroundColor Green

Write-Host ""
Write-Host "Step 5: Pushing image to ECR..." -ForegroundColor Yellow
Write-Host "This may take a few minutes depending on image size..." -ForegroundColor Gray
docker push "${ECR_REPOSITORY_URI}:latest"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to push Docker image to ECR. Please check:" -ForegroundColor Red
    Write-Host "  - Network connection" -ForegroundColor Yellow
    Write-Host "  - AWS credentials and permissions" -ForegroundColor Yellow
    Write-Host "  - ECR repository exists and is accessible" -ForegroundColor Yellow
    exit 1
}
Write-Host "Image pushed successfully to ECR." -ForegroundColor Green

Write-Host ""
Write-Host "Step 6: Deploying to App Runner..." -ForegroundColor Yellow
Write-Host "Note: If the App Runner service doesn't exist, you'll need to create it manually in the AWS Console" -ForegroundColor Yellow
Write-Host "or use the AWS CLI command below:" -ForegroundColor Yellow
Write-Host ""
Write-Host "aws apprunner create-service --cli-input-json file://infrastructure/apprunner-service.json --region $Region" -ForegroundColor Cyan
Write-Host ""
Write-Host "For now, if the service exists, updating it..." -ForegroundColor Yellow

# Check if service exists
$serviceArn = "arn:aws:apprunner:${Region}:${AWS_ACCOUNT_ID}:service/${APP_RUNNER_SERVICE_NAME}"
$ErrorActionPreference = "SilentlyContinue"
aws apprunner describe-service --service-arn $serviceArn --region $Region 2>&1 | Out-Null
$ErrorActionPreference = "Stop"
if ($LASTEXITCODE -eq 0) {
    Write-Host "Service exists. Starting deployment..." -ForegroundColor Green
    aws apprunner start-deployment --service-arn $serviceArn --region $Region
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Deployment started successfully. Check AWS Console for status." -ForegroundColor Green
    } else {
        Write-Host "Warning: Failed to start deployment. Service may already be deploying." -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Yellow
    Write-Host "Service does not exist yet." -ForegroundColor Yellow
    Write-Host "Please create it manually in AWS Console:" -ForegroundColor Yellow
    Write-Host "1. Go to AWS App Runner Console" -ForegroundColor Cyan
    Write-Host "2. Click 'Create service'" -ForegroundColor Cyan
    Write-Host "3. Select 'Container registry' -> 'Amazon ECR'" -ForegroundColor Cyan
    Write-Host "4. Select repository: $ECR_REPO_NAME" -ForegroundColor Cyan
    Write-Host "5. Configure environment variables" -ForegroundColor Cyan
    Write-Host "6. Deploy" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or use the provided apprunner-service.json template" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Deployment Steps Complete!" -ForegroundColor Green
Write-Host "ECR Repository: $ECR_REPOSITORY_URI" -ForegroundColor Green
Write-Host "Image Tag: latest" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
$ErrorActionPreference = "SilentlyContinue"
aws apprunner describe-service --service-arn $serviceArn --region $Region 2>&1 | Out-Null
$ErrorActionPreference = "Stop"
if ($LASTEXITCODE -eq 0) {
    Write-Host "1. Go to AWS App Runner Console to monitor deployment" -ForegroundColor White
    Write-Host "2. Once deployed, copy the service URL" -ForegroundColor White
    Write-Host "3. Update Amplify environment variable VITE_API_BASE_URL" -ForegroundColor White
} else {
    Write-Host "1. Create App Runner service in AWS Console (see instructions above)" -ForegroundColor White
    Write-Host "2. Use ECR repository: $ECR_REPOSITORY_URI" -ForegroundColor White
    Write-Host "3. Once deployed, update Amplify environment variables" -ForegroundColor White
}
Write-Host "==========================================" -ForegroundColor Green

