# Kubernetes Manifests for HomeLab DBaaS

This directory contains Kubernetes manifests for deploying and managing the HomeLab Database-as-a-Service (DBaaS) application. These manifests define the necessary resources for the frontend, backend, RBAC, namespaces, ingress, and persistent storage.

## Overview of Manifests

1. **Namespace (`namespace.yaml`)**  
   - Defines two namespaces:
     - `databases`: For database deployments.
     - `dbaas-system`: For the DBaaS application components.

2. **RBAC (`rbac.yaml`)**  
   - Configures Role-Based Access Control (RBAC) for the backend service.
   - Includes:
     - A `ServiceAccount` for the backend.
     - A `ClusterRole` with permissions to manage Kubernetes resources like pods, services, secrets, and Helm releases.
     - A `ClusterRoleBinding` to bind the `ServiceAccount` to the `ClusterRole`.

3. **Ingress (`ingress.yaml`)**  
   - Configures an NGINX ingress for routing traffic to the frontend and backend services.
   - Features:
     - Host-based routing (`dbaas.local`).
     - Path-based routing for `/` (frontend) and `/api` (backend).

4. **Frontend Deployment (`frontend-deployment.yaml`)**  
   - Defines the deployment and service for the frontend React application.
   - Features:
     - Liveness and readiness probes for health checks.
     - Environment variable `REACT_APP_API_URL` for backend communication.

5. **Backend Deployment (`backend-deployment.yaml`)**  
   - Defines the deployment and service for the Flask backend application.
   - Features:
     - Persistent storage using a `PersistentVolumeClaim`.
     - Liveness and readiness probes for health checks.
     - RBAC integration via `ServiceAccount`.

6. **Persistent Storage (`backend-storage.yaml`)**  
   - Defines a `PersistentVolumeClaim` for the backend to store database metadata.

## Key Features

- **Namespace Isolation**: Separates application components (`dbaas-system`) from user databases (`databases`).
- **RBAC Security**: Ensures the backend has only the necessary permissions to manage resources.
- **Ingress Configuration**: Provides a single entry point for accessing the application.
- **Health Probes**: Ensures the availability and readiness of the frontend and backend services.
- **Persistent Storage**: Ensures data durability for backend operations.

These manifests are designed to work seamlessly with my home Kubernetes cluster for easy deployment.
