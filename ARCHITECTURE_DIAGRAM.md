# Support Sphere - Architecture Diagrams

Visual representation of the microservices architecture.

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                            │
│                      (End Users)                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP Requests
                         │
         ┌───────────────▼────────────────┐
         │   Kubernetes NodePort          │
         │   Port: 30080                  │
         │   (External Access Point)      │
         └───────────────┬────────────────┘
                         │
                         │ Load Balanced
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
┌───▼────────┐   ┌──────▼──────┐   ┌────────▼───┐
│  Frontend  │   │  Frontend   │   │  Frontend  │
│   Pod 1    │   │   Pod 2     │   │   Pod 3    │
│  (Nginx)   │   │  (Nginx)    │   │  (Nginx)   │
│  Port: 80  │   │  Port: 80   │   │  Port: 80  │
└───┬────────┘   └──────┬──────┘   └────────┬───┘
    │                   │                    │
    │    Static Files   │   API Proxy        │
    │    /              │   /api/*           │
    │                   │                    │
    └───────────────────┼────────────────────┘
                        │
                        │ Internal Network
                        │ (ClusterIP)
                        │
            ┌───────────▼────────────┐
            │  Backend Service       │
            │  backend-service       │
            │  ClusterIP: 5000       │
            │  (Internal Only)       │
            └───────────┬────────────┘
                        │
                        │
                 ┌──────▼──────┐
                 │   Backend   │
                 │    Pod      │
                 │   (Flask)   │
                 │  Port: 5000 │
                 └──────┬──────┘
                        │
                        │
                 ┌──────▼──────┐
                 │   SQLite    │
                 │  Database   │
                 │  (Volume)   │
                 └─────────────┘
```

---

## 🔄 Request Flow

### Static Content Request
```
User Browser
    │
    │ GET http://localhost:30080/
    │
    ▼
NodePort Service (30080)
    │
    │ Load Balance
    │
    ▼
Frontend Pod (Nginx)
    │
    │ Serve static HTML
    │
    ▼
User Browser (index.html)
```

### API Request Flow
```
User Browser
    │
    │ GET http://localhost:30080/api/auth/login
    │
    ▼
NodePort Service (30080)
    │
    │ Load Balance
    │
    ▼
Frontend Pod (Nginx)
    │
    │ Proxy /api/* → http://backend-service:5000/
    │
    ▼
Backend Service (ClusterIP)
    │
    │ Route to backend pod
    │
    ▼
Backend Pod (Flask)
    │
    │ Process request
    │ Query database
    │
    ▼
SQLite Database
    │
    │ Return data
    │
    ▼
Backend Pod
    │
    │ JSON response
    │
    ▼
Frontend Pod (Nginx)
    │
    │ Proxy response
    │
    ▼
User Browser
```

---

## 🐳 Docker Compose Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Host                          │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │         support-sphere-network (Bridge)           │ │
│  │                                                   │ │
│  │  ┌─────────────────────┐  ┌──────────────────┐  │ │
│  │  │  Frontend Container │  │ Backend Container│  │ │
│  │  │                     │  │                  │  │ │
│  │  │  Nginx              │  │  Flask           │  │ │
│  │  │  Port: 80           │  │  Port: 5000      │  │ │
│  │  │                     │  │                  │  │ │
│  │  │  Proxy /api/*  ────────▶  API Endpoints   │  │ │
│  │  │                     │  │                  │  │ │
│  │  └─────────────────────┘  └────────┬─────────┘  │ │
│  │           │                         │            │ │
│  └───────────┼─────────────────────────┼────────────┘ │
│              │                         │              │
│              │                         │              │
│         Port 8080                 Port 5000           │
│              │                         │              │
│              │                         │              │
│              │                    ┌────▼────┐         │
│              │                    │ Volume  │         │
│              │                    │ backend-│         │
│              │                    │  data   │         │
│              │                    └─────────┘         │
└──────────────┼─────────────────────────────────────────┘
               │
               ▼
         Host Machine
      http://localhost:8080
      http://localhost:5000
```

---

## ☸️ Kubernetes Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                       │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                  Namespace: default                   │ │
│  │                                                       │ │
│  │  ┌─────────────────────────────────────────────────┐ │ │
│  │  │         Frontend Deployment                     │ │ │
│  │  │         Replicas: 3                             │ │ │
│  │  │                                                 │ │ │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐     │ │ │
│  │  │  │ Pod 1    │  │ Pod 2    │  │ Pod 3    │     │ │ │
│  │  │  │ Nginx    │  │ Nginx    │  │ Nginx    │     │ │ │
│  │  │  │ Port: 80 │  │ Port: 80 │  │ Port: 80 │     │ │ │
│  │  │  └──────────┘  └──────────┘  └──────────┘     │ │ │
│  │  │                                                 │ │ │
│  │  └────────────────────┬────────────────────────────┘ │ │
│  │                       │                              │ │
│  │           ┌───────────▼────────────┐                 │ │
│  │           │  Frontend Service      │                 │ │
│  │           │  Type: NodePort        │                 │ │
│  │           │  Port: 80              │                 │ │
│  │           │  NodePort: 30080       │                 │ │
│  │           └────────────────────────┘                 │ │
│  │                                                       │ │
│  │  ┌─────────────────────────────────────────────────┐ │ │
│  │  │         Backend Deployment                      │ │ │
│  │  │         Replicas: 1                             │ │ │
│  │  │                                                 │ │ │
│  │  │  ┌──────────────────────┐                      │ │ │
│  │  │  │ Pod                  │                      │ │ │
│  │  │  │ Flask                │                      │ │ │
│  │  │  │ Port: 5000           │                      │ │ │
│  │  │  │                      │                      │ │ │
│  │  │  │ ┌──────────────────┐ │                      │ │ │
│  │  │  │ │ Volume (emptyDir)│ │                      │ │ │
│  │  │  │ │ SQLite Database  │ │                      │ │ │
│  │  │  │ └──────────────────┘ │                      │ │ │
│  │  │  └──────────────────────┘                      │ │ │
│  │  │                                                 │ │ │
│  │  └────────────────────┬────────────────────────────┘ │ │
│  │                       │                              │ │
│  │           ┌───────────▼────────────┐                 │ │
│  │           │  Backend Service       │                 │ │
│  │           │  Type: ClusterIP       │                 │ │
│  │           │  Port: 5000            │                 │ │
│  │           │  (Internal Only)       │                 │ │
│  │           └────────────────────────┘                 │ │
│  │                                                       │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              │ NodePort 30080
                              │
                              ▼
                        External Access
                   http://localhost:30080
```

---

## 🔄 Self-Healing Process

```
┌─────────────────────────────────────────────────────────┐
│  Step 1: Normal Operation                              │
│                                                         │
│  Frontend Deployment (Desired: 3, Current: 3)          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Pod 1    │  │ Pod 2    │  │ Pod 3    │             │
│  │ Running  │  │ Running  │  │ Running  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
                         │
                         │ kubectl delete pod <pod-2>
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Step 2: Pod Deleted                                    │
│                                                         │
│  Frontend Deployment (Desired: 3, Current: 2)          │
│  ┌──────────┐                  ┌──────────┐            │
│  │ Pod 1    │     ❌ Deleted    │ Pod 3    │            │
│  │ Running  │                   │ Running  │            │
│  └──────────┘                   └──────────┘            │
│                                                         │
│  ⚠️ ReplicaSet detects mismatch!                        │
└─────────────────────────────────────────────────────────┘
                         │
                         │ Automatic Recreation
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Step 3: New Pod Creating                              │
│                                                         │
│  Frontend Deployment (Desired: 3, Current: 2+1)        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Pod 1    │  │ Pod 4    │  │ Pod 3    │             │
│  │ Running  │  │ Creating │  │ Running  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
                         │
                         │ Pod Starts
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Step 4: Restored                                       │
│                                                         │
│  Frontend Deployment (Desired: 3, Current: 3)          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Pod 1    │  │ Pod 4    │  │ Pod 3    │             │
│  │ Running  │  │ Running  │  │ Running  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
│                                                         │
│  ✅ Self-healing complete! (typically 5-10 seconds)     │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Service Discovery

```
┌─────────────────────────────────────────────────────────┐
│  Frontend Pod needs to call Backend                    │
│                                                         │
│  ┌──────────────────────┐                              │
│  │  Frontend Pod        │                              │
│  │                      │                              │
│  │  Request:            │                              │
│  │  http://backend-service:5000/api/users             │
│  │                      │                              │
│  └──────────┬───────────┘                              │
│             │                                           │
│             │ DNS Lookup                                │
│             ▼                                           │
│  ┌──────────────────────┐                              │
│  │  Kubernetes DNS      │                              │
│  │  (CoreDNS)           │                              │
│  │                      │                              │
│  │  backend-service     │                              │
│  │  → 10.96.100.50      │                              │
│  │  (ClusterIP)         │                              │
│  └──────────┬───────────┘                              │
│             │                                           │
│             │ Route to Service                          │
│             ▼                                           │
│  ┌──────────────────────┐                              │
│  │  Backend Service     │                              │
│  │  ClusterIP           │                              │
│  │  10.96.100.50:5000   │                              │
│  │                      │                              │
│  │  Selects backend pod │                              │
│  └──────────┬───────────┘                              │
│             │                                           │
│             │ Forward Request                           │
│             ▼                                           │
│  ┌──────────────────────┐                              │
│  │  Backend Pod         │                              │
│  │  Flask App           │                              │
│  │  10.244.0.15:5000    │                              │
│  │                      │                              │
│  │  Process & Respond   │                              │
│  └──────────────────────┘                              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔀 Load Balancing

```
┌─────────────────────────────────────────────────────────┐
│  Multiple Requests to Frontend Service                 │
│                                                         │
│  Request 1 ──┐                                          │
│  Request 2 ──┼──▶ Frontend Service (NodePort 30080)    │
│  Request 3 ──┘                                          │
│                         │                               │
│                         │ Round-Robin                   │
│                         │ Load Balancing                │
│                         │                               │
│         ┌───────────────┼───────────────┐               │
│         │               │               │               │
│         ▼               ▼               ▼               │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐         │
│  │ Pod 1    │    │ Pod 2    │    │ Pod 3    │         │
│  │ Nginx    │    │ Nginx    │    │ Nginx    │         │
│  │          │    │          │    │          │         │
│  │ Request 1│    │ Request 2│    │ Request 3│         │
│  └──────────┘    └──────────┘    └──────────┘         │
│                                                         │
│  ✅ Traffic distributed evenly across all pods         │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Container Layers

### Backend Container
```
┌─────────────────────────────────────┐
│  support-backend:v1                 │
├─────────────────────────────────────┤
│  Application Layer                  │
│  - app.py                           │
│  - routes/                          │
│  - models.py                        │
│  - templates/                       │
├─────────────────────────────────────┤
│  Dependencies Layer                 │
│  - Flask                            │
│  - SQLAlchemy                       │
│  - Flask-Login                      │
├─────────────────────────────────────┤
│  Python Runtime                     │
│  - Python 3.10                      │
├─────────────────────────────────────┤
│  Base OS                            │
│  - Debian (slim)                    │
└─────────────────────────────────────┘
```

### Frontend Container
```
┌─────────────────────────────────────┐
│  support-frontend:v1                │
├─────────────────────────────────────┤
│  Static Content                     │
│  - index.html                       │
│  - CSS/JS                           │
├─────────────────────────────────────┤
│  Nginx Configuration                │
│  - nginx.conf                       │
│  - Proxy rules                      │
├─────────────────────────────────────┤
│  Nginx Web Server                   │
│  - Nginx 1.x                        │
├─────────────────────────────────────┤
│  Base OS                            │
│  - Alpine Linux                     │
└─────────────────────────────────────┘
```

---

## 🎯 Deployment Comparison

### Monolithic (Before)
```
┌─────────────────────────────────────┐
│  Single Server                      │
│                                     │
│  ┌───────────────────────────────┐ │
│  │  Flask Application            │ │
│  │  - Frontend (templates)       │ │
│  │  - Backend (routes)           │ │
│  │  - Database (SQLite)          │ │
│  │  - Static files               │ │
│  └───────────────────────────────┘ │
│                                     │
│  ❌ Single point of failure         │
│  ❌ Hard to scale                   │
│  ❌ Tight coupling                  │
└─────────────────────────────────────┘
```

### Microservices (After)
```
┌─────────────────────────────────────────────────────────┐
│  Kubernetes Cluster                                     │
│                                                         │
│  ┌──────────────────┐      ┌──────────────────┐       │
│  │  Frontend        │      │  Backend         │       │
│  │  (3 replicas)    │      │  (1 replica)     │       │
│  │                  │      │                  │       │
│  │  - Nginx         │      │  - Flask API     │       │
│  │  - Static files  │◀────▶│  - Business      │       │
│  │  - API proxy     │      │    logic         │       │
│  └──────────────────┘      │  - Database      │       │
│                            └──────────────────┘       │
│                                                         │
│  ✅ High availability                                   │
│  ✅ Independent scaling                                 │
│  ✅ Loose coupling                                      │
│  ✅ Self-healing                                        │
└─────────────────────────────────────────────────────────┘
```

---

**For implementation details, see other documentation files.**
