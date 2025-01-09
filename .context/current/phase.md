# Project Phases

---
Legend:
✅ Done
🔄 In Progress
⏳ Not Started

## Phase 1 - MVP
Goal: Basic agent with init container and sidecar setup

### Features
1. Basic Agent Container
   - ✅ Container creation with specified image
   - ✅ Basic lifecycle management
   - ✅ Owner references

2. Init Container
   - ✅ Basic init container setup
   - ✅ Shared volume mounting
   - ✅ Simple wrapper injection

3. Sidecar Container
   - ⏳ Basic sidecar container setup
   - ⏳ Volume sharing with main container
   - ⏳ Basic lifecycle management

### CRD Structure for MVP
```yaml
spec:
  agent:
    image: nginx:latest
    name: agent
  sidecar:
    image: sidecar-image:latest
    name: tool-manager
```

## Phase 2 - Environment & Tool Management
1. Enhanced Environment Setup
   - 🔄 Environment variable injection
   - ⏳ SDK installation support
   - ⏳ Glue code injection
   - ⏳ Configurable init container

2. Tool Management
   - ⏳ Tool discovery via registry
   - ⏳ Tool installation in sidecar
   - ⏳ Inter-container communication

## Phase 3 - Production Features
1. Memory & API Management
   - ⏳ Memory management for all containers
   - ⏳ API integration via sidecar
   - ⏳ API proxying

2. Security & Monitoring
   - ⏳ Security features in sidecar
   - ⏳ Monitoring integration
   - ⏳ Production-grade logging

## Phase 4 - Advanced Features
1. Advanced Container Management
   - ⏳ Container lifecycle hooks
   - ⏳ Health checks
   - ⏳ Resource quotas

2. Advanced Tool Integration
   - ⏳ Version management
   - ⏳ Dependency resolution
   - ⏳ Tool updates

3. Advanced Security
   - ⏳ RBAC integration
   - ⏳ Network policies
   - ⏳ Secret management
