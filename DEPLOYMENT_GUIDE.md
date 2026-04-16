# Support Sphere - Microservices Deployment Guide

## 📁 Project Structure

```
support-sphere/
├── backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── app.py
│   ├── extensions.py
│   ├── models.py
│   ├── requirements.txt
│   ├── routes/
│   ├── utils/
│   ├── templates/
│   ├── static/
│   └── instance/
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── html/
│       └── index.html
├── k8s/
│   ├── backend-deployment.yaml
│   └── frontend-deployment.yaml
├── docker-compose.yml
└── DEPLOYMENT_GUIDE.md
```

---

## 🚀 Part 1: Docker Compose Deployment (Local Testing)

### Prerequisites
- Docker Desktop installed and running
- Docker Compose installed

### Step 1: Build and Run with Docker Compose

```bash
# Navigate to project root
cd support-sphere

# Build and start all services
docker-compose up --build -d

# Check running containers
docker-compose ps

# View logs
docker-compose logs -f

# View backend logs only
docker-compose logs -f backend

# View frontend logs only
docker-compose logs -f frontend
```

### Step 2: Access the Application

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:5000
- **Backend Health Check**: http://localhost:5000/

### Step 3: Test the Application

```bash
# Test backend connectivity
curl http://localhost:5000/

# Test frontend
curl http://localhost:8080/

# Test API proxy through frontend
curl http://localhost:8080/api/
```

### Step 4: Stop and Clean Up

```bash
# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

---

## 🐳 Part 2: Docker Hub Preparation

### Step 1: Login to Docker Hub

```bash
# Login to Docker Hub
docker login

# Enter your Docker Hub username and password
```

### Step 2: Build Images with Tags

```bash
# Build backend image
docker build -t <your-dockerhub-username>/support-backend:v1 ./backend

# Build frontend image
docker build -t <your-dockerhub-username>/support-frontend:v1 ./frontend

# Verify images
docker images | grep support
```

### Step 3: Push Images to Docker Hub

```bash
# Push backend image
docker push <your-dockerhub-username>/support-backend:v1

# Push frontend image
docker push <your-dockerhub-username>/support-frontend:v1
```

### Step 4: Verify on Docker Hub

Visit: https://hub.docker.com/repositories/<your-dockerhub-username>

---

## ☸️ Part 3: Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (Minikube, Docker Desktop K8s, or cloud provider)
- kubectl installed and configured

### Step 1: Verify Kubernetes Cluster

```bash
# Check cluster status
kubectl cluster-info

# Check nodes
kubectl get nodes

# Check current context
kubectl config current-context
```

### Step 2: Update Kubernetes YAML Files

**IMPORTANT**: Before deploying, update the image names in the YAML files:

Edit `k8s/backend-deployment.yaml`:
```yaml
image: <your-dockerhub-username>/support-backend:v1
```

Edit `k8s/frontend-deployment.yaml`:
```yaml
image: <your-dockerhub-username>/support-frontend:v1
```

### Step 3: Deploy Backend Service

```bash
# Deploy backend
kubectl apply -f k8s/backend-deployment.yaml

# Verify backend deployment
kubectl get deployments
kubectl get pods -l tier=backend
kubectl get services -l tier=backend

# Check backend logs
kubectl logs -l tier=backend
```

### Step 4: Deploy Frontend Service

```bash
# Deploy frontend
kubectl apply -f k8s/frontend-deployment.yaml

# Verify frontend deployment
kubectl get deployments
kubectl get pods -l tier=frontend
kubectl get services -l tier=frontend

# Check frontend logs
kubectl logs -l tier=frontend
```

### Step 5: Verify All Resources

```bash
# List all deployments
kubectl get deployments

# List all pods
kubectl get pods

# List all services
kubectl get services

# Get detailed information
kubectl get all -l app=support-sphere
```

### Step 6: Access the Application

#### For Minikube:
```bash
# Get Minikube IP
minikube ip

# Access application
# Frontend: http://<minikube-ip>:30080
```

#### For Docker Desktop Kubernetes:
```bash
# Access application
# Frontend: http://localhost:30080
```

#### For Cloud Providers (AWS, GCP, Azure):
```bash
# Get external IP
kubectl get service frontend-service

# Access using the external IP
```

---

## 🔄 Part 4: Demonstrate Self-Healing (Resiliency)

### Test 1: Delete a Frontend Pod

```bash
# List frontend pods
kubectl get pods -l tier=frontend

# Copy one pod name and delete it
kubectl delete pod <frontend-pod-name>

# Watch pods being recreated automatically
kubectl get pods -l tier=frontend -w

# Verify 3 replicas are maintained
kubectl get pods -l tier=frontend
```

### Test 2: Delete Backend Pod

```bash
# List backend pods
kubectl get pods -l tier=backend

# Delete backend pod
kubectl delete pod <backend-pod-name>

# Watch automatic recreation
kubectl get pods -l tier=backend -w
```

### Test 3: Scale Frontend Replicas

```bash
# Scale frontend to 5 replicas
kubectl scale deployment frontend-deployment --replicas=5

# Verify scaling
kubectl get pods -l tier=frontend

# Scale back to 3
kubectl scale deployment frontend-deployment --replicas=3
```

### Test 4: Simulate Pod Crash

```bash
# Get a pod name
kubectl get pods -l tier=frontend

