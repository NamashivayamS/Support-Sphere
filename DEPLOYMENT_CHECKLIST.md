# Support Sphere - Deployment Checklist

Use this checklist to ensure successful deployment for your academic evaluation.

---

## 📋 Pre-Deployment Checklist

### System Requirements
- [ ] Docker Desktop installed and running
- [ ] Docker Compose installed (comes with Docker Desktop)
- [ ] kubectl installed (for Kubernetes deployment)
- [ ] Kubernetes cluster available (Docker Desktop K8s, Minikube, or cloud)
- [ ] Docker Hub account created (for Kubernetes deployment)
- [ ] Minimum 4GB RAM available
- [ ] Minimum 10GB disk space available

### Verify Installations
```bash
# Check Docker
docker --version
docker ps

# Check Docker Compose
docker-compose --version

# Check Kubernetes (if deploying to K8s)
kubectl version --client
kubectl cluster-info
```

---

## 🐳 Part 1: Docker Compose Deployment

### Step 1: Preparation
- [ ] Navigate to project root directory
- [ ] Verify `docker-compose.yml` exists
- [ ] Verify `backend/` directory exists with Dockerfile
- [ ] Verify `frontend/` directory exists with Dockerfile

### Step 2: Build and Deploy
```bash
# Build and start services
docker-compose up --build -d
```
- [ ] Command executes without errors
- [ ] Both services start successfully

### Step 3: Verification
```bash
# Check running containers
docker-compose ps
```
- [ ] `support-sphere-backend` is running
- [ ] `support-sphere-frontend` is running
- [ ] Both show status as "Up"

### Step 4: Test Access
- [ ] Frontend accessible: http://localhost:8080
- [ ] Backend accessible: http://localhost:5000
- [ ] Frontend loads without errors
- [ ] Backend returns response

### Step 5: Check Logs
```bash
# View all logs
docker-compose logs

# Check for errors
docker-compose logs | grep -i error
```
- [ ] No critical errors in backend logs
- [ ] No critical errors in frontend logs
- [ ] Database initialized successfully

### Step 6: Test Functionality
- [ ] Click "Access Application" button on frontend
- [ ] Can navigate to login page
- [ ] Backend API responds to requests

