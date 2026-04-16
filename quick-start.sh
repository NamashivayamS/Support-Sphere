#!/bin/bash

# Support Sphere - Quick Start Script
# This script automates the deployment process

set -e

echo "=========================================="
echo "Support Sphere - Quick Start Deployment"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi
print_success "Docker is installed"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi
print_success "Docker Compose is installed"

# Ask user for deployment type
echo ""
echo "Select deployment type:"
echo "1) Docker Compose (Local Testing)"
echo "2) Kubernetes (Production-like)"
echo "3) Both"
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo ""
        print_info "Starting Docker Compose deployment..."
        docker-compose up --build -d
        
        echo ""
        print_success "Deployment complete!"
        echo ""
        echo "Access the application:"
        echo "  Frontend: http://localhost:8080"
        echo "  Backend:  http://localhost:5000"
        echo ""
        echo "To view logs: docker-compose logs -f"
        echo "To stop: docker-compose down"
        ;;
    
    2)
        echo ""
        read -p "Enter your Docker Hub username: " dockerhub_username
        
        if [ -z "$dockerhub_username" ]; then
            print_error "Docker Hub username is required"
            exit 1
        fi
        
        print_info "Building and pushing images..."
        
        # Build images
        docker build -t $dockerhub_username/support-backend:v1 ./backend
        docker build -t $dockerhub_username/support-frontend:v1 ./frontend
        
        print_success "Images built successfully"
        
        # Ask if user wants to push to Docker Hub
        read -p "Push images to Docker Hub? (y/n): " push_choice
        
        if [ "$push_choice" = "y" ]; then
            docker login
            docker push $dockerhub_username/support-backend:v1
            docker push $dockerhub_username/support-frontend:v1
            print_success "Images pushed to Docker Hub"
        fi
        
        # Update Kubernetes YAML files
        print_info "Updating Kubernetes YAML files..."
        sed -i "s|<your-dockerhub-username>|$dockerhub_username|g" k8s/backend-deployment.yaml
        sed -i "s|<your-dockerhub-username>|$dockerhub_username|g" k8s/frontend-deployment.yaml
        
        # Deploy to Kubernetes
        print_info "Deploying to Kubernetes..."
        kubectl apply -f k8s/backend-deployment.yaml
        kubectl apply -f k8s/frontend-deployment.yaml
        
        print_success "Kubernetes deployment complete!"
        
        echo ""
        echo "Waiting for pods to be ready..."
        kubectl wait --for=condition=ready pod -l app=support-sphere --timeout=120s
        
        echo ""
        print_success "All pods are ready!"
        echo ""
        echo "Access the application:"
        echo "  kubectl get services"
        echo "  Frontend NodePort: 30080"
        echo ""
        echo "To view pods: kubectl get pods"
        echo "To view logs: kubectl logs -l app=support-sphere"
        ;;
    
    3)
        echo ""
        print_info "Starting Docker Compose deployment first..."
        docker-compose up --build -d
        
        print_success "Docker Compose deployment complete!"
        
        echo ""
        read -p "Enter your Docker Hub username for Kubernetes: " dockerhub_username
        
        if [ -z "$dockerhub_username" ]; then
            print_error "Docker Hub username is required"
            exit 1
        fi
        
        print_info "Building images for Kubernetes..."
        docker build -t $dockerhub_username/support-backend:v1 ./backend
        docker build -t $dockerhub_username/support-frontend:v1 ./frontend
        
        read -p "Push images to Docker Hub? (y/n): " push_choice
        
        if [ "$push_choice" = "y" ]; then
            docker login
            docker push $dockerhub_username/support-backend:v1
            docker push $dockerhub_username/support-frontend:v1
            print_success "Images pushed to Docker Hub"
        fi
        
        # Update and deploy to Kubernetes
        sed -i "s|<your-dockerhub-username>|$dockerhub_username|g" k8s/backend-deployment.yaml
        sed -i "s|<your-dockerhub-username>|$dockerhub_username|g" k8s/frontend-deployment.yaml
        
        kubectl apply -f k8s/backend-deployment.yaml
        kubectl apply -f k8s/frontend-deployment.yaml
        
        print_success "Both deployments complete!"
        
        echo ""
        echo "Docker Compose:"
        echo "  Frontend: http://localhost:8080"
        echo "  Backend:  http://localhost:5000"
        echo ""
        echo "Kubernetes:"
        echo "  Check services: kubectl get services"
        echo "  Frontend NodePort: 30080"
        ;;
    
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

echo ""
print_success "Deployment script completed!"