# Execute into pod and kill the process
kubectl exec -it <pod-name> -- /bin/sh
# Inside pod: kill 1

# Exit and watch pod restart
kubectl get pods -l tier=frontend -w
```

---

## 📊 Part 5: Monitoring and Debugging

### View Logs

```bash
# All backend logs
kubectl logs -l tier=backend --tail=100

# All frontend logs
kubectl logs -l tier=frontend --tail=100

# Follow logs in real-time
kubectl logs -l tier=backend -f

# Logs from specific pod
kubectl logs <pod-name>
```

### Describe Resources

```bash
# Describe deployment
kubectl describe deployment backend-deployment
kubectl describe deployment frontend-deployment

# Describe pod
kubectl describe pod <pod-name>

# Describe service
kubectl describe service backend-service
kubectl describe service frontend-service
```

### Execute Commands in Pods

```bash
# Get shell access to backend pod
kubectl exec -it <backend-pod-name> -- /bin/bash

# Get shell access to frontend pod
kubectl exec -it <frontend-pod-name> -- /bin/sh

# Run single command
kubectl exec <pod-name> -- ls -la
```

### Port Forwarding (for testing)

```bash
# Forward backend port
kubectl port-forward service/backend-service 5000:5000

# Forward frontend port
kubectl port-forward service/frontend-service 8080:80

# Access via localhost
# Backend: http://localhost:5000
# Frontend: http://localhost:8080
```

---

## 🧹 Part 6: Cleanup

### Delete Kubernetes Resources

```bash
# Delete all resources
kubectl delete -f k8s/backend-deployment.yaml
kubectl delete -f k8s/frontend-deployment.yaml

# Verify deletion
kubectl get all -l app=support-sphere

# Delete namespace (if created)
kubectl delete namespace support-sphere
```

### Clean Docker Resources

```bash
# Stop Docker Compose
docker-compose down -v

# Remove images
docker rmi <your-dockerhub-username>/support-backend:v1
docker rmi <your-dockerhub-username>/support-frontend:v1

# Clean all unused resources
docker system prune -a
```

---

## 🐛 Common Issues and Fixes

### Issue 1: ImagePullBackOff

**Problem**: Kubernetes can't pull images from Docker Hub

**Solution**:
```bash
# Verify image exists on Docker Hub
docker pull <your-dockerhub-username>/support-backend:v1

# Check pod events
kubectl describe pod <pod-name>

# Ensure image name is correct in YAML files
```

### Issue 2: CrashLoopBackOff

**Problem**: Pod keeps crashing and restarting

**Solution**:
```bash
# Check pod logs
kubectl logs <pod-name>

# Check previous logs
kubectl logs <pod-name> --previous

# Describe pod for events
kubectl describe pod <pod-name>
```

### Issue 3: Service Not Accessible

**Problem**: Can't access frontend via NodePort

**Solution**:
```bash
# Verify service is running
kubectl get service frontend-service

# Check if pods are ready
kubectl get pods -l tier=frontend

# For Minikube, use minikube service
minikube service frontend-service

# Check firewall rules
```

### Issue 4: Backend Connection Failed

**Problem**: Frontend can't connect to backend

**Solution**:
```bash
# Verify backend service exists
kubectl get service backend-service

# Check backend pods are running
kubectl get pods -l tier=backend

# Test backend connectivity from frontend pod
kubectl exec -it <frontend-pod> -- wget -O- http://backend-service:5000
```

### Issue 5: Database Not Persisting

**Problem**: Data lost when pod restarts

**Solution**:
- For production, use PersistentVolume instead of emptyDir
- Current setup uses emptyDir for simplicity (data is ephemeral)

---

## 📝 Test Credentials

Once the application is running, use these credentials:

**Manager Account**:
- Email: manager@supportsphere.com
- Password: manager123

**Team Member Account**:
- Email: mike@supportsphere.com
- Password: team123

**Customer Account**:
- Email: john@example.com
- Password: customer123

---

## ✅ Verification Checklist

- [ ] Docker Compose runs successfully
- [ ] Both services accessible locally
- [ ] Images pushed to Docker Hub
- [ ] Kubernetes cluster is running
- [ ] Backend deployment created (1 replica)
- [ ] Frontend deployment created (3 replicas)
- [ ] Backend service (ClusterIP) created
- [ ] Frontend service (NodePort) created
- [ ] Application accessible via NodePort
- [ ] Pod deletion triggers automatic recreation
- [ ] All pods show "Running" status
- [ ] Logs show no critical errors

---

## 🎓 Academic Evaluation Points

This implementation demonstrates:

1. **Microservices Architecture**: Separation of frontend and backend
2. **Containerization**: Docker containers for both services
3. **Container Orchestration**: Kubernetes deployment
4. **Service Discovery**: Backend service accessible via DNS name
5. **Load Balancing**: Multiple frontend replicas
6. **Self-Healing**: Automatic pod recreation on failure
7. **Scalability**: Easy horizontal scaling with replicas
8. **Health Checks**: Liveness and readiness probes
9. **Resource Management**: CPU and memory limits
10. **Production Readiness**: Proper logging, monitoring, and error handling

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)

---

## 🤝 Support

For issues or questions:
1. Check the "Common Issues and Fixes" section
2. Review pod logs: `kubectl logs <pod-name>`
3. Describe resources: `kubectl describe <resource-type> <resource-name>`

---

**Good luck with your academic evaluation! 🎓**
