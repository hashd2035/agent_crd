import pytest
from kubernetes import client, config
import time

@pytest.fixture
def k8s_client():
    # Load kube config
    config.load_kube_config()
    return client.CustomObjectsApi()

@pytest.fixture
def k8s_core_client():
    # Load kube config
    config.load_kube_config()
    return client.CoreV1Api()


@pytest.fixture
def create_agent_resource(k8s_client, delete_agent_resource):
    def _create_agent(name, image, environment=None, sidecar=None):
        # First try to delete the resource if it exists
        delete_agent_resource(name=name, namespace="default")
        
        agent = {
            "apiVersion": "agents.example.com/v1",
            "kind": "AgentType",
            "metadata": {"name": name},
            "spec": {
                "agent": {
                    "name": "agent",
                    "image": image
                }
            }
        }
        
        # Add environment configuration if provided
        if environment:
            agent["spec"]["agent"]["environment"] = environment
        
        # Add sidecar if specified
        if sidecar:
            agent["spec"]["sidecar"] = sidecar
        
        k8s_client.create_namespaced_custom_object(
            group="agents.example.com",
            version="v1",
            namespace="default",
            plural="agenttypes",
            body=agent
        )
        time.sleep(5)  # Increased wait time
        return agent
    return _create_agent

@pytest.fixture
def delete_agent_resource(k8s_core_client, k8s_client):
    def _delete_agent(name, namespace="default"):
        try:
            # Delete the AgentType resource
            k8s_client.delete_namespaced_custom_object(
                group="agents.example.com",
                version="v1",
                namespace=namespace,
                plural="agenttypes",
                name=name
            )
            
            # Wait for pod deletion with a more robust check
            max_retries = 30
            retry_interval = 1
            for _ in range(max_retries):
                try:
                    k8s_core_client.read_namespaced_pod(
                        name=f"{name}-pod",
                        namespace=namespace
                    )
                    time.sleep(retry_interval)
                except client.exceptions.ApiException as e:
                    if e.status == 404:  # Pod is gone
                        return
                    raise
            
            raise Exception("Timeout while waiting for pod deletion")
            
        except client.exceptions.ApiException as e:
            if e.status != 404:  # Ignore 404 errors
                raise

    return _delete_agent