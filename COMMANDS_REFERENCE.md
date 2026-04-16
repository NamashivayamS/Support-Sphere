# Support Sphere - Commands Reference

Quick reference for all deployment and management commands.

---

## 🐳 Docker Commands

### Build Images
```bash
# Build backend image
docker build -t <username>/support-backend:v1 ./backend

# Build frontend image
docker build -t <username>/support-frontend:v1 ./frontend

# Build both with specific tags
docker build -t <username>/support-backend:v1 -t <username>/support-backend:latest ./backend
docker build -t <username>/support-frontend:v1 -t <username>/support-frontend:latest ./frontend
```

### Push to Docker Hub
```bash
# Login to Docker Hub
docker login

# Push images
docker push <username>/support-backend:v1
docker push <username>/support-frontend:v1

# Push all tags
docker push <username>/support-backend --all-tags
docker push <username>/support-frontend --all-tags
```

### Run Containers Manually
```bash
# Run backend
docker run -d -p 5000:5000 --name backend <username>/support-backend:v1

# Run frontend
docker run -d -p 8080:80 --name frontend <username>/support-frontend:v1

# Stop containers
docker stop backend frontend

# Remove containers
docker rm backend frontend
```

### Image Management
```bash
# List images
docker images

# Remove image
docker rmi <username>/support-backend:v1

# Remove all unused images
docker image prune -a

# View image details
docker inspect <username>/support-backend:v1
```

---

## 🐙 Docker Compose Commands

### Basic Operations
```bash
# Start services (build if needed)
docker-compose up --build -d

# Start without building
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop and remove images
docker-compose down --rmi all
```

### Monitoring
```bash
# View running services
docker-compose ps

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f backend
docker-compose logs -f frontend

# View last 100 lines
docker-compose logs --tail=100

# View service status
docker-compose top
```

### Service Management
```bash
# Restart services
docker-compose restart

# Restart specific service
docker-compose restart backend

# Stop specific service
docker-compose stop backend

# Start specific service
docker-compose start backend

# Scale service
docker-compose up -d --scale frontend=3
```

### Debugging
```bash
# Execute command in service
docker-compose exec backend bash
docker-compose exec frontend sh

# View service configuration
docker-compose config

# Validate compose file
docker-compose config --quiet
```

---

## ☸️ Kubernetes Commands

### Cluster Management
```bash
# Check cluster info
kubectl cluster-info

# View nodes
kubectl get nodes

# View cluster context
kubectl config current-context

# Switch context
kubectl config use-context <context-name>
```

### Deployment
```bash
# Apply deployment
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml

# Apply all files in directory
kubectl apply -f k8s/

# Delete deployment
kubectl delete -f k8s/backend-deployment.yaml
kubectl delete -f k8s/frontend-deployment.yaml

# Delete all resources with label
kubectl delete all -l app=support-sphere
```

### View Resources
```bash
# View all resources
kubectl get all

# View specific resources
kubectl get deployments
kubectl get pods
kubectl get services
kubectl get replicasets

# View with labels
kubectl get all -l app=support-sphere
kubectl get pods -l tier=backend
kubectl get pods -l tier=frontend

# View with wide output
kubectl get pods -o wide

# View in YAML format
kubectl get deployment backend-deployment -o yaml

# View in JSON format
kubectl get deployment backend-deployment -o json
```

### Pod Management
```bash
# List pods
kubectl get pods

# List pods with watch
kubectl get pods -w

# Describe pod
kubectl describe pod <pod-name>

# Delete pod
kubectl delete pod <pod-name>

# Force delete pod
kubectl delete pod <pod-name> --force --grace-period=0

# Get pod logs
kubectl logs <pod-name>

# Follow logs
kubectl logs -f <pod-name>

# View previous logs (if crashed)
kubectl logs <pod-name> --previous

# Logs from all pods with label
kubectl logs -l tier=backend
kubectl logs -l tier=frontend --tail=50
```

### Execute Commands in Pods
```bash
# Get shell access
kubectl exec -it <pod-name> -- /bin/bash
kubectl exec -it <pod-name> -- /bin/sh

# Run single command
kubectl exec <pod-name> -- ls -la
kubectl exec <pod-name> -- env
kubectl exec <pod-name> -- cat /etc/nginx/nginx.conf

# Test connectivity from pod
kubectl exec -it <frontend-pod> -- wget -O- http://backend-service:5000
kubectl exec -it <frontend-pod> -- curl http://backend-service:5000
```

### Scaling
```bash
# Scale deployment
kubectl scale deployment frontend-deployment --replicas=5
kubectl scale deployment backend-deployment --replicas=2

# Autoscale (requires metrics server)
kubectl autoscale deployment frontend-deployment --min=3 --max=10 --cpu-percent=80

# View autoscaler
kubectl get hpa
```

### Service Management
```bash
# List services
kubectl get services
kubectl get svc

# Describe service
kubectl describe service backend-service
kubectl describe service frontend-service

# View endpoints
kubectl get endpoints

# Port forwarding
kubectl port-forward service/backend-service 5000:5000
kubectl port-forward service/frontend-service 8080:80
kubectl port-forward pod/<pod-name> 5000:5000
```

