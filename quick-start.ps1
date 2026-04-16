# Support Sphere - Quick Start Script (PowerShell)
# This script automates the deployment process for Windows

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Support Sphere - Quick Start Deployment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

function Print-Success {
    param($Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Print-Error {
    param($Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Print-Info {
    param($Message)
    Write-Host "ℹ $Message" -ForegroundColor Yellow
}

# Check if Docker is installed
try {
    docker --version | Out-Null
    Print-Success "Docker is installed"
} catch {
    Print-Error "Docker is not installed. Please install Docker Desktop first."
    exit 1
}

# Check if Docker Compose is installed
try {
    docker-compose --version | Out-Null
    Print-Success "Docker Compose is installed"
} catch {
    Print-Error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
}

# Ask user for deployment type
Write-Host ""
Write-Host "Select deployment type:"
Write-Host "1) Docker Compose (Local Testing)"
Write-Host "2) Kubernetes (Production-like)"
Write-Host "3) Both"
$choice = Read-Host "Enter choice [1-3]"

switch ($choice) {
    "1" {
        Write-Host ""
        Print-Info "Starting Docker Compose deployment..."
        docker-compose up --build -d
        
        Write-Host ""
        Print-Success "Deployment complete!"
        Write-Host ""
        Write-Host "Access the application:"
        Write-Host "  Frontend: http://localhost:8080"
        Write-Host "  Backend:  http://localhost:5000"
        Write-Host ""
        Write-Host "To view logs: docker-compose logs -f"
        Write-Host "To stop: docker-compose down"
    }
    
    "2" {
        Write-Host ""
        $dockerhubUsername = Read-Host "Enter your Docker Hub username"
        
        if ([string]::IsNullOrWhiteSpace($dockerhubUsername)) {
            Print-Error "Docker Hub username is required"
            exit 1
        }
        
        Print-Info "Building and pushing images..."
        
        # Build images
        docker build -t "$dockerhubUsername/support-backend:v1" ./backend
        docker build -t "$dockerhubUsername/support-frontend:v1" ./frontend
        
        Print-Success "Images built successfully"
        
        # Ask if user wants to push to Docker Hub
        $pushChoice = Read-Host "Push images to Docker Hub? (y/n)"
        
        if ($pushChoice -eq "y") {
            docker login
            docker push "$dockerhubUsername/support-backend:v1"
            docker push "$dockerhubUsername/support-frontend:v1"
            Print-Success "Images pushed to Docker Hub"
        }
        
        # Update Kubernetes YAML files
        Print-Info "Updating Kubernetes YAML files..."
        (Get-Content k8s/backend-deployment.yaml) -replace '<your-dockerhub-username>', $dockerhubUsername | Set-Content k8s/backend-deployment.yaml
        (Get-Content k8s/frontend-deployment.yaml) -replace '<your-dockerhub-username>', $dockerhubUsername | Set-Content k8s/frontend-deployment.yaml
        
        # Deploy to Kubernetes
        Print-Info "Deploying to Kubernetes..."
        kubectl apply -f k8s/backend-deployment.yaml
        kubectl apply -f k8s/frontend-deployment.yaml
        
        Print-Success "Kubernetes deployment complete!"
        
        Write-Host ""
        Write-Host "Waiting for pods to be ready..."
        kubectl wait --for=condition=ready pod -l app=support-sphere --timeout=120s
        
        Write-Host ""
        Print-Success "All pods are ready!"
        Write-Host ""
        Write-Host "Access the application:"
        Write-Host "  kubectl get services"
        Write-Host "  Frontend NodePort: 30080"
        Write-Host ""
        Write-Host "To view pods: kubectl get pods"
        Write-Host "To view logs: kubectl logs -l app=support-sphere"
    }
    
    "3" {
        Write-Host ""
        Print-Info "Starting Docker Compose deployment first..."
        docker-compose up --build -d
        
        Print-Success "Docker Compose deployment complete!"
        
        Write-Host ""
        $dockerhubUsername = Read-Host "Enter your Docker Hub username for Kubernetes"
        
        if ([string]::IsNullOrWhiteSpace($dockerhubUsername)) {
            Print-Error "Docker Hub username is required"
            exit 1
        }
        
        Print-Info "Building images for Kubernetes..."
        docker build -t "$dockerhubUsername/support-backend:v1" ./backend
        docker build -t "$dockerhubUsername/support-frontend:v1" ./frontend
        
        $pushChoice = Read-Host "Push images to Docker Hub? (y/n)"
        
        if ($pushChoice -eq "y") {
            docker login
            docker push "$dockerhubUsername/support-backend:v1"
            docker push "$dockerhubUsername/support-frontend:v1"
            Print-Success "Images pushed to Docker Hub"
        }
        
        # Update and deploy to Kubernetes
        (Get-Content k8s/backend-deployment.yaml) -replace '<your-dockerhub-username>', $dockerhubUsername | Set-Content k8s/backend-deployment.yaml
        (Get-Content k8s/frontend-deployment.yaml) -replace '<your-dockerhub-username>', $dockerhubUsername | Set-Content k8s/frontend-deployment.yaml
        
        kubectl apply -f k8s/backend-deployment.yaml
        kubectl apply -f k8s/frontend-deployment.yaml
        
        Print-Success "Both deployments complete!"
        
        Write-Host ""
        Write-Host "Docker Compose:"
        Write-Host "  Frontend: http://localhost:8080"
        Write-Host "  Backend:  http://localhost:5000"
        Write-Host ""
        Write-Host "Kubernetes:"
        Write-Host "  Check services: kubectl get services"
        Write-Host "  Frontend NodePort: 30080"
    }
    
    default {
        Print-Error "Invalid choice"
        exit 1
    }
}

Write-Host ""
Print-Success "Deployment script completed!"
