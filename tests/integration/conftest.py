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

# In conftest.py

@pytest.fixture
def create_agent_resource(k8s_client, delete_agent_resource):
    def _create_agent(name, image, sidecar=None, environment=None):
        # First try to delete the resource if it exists
        delete_agent_resource(name=name, namespace="default")
        
        # Create the agent spec
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
        
        # Add sidecar configuration if provided
        if sidecar:
            # Ensure sidecar is added at the spec level, not under agent
            agent["spec"]["sidecar"] = sidecar
        
        # Add environment configuration if provided
        if environment:
            agent["spec"]["agent"]["environment"] = environment
        
        print(f"Creating AgentType with spec: {agent}")  # Debug output
        
        try:
            # Create the custom resource
            response = k8s_client.create_namespaced_custom_object(
                group="agents.example.com",
                version="v1",
                namespace="default",
                plural="agenttypes",
                body=agent
            )
            print(f"Created AgentType response: {response}")  # Debug output
            time.sleep(5)  # Wait for operator to process
            return agent
        except Exception as e:
            print(f"Failed to create agent: {str(e)}")
            raise
    
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
                    pods = k8s_core_client.list_namespaced_pod(
                       namespace=namespace,
                       label_selector=f"app={name}"
                    ).items

                    if not pods:
                        return
                    time.sleep(retry_interval)
                except client.exceptions.ApiException as e:
                    if e.status == 404:  # Pod is gone
                        return
                    raise
            # Wait a bit longer for pod termination
            time.sleep(10)
            #Check if the pod is still there (not necessary)
            pods = k8s_core_client.list_namespaced_pod(
                        namespace=namespace,
                        label_selector=f"app={name}"
                    ).items
            if pods:
              raise Exception("Timeout while waiting for pod deletion")

        except client.exceptions.ApiException as e:
            if e.status != 404:  # Ignore 404 errors
                raise

    return _delete_agent