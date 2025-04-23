# HomeLab Database-as-a-Service (DBaaS)

This project provides a platform for creating and managing databases as a service on a home Kubernetes cluster. It is designed for local development and testing, enabling users to quickly deploy and manage common database applications.

## Key Features

- **Database Customization**: Users can create databases by specifying:
  - A unique name for the database.
  - The type of database (PostgreSQL, MySQL, MongoDB, Kafka).
  - Storage size requirements.
- **Automated Deployment**: The backend processes user requests and deploys databases using Helm charts.
- **Credential Management**: Automatically generates and returns credentials for:
  - Admin access.
  - Read-only access.
- **Monitoring Integration**: Provides a link to a Grafana dashboard for monitoring database status.
- **Namespace Isolation**: Separates application components and user databases for better organization and security.

## Technologies Used

- **Frontend**: React.js
  - Provides a user-friendly web interface for managing databases.
  - Communicates with the backend via REST APIs.
- **Backend**: Flask
  - Handles API requests and interacts with the Kubernetes cluster.
  - Uses the Kubernetes Python client for resource management.
- **Kubernetes**:
  - Manages database deployments, services, and persistent storage.
  - Uses Helm charts for templated deployments.
- **Helm**:
  - Simplifies the deployment of database applications.
  - Supports customization via values files.
- **Grafana**:
  - Provides monitoring and visualization for deployed databases.
- **NGINX Ingress**:
  - Routes traffic to the frontend and backend services.

## How It Works

1. **User Interaction**: Users interact with the web application to specify database details.
2. **Backend Processing**: The backend validates the request, generates credentials, and deploys the database using Helm.
3. **Database Deployment**: The database is deployed in the `databases` namespace, and credentials are stored in Kubernetes secrets.
4. **Monitoring**: A Grafana dashboard link is provided for monitoring the database.
