# Support Sphere - Microservices Architecture

## 🎯 Overview

This project has been transformed from a monolithic Flask application into a **microservices-based, containerized, and Kubernetes-deployable system**.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer                        │
│                   (NodePort: 30080)                     │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼─────┐          ┌─────▼────┐          ┌──────────┐
    │ Frontend │          │ Frontend │          │ Frontend │
    │  Pod 1   │          │  Pod 2   │          │  Pod 3   │
    │ (Nginx)  │          │ (Nginx)  │          │ (Nginx)  │
    └────┬─────┘          └─────┬────┘          └──────┬───┘
         │                      │                       │
         └──────────────────────┼───────────────────────┘
                                │
                    ┌───────────▼────────────┐
                    │  Backend Service       │
                    │  (ClusterIP: 5000)     │
                    └───────────┬────────────┘
                                │
                         ┌──────▼──────┐
                         │   Backend   │
                         │    Pod      │
                         │   (Flask)   │
                         └─────────────┘
```

## 📦 Components

### Frontend Service
- **Technology**: Nginx
- **Replicas**: 3 (for high availability)
- **Exposure**: NodePort (30080)
- **Purpose**: Serves static content and proxies API requests

### Backend Service
- **Technology**: Flask (Python)
- **Replicas**: 1
- **Exposure**: ClusterIP (internal only)
- **Purpose**: REST API and business logic

## 🚀 Quick Start

### Option 1: Automated Deployment (Recommended)

**For Windows (PowerShell):**
```powershell
.\quick-start.ps1
```

**For Linux/Mac:**
```bash
chmod +x quick-start.sh
./quick-start.sh
```

### Option 2: Manual Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed step-by-step instructions.

## 📋 Prerequisites

- Docker Desktop (with Kubernetes enabled)
- kubectl CLI tool
- Docker Hub account (for Kubernetes deployment)
- 4GB+ RAM available
- 10GB+ disk space

## 🔧 Local Development with Docker Compose

```bash
# Start services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Access Points:**
- Frontend: http://localhost:8080
- Backend API: http://localhost:5000

## ☸️ Kubernetes Deployment

### 1. Build and Push Images

```bash
# Replace <username> with your Docker Hub username
docker build -t <username>/support-backend:v1 ./backend
docker build -t <username>/support-frontend:v1 ./frontend

docker push <username>/support-backend:v1
docker push <username>/support-frontend:v1
```

### 2. Update Kubernetes YAML Files

Edit `k8s/backend-deployment.yaml` and `k8s/frontend-deployment.yaml`:
```yaml
image: <username>/support-backend:v1
image: <username>/support-frontend:v1
```

### 3. Deploy to Kubernetes

```bash
# Deploy backend
kubectl apply -f k8s/backend-deployment.yaml

# Deploy frontend
kubectl apply -f k8s/frontend-deployment.yaml

# Verify deployment
kubectl get all -l app=support-sphere
```

### 4. Access Application

```bash
# Get service information
kubectl get services

# Access frontend
# For Docker Desktop: http://localhost:30080
# For Minikube: http://$(minikube ip):30080
```

## 🔄 Self-Healing Demonstration

```bash
# List pods
kubectl get pods

# Delete a frontend pod
kubectl delete pod <frontend-pod-name>

# Watch automatic recreation
kubectl get pods -w

# Verify 3 replicas are maintained
kubectl get pods -l tier=frontend
```

## 📊 Monitoring

```bash
# View all resources
kubectl get all -l app=support-sphere

# View logs
kubectl logs -l tier=backend
kubectl logs -l tier=frontend

# Describe resources
kubectl describe deployment backend-deployment
kubectl describe deployment frontend-deployment

# Check pod health
kubectl get pods -o wide
```

## 🧪 Testing

### Test Backend Connectivity
```bash
# Direct backend test
curl http://localhost:5000/

# Through Kubernetes service
kubectl port-forward service/backend-service 5000:5000
curl http://localhost:5000/
```

### Test Frontend
```bash
# Direct frontend test
curl http://localhost:8080/

# Check API proxy
curl http://localhost:8080/api/
```

### Test Service Communication
```bash
# Execute into frontend pod
kubectl exec -it <frontend-pod-name> -- /bin/sh

# Test backend connectivity from inside pod
wget -O- http://backend-service:5000/
```