### Debugging
```bash
# Describe resources
kubectl describe deployment <deployment-name>
kubectl describe pod <pod-name>
kubectl describe service <service-name>

# View events
kubectl get events
kubectl get events --sort-by=.metadata.creationTimestamp

# View resource usage (requires metrics server)
kubectl top nodes
kubectl top pods

# Check pod status
kubectl get pods --field-selector=status.phase=Running
kubectl get pods --field-selector=status.phase=Pending
kubectl get pods --field-selector=status.phase=Failed
```

### Rolling Updates
```bash
# Update image
kubectl set image deployment/backend-deployment backend=<username>/support-backend:v2

# View rollout status
kubectl rollout status deployment/backend-deployment

# View rollout history
kubectl rollout history deployment/backend-deployment

# Rollback to previous version
kubectl rollout undo deployment/backend-deployment

# Rollback to specific revision
kubectl rollout undo deployment/backend-deployment --to-revision=2

# Pause rollout
kubectl rollout pause deployment/backend-deployment

# Resume rollout
kubectl rollout resume deployment/backend-deployment
```

### Configuration
```bash
# Create configmap
kubectl create configmap app-config --from-file=config.yaml

# Create secret
kubectl create secret generic app-secret --from-literal=password=secret123

# View configmaps
kubectl get configmaps

# View secrets
kubectl get secrets

# Describe configmap
kubectl describe configmap app-config
```

---

## 🔍 Monitoring & Troubleshooting

### Health Checks
```bash
# Check pod readiness
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.conditions[?(@.type=="Ready")].status}{"\n"}{end}'

# Check pod restarts
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[0].restartCount}{"\n"}{end}'
```

### Resource Usage
```bash
# View resource requests/limits
kubectl describe nodes

# View pod resource usage (requires metrics server)
kubectl top pods
kubectl top pods --containers

# View node resource usage
kubectl top nodes
```

### Network Debugging
```bash
# Test DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup backend-service

# Test connectivity
kubectl run -it --rm debug --image=busybox --restart=Never -- wget -O- http://backend-service:5000

# Test with curl
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- curl http://backend-service:5000
```

### Common Issues
```bash
# ImagePullBackOff
kubectl describe pod <pod-name>  # Check image name and pull policy

# CrashLoopBackOff
kubectl logs <pod-name> --previous  # Check previous logs
kubectl describe pod <pod-name>  # Check events

# Pending pods
kubectl describe pod <pod-name>  # Check scheduling issues
kubectl get events  # Check cluster events

# Service not accessible
kubectl get endpoints  # Check if endpoints exist
kubectl describe service <service-name>  # Check service configuration
```

---

## 🧹 Cleanup Commands

### Docker Cleanup
```bash
# Stop all containers
docker stop $(docker ps -aq)

# Remove all containers
docker rm $(docker ps -aq)

# Remove all images
docker rmi $(docker images -q)

# Remove unused resources
docker system prune

# Remove everything (including volumes)
docker system prune -a --volumes

# Remove specific images
docker rmi <username>/support-backend:v1
docker rmi <username>/support-frontend:v1
```

### Docker Compose Cleanup
```bash
# Stop and remove containers
docker-compose down

# Remove containers and volumes
docker-compose down -v

# Remove containers, volumes, and images
docker-compose down -v --rmi all

# Remove orphan containers
docker-compose down --remove-orphans
```

### Kubernetes Cleanup
```bash
# Delete specific resources
kubectl delete deployment backend-deployment
kubectl delete deployment frontend-deployment
kubectl delete service backend-service
kubectl delete service frontend-service

# Delete by file
kubectl delete -f k8s/backend-deployment.yaml
kubectl delete -f k8s/frontend-deployment.yaml

# Delete all resources with label
kubectl delete all -l app=support-sphere

# Delete namespace (if created)
kubectl delete namespace support-sphere

# Force delete stuck resources
kubectl delete pod <pod-name> --force --grace-period=0
```

---

## 🚀 Quick Deployment Workflows

### Local Development (Docker Compose)
```bash
# 1. Start services
docker-compose up --build -d

# 2. View logs
docker-compose logs -f

# 3. Test application
curl http://localhost:8080
curl http://localhost:5000

# 4. Stop services
docker-compose down
```

### Production Deployment (Kubernetes)
```bash
# 1. Build images
docker build -t <username>/support-backend:v1 ./backend
docker build -t <username>/support-frontend:v1 ./frontend

# 2. Push to Docker Hub
docker login
docker push <username>/support-backend:v1
docker push <username>/support-frontend:v1

# 3. Update YAML files (replace <username>)
sed -i 's/<your-dockerhub-username>/<username>/g' k8s/*.yaml

# 4. Deploy to Kubernetes
kubectl apply -f k8s/

# 5. Verify deployment
kubectl get all -l app=support-sphere

# 6. Access application
kubectl get services
# Frontend: http://localhost:30080 (or minikube ip)
```

### Self-Healing Demo
```bash
# 1. List pods
kubectl get pods -l tier=frontend

# 2. Delete a pod
kubectl delete pod <frontend-pod-name>

# 3. Watch recreation
kubectl get pods -l tier=frontend -w

# 4. Verify 3 replicas maintained
kubectl get pods -l tier=frontend
```

---

## 📝 Notes

- Replace `<username>` with your Docker Hub username
- Replace `<pod-name>` with actual pod name from `kubectl get pods`
- Use `-n <namespace>` flag to specify namespace if not using default
- Add `--dry-run=client -o yaml` to preview changes without applying

---

**For detailed explanations, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**
