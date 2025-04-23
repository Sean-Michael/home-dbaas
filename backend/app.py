# flask/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import os
import base64
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import json
import os

app = Flask(__name__)
CORS(app)

try:
    config.load_incluster_config()
except config.ConfigException:
    config.load_kube_config()

core_v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()
custom_objects = client.CustomObjectsApi()

DATA_FILE = '/app/data/databases.json'
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

deployed_databases = {}
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        deployed_databases = json.load(f)

def save_databases():
    with open(DATA_FILE, 'w') as f:
        json.dump(deployed_databases, f)

@app.route('/api/databases', methods=['GET'])
def list_databases():
    """List all deployed databases"""
    return jsonify({"databases": list(deployed_databases.values())})

@app.route('/api/databases', methods=['POST'])
def create_database():
    """Create a new database instance"""
    data = request.json
    
    if not data or 'name' not in data or 'type' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    db_name = data['name'].lower()
    db_type = data['type'].lower()
    
    valid_types = ['postgres', 'mysql', 'mongodb', 'kafka']
    if db_type not in valid_types:
        return jsonify({"error": f"Database type must be one of: {', '.join(valid_types)}"}), 400
    
    deployment_id = str(uuid.uuid4())[:8]
    namespace = "databases"
    release_name = f"{db_name}-{deployment_id}"
    
    try:
        try:
            core_v1.read_namespace(name=namespace)
        except ApiException as e:
            if e.status == 404:
                namespace_manifest = client.V1Namespace(
                    metadata=client.V1ObjectMeta(name=namespace)
                )
                core_v1.create_namespace(body=namespace_manifest)
            else:
                raise
        
        if db_type == 'postgres':
            admin_password = os.urandom(8).hex()
            readonly_password = os.urandom(8).hex()
            
            secret_data = {
                "admin-password": base64.b64encode(admin_password.encode()).decode(),
                "readonly-password": base64.b64encode(readonly_password.encode()).decode()
            }
            
            secret = client.V1Secret(
                metadata=client.V1ObjectMeta(
                    name=f"{release_name}-creds",
                    namespace=namespace
                ),
                type="Opaque",
                data=secret_data
            )
            
            core_v1.create_namespaced_secret(namespace=namespace, body=secret)
            
            postgres_values = {
                "auth": {
                    "database": db_name,
                    "username": f"{db_name}_admin",
                    "password": admin_password,
                    "replicationUsername": f"{db_name}_ro",
                    "replicationPassword": readonly_password
                },
                "primary": {
                    "persistence": {
                        "size": data.get('storage', '1Gi')
                    },
                    "resources": {
                        "requests": {
                            "memory": "256Mi",
                            "cpu": "100m"
                        },
                        "limits": {
                            "memory": "512Mi",
                            "cpu": "500m"
                        }
                    }
                },
                "architecture": "standalone"
            }
            
            helm_release = {
                "apiVersion": "helm.fluxcd.io/v1",
                "kind": "HelmRelease",
                "metadata": {
                    "name": release_name,
                    "namespace": namespace
                },
                "spec": {
                    "releaseName": release_name,
                    "chart": {
                        "repository": "https://charts.bitnami.com/bitnami",
                        "name": "postgresql",
                        "version": "16.6.4"  
                    },
                    "values": postgres_values
                }
            }
            
            custom_objects.create_namespaced_custom_object(
                group="helm.fluxcd.io",
                version="v1",
                namespace=namespace,
                plural="helmreleases",
                body=helm_release
            )

            deployment = {
                "id": deployment_id,
                "name": db_name,
                "type": db_type,
                "release": release_name,
                "namespace": namespace,
                "credentials": {
                    "admin": {
                        "username": f"{db_name}_admin",
                        "password": admin_password
                    },
                    "readonly": {
                        "username": f"{db_name}_ro",
                        "password": readonly_password
                    }
                },
                "connection": f"{release_name}-postgresql.{namespace}.svc.cluster.local",
                "port": 5432,
                "dashboard": f"http://grafana.local/d/database-{deployment_id}"
            }
            
            deployed_databases[deployment_id] = deployment
            save_databases()
            return jsonify(deployment), 201
            
        # TODO: Add similar logic for MySQL, MongoDB, and Kafka
        else:
            return jsonify({"error": f"Support for {db_type} not yet implemented"}), 501
            
    except ApiException as e:
        return jsonify({"error": f"Kubernetes API error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Failed to deploy database: {str(e)}"}), 500

@app.route('/api/databases/<deployment_id>', methods=['DELETE'])
def delete_database(deployment_id):
    """Delete a database instance"""
    if deployment_id not in deployed_databases:
        return jsonify({"error": "Database not found"}), 404
    
    deployment = deployed_databases[deployment_id]
    release_name = deployment['release']
    namespace = deployment['namespace']
    
    try:
        custom_objects.delete_namespaced_custom_object(
            group="helm.fluxcd.io",
            version="v1",
            namespace=namespace,
            plural="helmreleases",
            name=release_name
        )
        
        core_v1.delete_namespaced_secret(
            name=f"{release_name}-creds",
            namespace=namespace
        )
        
        del deployed_databases[deployment_id]
        return jsonify({"message": f"Database {deployment_id} deleted successfully"})
        
    except ApiException as e:
        return jsonify({"error": f"Kubernetes API error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Failed to delete database: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)