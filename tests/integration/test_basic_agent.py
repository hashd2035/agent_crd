import pytest
from kubernetes import client
import time
import json


def test_create_basic_agent(k8s_core_client, create_agent_resource, delete_agent_resource):
    """
    Test Scenario 1: Should create a basic agent pod
    """
    agent_name = "test-agent-create"
    agent_image = "nginx:latest"

    # Create AgentType resource
    agent_data = create_agent_resource(name=agent_name, image=agent_image)

    # Verify pod exists and is running
    pod = k8s_core_client.read_namespaced_pod(
        name=f"{agent_name}-pod",
        namespace="default"
    )

    assert pod.metadata.labels['app'] == agent_name
    assert pod.status.phase in ['Running', 'Pending']
    assert pod.metadata.owner_references[0].kind == 'AgentType'
    assert pod.metadata.owner_references[0].name == agent_name

    # Cleanup
    delete_agent_resource(name=agent_name)

def test_delete_agent(k8s_core_client, create_agent_resource, delete_agent_resource):
    """
    Test Scenario 2: Should clean up resources when agent is deleted
    """
    agent_name = "test-agent-delete"
    agent_image = "nginx:latest"

    # Create AgentType resource
    create_agent_resource(name=agent_name, image=agent_image)

    # Verify pod exists
    pod = k8s_core_client.read_namespaced_pod(
        name=f"{agent_name}-pod",
        namespace="default"
    )
    assert pod is not None

    # Delete AgentType, this will also delete pod via garbage collection, and we wait in fixture
    delete_agent_resource(name=agent_name)
    # Verify pod is removed
    with pytest.raises(client.exceptions.ApiException, match="Not Found"):
        k8s_core_client.read_namespaced_pod(
            name=f"{agent_name}-pod",
            namespace="default"
        )
    
def test_invalid_configuration(k8s_core_client, create_agent_resource, delete_agent_resource):
    """
    Test Scenario 3: Should handle missing image properly
    """
    agent_name = "test-agent-invalid"
    
    with pytest.raises(client.exceptions.ApiException) as excinfo:
        create_agent_resource(name=agent_name, image=None)
    
    
    assert "Required value" in json.loads(excinfo.value.body)['message']
    
    # Verify no pod is created
    with pytest.raises(client.exceptions.ApiException, match="Not Found"):
      k8s_core_client.read_namespaced_pod(
        name=f"{agent_name}-pod",
        namespace="default"
    )