## 📁 Project Structure

```
support-sphere/
├── backend/                    # Backend microservice
│   ├── Dockerfile             # Backend container definition
│   ├── .dockerignore          # Docker ignore rules
│   ├── app.py                 # Flask application
│   ├── extensions.py          # Flask extensions
│   ├── models.py              # Database models
│   ├── requirements.txt       # Python dependencies
│   ├── routes/                # API routes
│   ├── utils/                 # Utility functions
│   ├── templates/             # Jinja2 templates
│   ├── static/                # Static assets
│   └── instance/              # SQLite database
│
├── frontend/                   # Frontend microservice
│   ├── Dockerfile             # Frontend container definition
│   ├── nginx.conf             # Nginx configuration
│   └── html/                  # Static HTML files
│       └── index.html         # Landing page
│
├── k8s/                        # Kubernetes manifests
│   ├── backend-deployment.yaml    # Backend deployment & service
│   └── frontend-deployment.yaml   # Frontend deployment & service
│
├── docker-compose.yml          # Docker Compose configuration
├── DEPLOYMENT_GUIDE.md         # Detailed deployment guide
├── quick-start.sh              # Automated deployment (Linux/Mac)
├── quick-start.ps1             # Automated deployment (Windows)
└── README-MICROSERVICES.md     # This file
```

## 🔐 Default Credentials

**Manager:**
- Email: manager@supportsphere.com
- Password: manager123

**Team Member:**
- Email: mike@supportsphere.com
- Password: team123

**Customer:**
- Email: john@example.com
- Password: customer123

## 🛠️ Troubleshooting

### Pods Not Starting
```bash
# Check pod status
kubectl get pods

# View pod logs
kubectl logs <pod-name>

# Describe pod for events
kubectl describe pod <pod-name>
```

### ImagePullBackOff Error
```bash
# Verify image exists
docker pull <username>/support-backend:v1

# Check image name in YAML files
kubectl describe pod <pod-name>
```

### Service Not Accessible
```bash
# Check service status
kubectl get services

# Verify pods are running
kubectl get pods

# Check service endpoints
kubectl get endpoints
```

### Backend Connection Failed
```bash
# Test backend service
kubectl exec -it <frontend-pod> -- wget -O- http://backend-service:5000

# Check backend logs
kubectl logs -l tier=backend
```

## 📈 Scaling

### Scale Frontend
```bash
# Scale to 5 replicas
kubectl scale deployment frontend-deployment --replicas=5

# Scale back to 3
kubectl scale deployment frontend-deployment --replicas=3
```

### Scale Backend
```bash
# Scale to 2 replicas
kubectl scale deployment backend-deployment --replicas=2
```

## 🧹 Cleanup

### Docker Compose
```bash
docker-compose down -v
docker-compose down --rmi all
```

### Kubernetes
```bash
kubectl delete -f k8s/backend-deployment.yaml
kubectl delete -f k8s/frontend-deployment.yaml
```

### Complete Cleanup
```bash
# Stop all services
docker-compose down -v

# Delete Kubernetes resources
kubectl delete all -l app=support-sphere

# Remove Docker images
docker rmi <username>/support-backend:v1
docker rmi <username>/support-frontend:v1

# Clean Docker system
docker system prune -a
```

## 🎓 Academic Evaluation Checklist

- ✅ Microservices architecture (frontend + backend separation)
- ✅ Containerization with Docker
- ✅ Docker Compose for local testing
- ✅ Docker Hub image repository
- ✅ Kubernetes deployment manifests
- ✅ Frontend: 3 replicas (high availability)
- ✅ Backend: 1 replica (can be scaled)
- ✅ Service exposure (ClusterIP + NodePort)
- ✅ Self-healing capability (automatic pod recreation)
- ✅ Health checks (liveness + readiness probes)
- ✅ Resource limits (CPU + memory)
- ✅ Service discovery (DNS-based)
- ✅ Load balancing (across frontend replicas)
- ✅ Production-ready configuration

## 📚 Documentation

- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)

## 🤝 Contributing

This is an academic project demonstrating microservices architecture, containerization, and Kubernetes deployment.

## 📄 License

Educational use only.

---

**Built with ❤️ for academic evaluation**
