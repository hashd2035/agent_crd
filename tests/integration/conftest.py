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
def create_agent_resource(k8s_client):
    def _create_agent(name, image, namespace="default"):
        agent = {
            "apiVersion": "agents.example.com/v1",
            "kind": "AgentType",
            "metadata": {
                "name": name
            },
            "spec": {
                "agent": {
                    "image": image
                }
            }
        }
        k8s_client.create_namespaced_custom_object(
            group="agents.example.com",
            version="v1",
            namespace=namespace,
            plural="agenttypes",
            body=agent
        )
        # Simple wait for pod creation
        time.sleep(2)
        return agent
    return _create_agent

@pytest.fixture
def delete_agent_resource(k8s_client, k8s_core_client):
    def _delete_agent(name, namespace="default"):
         try:
            k8s_client.delete_namespaced_custom_object(
                group="agents.example.com",
                version="v1",
                name=name,
                namespace=namespace,
                plural="agenttypes",
            )
            # Wait for deletion to complete
            timeout = 10
            start_time = time.time()
            while True:
                try:
                     k8s_core_client.read_namespaced_pod(
                        name=f"{name}-pod",
                        namespace=namespace
                    )
                     time.sleep(1)
                     if time.time() - start_time > timeout:
                       raise Exception(f"Timeout while waiting for pod deletion")
                except client.exceptions.ApiException as e:
                    if e.status == 404:
                        break # resource not found
                    else:
                      raise
         except client.exceptions.ApiException as e:
            if e.status != 404:
                raise
    return _delete_agent