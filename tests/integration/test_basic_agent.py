import pytest
import kubernetes
from kubernetes import client, config
import time

def test_create_basic_agent(k8s_client):
    """
    Test Scenario 1: Should create a basic agent pod
    """
    # Create AgentType resource
    agent = {
        "apiVersion": "agents.example.com/v1",
        "kind": "AgentType",
        "metadata": {
            "name": "test-agent"
        },
        "spec": {
            "agent": {
                "image": "nginx:latest"
            }
        }
    }
    
    # Apply the AgentType
    k8s_client.create_namespaced_custom_object(
        group="agents.example.com",
        version="v1",
        namespace="default",
        plural="agenttypes",
        body=agent
    )
    
    # Wait for pod creation (simple wait)
    time.sleep(5)
    
    # Verify pod exists and is running
    v1 = client.CoreV1Api()
    pod = v1.read_namespaced_pod(
        name="test-agent-pod",
        namespace="default"
    )
    
    assert pod.metadata.labels['app'] == "test-agent"
    assert pod.status.phase in ['Running', 'Pending']
