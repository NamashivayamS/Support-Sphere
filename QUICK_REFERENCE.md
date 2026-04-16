# Support Sphere - Quick Reference Card

One-page reference for all essential commands.

---

## 🚀 Quick Start

### Docker Compose (Local)
```bash
docker-compose up --build -d          # Start
docker-compose logs -f                # View logs
docker-compose down                   # Stop
```
**Access:** http://localhost:8080

### Kubernetes (Production)
```bash
# 1. Build & Push
docker build -t <user>/support-backend:v1 ./backend
docker build -t <user>/support-frontend:v1 ./frontend
docker push <user>/support-backend:v1
docker push <user>/support-frontend:v1

# 2. Update YAML files with your username

# 3. Deploy
kubectl apply -f k8s/

# 4. Verify
kubectl get all -l app=support-sphere
```
**Access:** http://localhost:30080

---

## 📊 Essential Commands

### Docker Compose
| Command | Description |
|---------|-------------|
| `docker-compose up -d` | Start services |
| `docker-compose ps` | List services |
| `docker-compose logs -f` | Follow logs |
| `docker-compose down` | Stop services |
| `docker-compose down -v` | Stop + remove volumes |

### Kubernetes - View
| Command | Description |
|---------|-------------|
| `kubectl get pods` | List all pods |
| `kubectl get services` | List services |
| `kubectl get deployments` | List deployments |
| `kubectl get all -l app=support-sphere` | All resources |

### Kubernetes - Logs
| Command | Description |
|---------|-------------|
| `kubectl logs -l tier=backend` | Backend logs |
| `kubectl logs -l tier=frontend` | Frontend logs |
| `kubectl logs <pod-name>` | Specific pod |
| `kubectl logs -f <pod-name>` | Follow logs |

### Kubernetes - Debug
| Command | Description |
|---------|-------------|
| `kubectl describe pod <name>` | Pod details |
| `kubectl describe deployment <name>` | Deployment details |
| `kubectl exec -it <pod> -- /bin/sh` | Shell access |
| `kubectl get events` | Cluster events |

---

## 🔄 Self-Healing Demo

```bash
# 1. List pods
kubectl get pods -l tier=frontend

# 2. Delete one
kubectl delete pod <pod-name>

# 3. Watch recreation
kubectl get pods -l tier=frontend -w

# Result: Automatic recreation to maintain 3 replicas
```

---

## 📁 Project Structure

```
support-sphere/
├── backend/              # Flask backend
│   ├── Dockerfile
│   └── app.py
├── frontend/             # Nginx frontend
│   ├── Dockerfile
│   └── nginx.conf
├── k8s/                  # Kubernetes configs
│   ├── backend-deployment.yaml
│   └── frontend-deployment.yaml
└── docker-compose.yml    # Docker Compose config
```

---

## 🎯 Access Points

| Environment | Frontend | Backend |
|-------------|----------|---------|
| Docker Compose | http://localhost:8080 | http://localhost:5000 |
| Kubernetes | http://localhost:30080 | Internal only (ClusterIP) |

---

## 🔐 Test Credentials

| Role | Email | Password |
|------|-------|----------|
| Manager | manager@supportsphere.com | manager123 |
| Team | mike@supportsphere.com | team123 |
| Customer | john@example.com | customer123 |

---

## 🐛 Quick Troubleshooting

### Docker Compose Issues
```bash
# Port in use
docker-compose down

# View errors
docker-compose logs

# Rebuild
docker-compose up --build
```

### Kubernetes Issues
```bash
# ImagePullBackOff
kubectl describe pod <pod-name>

# CrashLoopBackOff
kubectl logs <pod-name>
kubectl logs <pod-name> --previous

# Pending pods
kubectl describe nodes
kubectl get events
```

---

## 📊 Verification Commands

### Check Everything is Running
```bash
# Docker Compose
docker-compose ps

# Kubernetes
kubectl get all -l app=support-sphere
kubectl get pods
```

### Test Connectivity
```bash
# Docker Compose
curl http://localhost:8080
curl http://localhost:5000

# Kubernetes
kubectl exec -it <frontend-pod> -- wget -O- http://backend-service:5000
```

---

## 🧹 Cleanup

### Docker Compose
```bash
docker-compose down -v
```

### Kubernetes
```bash
kubectl delete -f k8s/
```

### Complete Cleanup
```bash
docker-compose down -v
kubectl delete all -l app=support-sphere
docker system prune -a
```

---

## 📈 Scaling

```bash
# Scale frontend to 5
kubectl scale deployment frontend-deployment --replicas=5

# Scale back to 3
kubectl scale deployment frontend-deployment --replicas=3

# Verify
kubectl get pods -l tier=frontend
```

---

## 📚 Documentation Files

- **DEPLOYMENT_GUIDE.md** - Complete step-by-step guide
- **README-MICROSERVICES.md** - Architecture overview
- **COMMANDS_REFERENCE.md** - All commands detailed
- **DEPLOYMENT_CHECKLIST.md** - Evaluation checklist
- **IMPLEMENTATION_SUMMARY.md** - What was implemented
- **QUICK_REFERENCE.md** - This file

---

## ✅ Success Indicators

### Docker Compose
- ✅ Both services show "Up" in `docker-compose ps`
- ✅ Frontend accessible at port 8080
- ✅ Backend accessible at port 5000
- ✅ No errors in logs

### Kubernetes
- ✅ 4 pods running (1 backend + 3 frontend)
- ✅ All pods show "Running" status
- ✅ 2 services created (ClusterIP + NodePort)
- ✅ Frontend accessible at port 30080
- ✅ Pod deletion triggers automatic recreation

---

## 🎓 Key Features

- ✅ Microservices Architecture
- ✅ Docker Containerization
- ✅ Kubernetes Orchestration
- ✅ High Availability (3 replicas)
- ✅ Self-Healing
- ✅ Service Discovery
- ✅ Load Balancing
- ✅ Health Checks
- ✅ Resource Limits

---

**For detailed instructions, see DEPLOYMENT_GUIDE.md**