### Screenshots to Capture
- [ ] `docker-compose ps` output
- [ ] Frontend homepage (http://localhost:8080)
- [ ] Backend response (http://localhost:5000)
- [ ] `docker-compose logs` output

---

## ☸️ Part 2: Kubernetes Deployment

### Step 1: Prepare Images

#### Build Images
```bash
# Replace <username> with your Docker Hub username
docker build -t <username>/support-backend:v1 ./backend
docker build -t <username>/support-frontend:v1 ./frontend
```
- [ ] Backend image built successfully
- [ ] Frontend image built successfully
- [ ] No build errors

#### Verify Images
```bash
docker images | grep support
```
- [ ] `support-backend:v1` appears in list
- [ ] `support-frontend:v1` appears in list

### Step 2: Push to Docker Hub

#### Login
```bash
docker login
```
- [ ] Successfully logged in to Docker Hub

#### Push Images
```bash
docker push <username>/support-backend:v1
docker push <username>/support-frontend:v1
```
- [ ] Backend image pushed successfully
- [ ] Frontend image pushed successfully
- [ ] Images visible on Docker Hub website

### Step 3: Update Kubernetes YAML Files

#### Edit backend-deployment.yaml
```bash
# Open k8s/backend-deployment.yaml
# Replace: <your-dockerhub-username>/support-backend:v1
# With: <username>/support-backend:v1
```
- [ ] Image name updated in backend-deployment.yaml

#### Edit frontend-deployment.yaml
```bash
# Open k8s/frontend-deployment.yaml
# Replace: <your-dockerhub-username>/support-frontend:v1
# With: <username>/support-frontend:v1
```
- [ ] Image name updated in frontend-deployment.yaml

### Step 4: Verify Kubernetes Cluster

```bash
# Check cluster status
kubectl cluster-info

# Check nodes
kubectl get nodes
```
- [ ] Cluster is running
- [ ] At least one node is Ready

### Step 5: Deploy Backend

```bash
# Deploy backend
kubectl apply -f k8s/backend-deployment.yaml
```
- [ ] Deployment created successfully
- [ ] Service created successfully

#### Verify Backend
```bash
# Check deployment
kubectl get deployment backend-deployment

# Check pods
kubectl get pods -l tier=backend

# Check service
kubectl get service backend-service
```
- [ ] Deployment shows 1/1 READY
- [ ] Pod is in "Running" state
- [ ] Service is created (ClusterIP type)

### Step 6: Deploy Frontend

```bash
# Deploy frontend
kubectl apply -f k8s/frontend-deployment.yaml
```
- [ ] Deployment created successfully
- [ ] Service created successfully

#### Verify Frontend
```bash
# Check deployment
kubectl get deployment frontend-deployment

# Check pods
kubectl get pods -l tier=frontend

# Check service
kubectl get service frontend-service
```
- [ ] Deployment shows 3/3 READY
- [ ] All 3 pods are in "Running" state
- [ ] Service is created (NodePort type)
- [ ] NodePort is 30080

### Step 7: Verify All Resources

```bash
# View all resources
kubectl get all -l app=support-sphere
```
- [ ] 2 deployments (backend, frontend)
- [ ] 4 pods total (1 backend + 3 frontend)
- [ ] 2 services (backend-service, frontend-service)
- [ ] 2 replicasets
- [ ] All pods show "Running" status

### Step 8: Check Pod Health

```bash
# Describe backend pod
kubectl describe pod -l tier=backend

# Describe frontend pods
kubectl describe pod -l tier=frontend
```
- [ ] No error events
- [ ] Liveness probes passing
- [ ] Readiness probes passing
- [ ] Containers are ready

### Step 9: Access Application

#### For Docker Desktop Kubernetes:
- [ ] Access: http://localhost:30080
- [ ] Frontend loads successfully

#### For Minikube:
```bash
minikube ip
# Access: http://<minikube-ip>:30080
```
- [ ] Get Minikube IP
- [ ] Access application via IP:30080
- [ ] Frontend loads successfully

### Step 10: Test Service Communication

```bash
# Get a frontend pod name
kubectl get pods -l tier=frontend

# Test backend connectivity from frontend pod
kubectl exec -it <frontend-pod-name> -- wget -O- http://backend-service:5000
```
- [ ] Frontend can reach backend service
- [ ] Backend responds successfully

### Screenshots to Capture
- [ ] `kubectl get all -l app=support-sphere` output
- [ ] `kubectl get pods` output showing all pods running
- [ ] `kubectl get services` output
- [ ] Frontend homepage via NodePort
- [ ] `kubectl describe pod` output for one pod

---

## 🔄 Part 3: Self-Healing Demonstration

### Test 1: Delete Frontend Pod

```bash
# List frontend pods
kubectl get pods -l tier=frontend

# Copy one pod name
# Delete the pod
kubectl delete pod <frontend-pod-name>

# Immediately watch pods
kubectl get pods -l tier=frontend -w
```
- [ ] Pod deletion successful
- [ ] New pod automatically created
- [ ] New pod reaches "Running" state
- [ ] 3 replicas maintained

### Test 2: Delete Backend Pod

```bash
# List backend pods
kubectl get pods -l tier=backend

# Delete backend pod
kubectl delete pod <backend-pod-name>

# Watch recreation
kubectl get pods -l tier=backend -w
```
- [ ] Pod deletion successful
- [ ] New pod automatically created
- [ ] New pod reaches "Running" state
- [ ] 1 replica maintained

### Test 3: Verify Application Still Works

- [ ] Access application via NodePort
- [ ] Application loads successfully
- [ ] No downtime experienced

### Screenshots to Capture
- [ ] Before deletion: `kubectl get pods` output
- [ ] During recreation: `kubectl get pods -w` output
- [ ] After recreation: `kubectl get pods` output showing new pod
- [ ] Application still accessible

---

## 📊 Part 4: Monitoring and Logs

### View Logs

```bash
# Backend logs
kubectl logs -l tier=backend --tail=50

# Frontend logs
kubectl logs -l tier=frontend --tail=50

# Specific pod logs
kubectl logs <pod-name>
```
- [ ] Backend logs show no critical errors
- [ ] Frontend logs show no critical errors
- [ ] Application initialized successfully

### Resource Usage

```bash
# View pod resource usage (if metrics server installed)
kubectl top pods

# View node resource usage
kubectl top nodes
```
- [ ] Pods are within resource limits
- [ ] No resource exhaustion

### Screenshots to Capture
- [ ] `kubectl logs` output for backend
- [ ] `kubectl logs` output for frontend
- [ ] `kubectl top pods` output (if available)

---

## 🧪 Part 5: Scaling Test (Optional)

### Scale Frontend

```bash
# Scale to 5 replicas
kubectl scale deployment frontend-deployment --replicas=5

# Verify scaling
kubectl get pods -l tier=frontend
```
- [ ] Deployment scaled successfully
- [ ] 5 pods running

### Scale Back

```bash
# Scale back to 3
kubectl scale deployment frontend-deployment --replicas=3

# Verify
kubectl get pods -l tier=frontend
```
- [ ] Deployment scaled down
- [ ] 3 pods running
- [ ] Extra pods terminated

### Screenshots to Capture
- [ ] Scaled to 5 replicas
- [ ] Scaled back to 3 replicas

---

## 📸 Required Screenshots for Evaluation

### Docker Compose
1. [ ] `docker-compose ps` showing both services running
2. [ ] Frontend homepage (http://localhost:8080)
3. [ ] Backend response (http://localhost:5000)
4. [ ] `docker-compose logs` output

### Kubernetes
5. [ ] `kubectl get all -l app=support-sphere` showing all resources
6. [ ] `kubectl get pods` showing 4 pods (1 backend + 3 frontend)
7. [ ] `kubectl get services` showing both services
8. [ ] Frontend via NodePort (http://localhost:30080)
9. [ ] `kubectl describe deployment frontend-deployment` showing 3 replicas
10. [ ] `kubectl describe deployment backend-deployment` showing 1 replica

### Self-Healing
11. [ ] Before pod deletion
12. [ ] After pod deletion showing automatic recreation
13. [ ] Final state with all pods running

### Logs
14. [ ] Backend logs
15. [ ] Frontend logs

---

## ✅ Final Verification

### Architecture Checklist
- [ ] Microservices architecture implemented (frontend + backend)
- [ ] Services are independent and containerized
- [ ] Service-to-service communication via DNS
- [ ] No hardcoded localhost references

### Docker Checklist
- [ ] Backend Dockerfile exists and works
- [ ] Frontend Dockerfile exists and works
- [ ] Docker Compose configuration valid
- [ ] Both services run in Docker Compose
- [ ] Images tagged correctly for Docker Hub

### Kubernetes Checklist
- [ ] Backend deployment created (1 replica)
- [ ] Frontend deployment created (3 replicas)
- [ ] Backend service (ClusterIP) created
- [ ] Frontend service (NodePort) created
- [ ] All pods in "Running" state
- [ ] Health checks configured and passing
- [ ] Resource limits defined
- [ ] Self-healing works (pod recreation)

### Documentation Checklist
- [ ] DEPLOYMENT_GUIDE.md reviewed
- [ ] README-MICROSERVICES.md reviewed
- [ ] COMMANDS_REFERENCE.md available
- [ ] IMPLEMENTATION_SUMMARY.md reviewed

---

## 🐛 Troubleshooting

### If Docker Compose Fails

**Issue: Port already in use**
```bash
docker-compose down
# Or stop the running Flask app first
```

**Issue: Build fails**
```bash
# Check Dockerfile syntax
docker-compose config
# View detailed build logs
docker-compose up --build
```

### If Kubernetes Deployment Fails

**Issue: ImagePullBackOff**
```bash
# Verify image exists on Docker Hub
docker pull <username>/support-backend:v1
# Check image name in YAML
kubectl describe pod <pod-name>
```

**Issue: CrashLoopBackOff**
```bash
# Check logs
kubectl logs <pod-name>
kubectl logs <pod-name> --previous
# Check events
kubectl describe pod <pod-name>
```

**Issue: Pods stuck in Pending**
```bash
# Check node resources
kubectl describe nodes
# Check events
kubectl get events
```

---

## 📝 Evaluation Report Template

```
# Support Sphere - Microservices Deployment Report

## Student Information
- Name: [Your Name]
- Date: [Date]
- Project: Support Sphere Microservices Transformation

## Part 1: Docker Compose Deployment
- Status: ✅ Success / ❌ Failed
- Frontend URL: http://localhost:8080
- Backend URL: http://localhost:5000
- Screenshots: [Attached]
- Notes: [Any observations]

## Part 2: Kubernetes Deployment
- Status: ✅ Success / ❌ Failed
- Frontend Replicas: 3
- Backend Replicas: 1
- NodePort: 30080
- Access URL: http://localhost:30080
- Screenshots: [Attached]
- Notes: [Any observations]

## Part 3: Self-Healing Demonstration
- Status: ✅ Success / ❌ Failed
- Pod deleted: [Pod name]
- Recreation time: [Seconds]
- Final state: All pods running
- Screenshots: [Attached]
- Notes: [Any observations]

## Architecture Highlights
- Microservices: Frontend (Nginx) + Backend (Flask)
- Containerization: Docker
- Orchestration: Kubernetes
- High Availability: 3 frontend replicas
- Self-Healing: Automatic pod recreation
- Service Discovery: DNS-based
- Load Balancing: Across frontend replicas

## Challenges Faced
[Describe any challenges and how you resolved them]

## Conclusion
[Summary of successful implementation]
```

---

## 🎓 Submission Checklist

- [ ] All screenshots captured
- [ ] Evaluation report completed
- [ ] Code repository ready
- [ ] Docker images on Docker Hub
- [ ] Documentation reviewed
- [ ] All services tested and working
- [ ] Self-healing demonstrated
- [ ] Ready for presentation

---

**Good luck with your evaluation! 🚀**

**Estimated Time:**
- Docker Compose: 10-15 minutes
- Kubernetes: 20-30 minutes
- Self-Healing Demo: 5-10 minutes
- Total: 35-55 minutes
