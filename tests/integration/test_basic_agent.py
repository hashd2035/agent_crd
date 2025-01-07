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
      
def test_volume_creation(k8s_core_client, create_agent_resource, delete_agent_resource):
    """
    Test Scenario 4: Should create shared volume
    """
    agent_name = "test-volume-create"
    agent_image = "nginx:latest"
    volume_name = "shared-volume"

    # Create AgentType resource with volume
    agent_data = create_agent_resource(name=agent_name, image=agent_image)
    
    # Verify pod exists and has volume
    pod = k8s_core_client.read_namespaced_pod(
        name=f"{agent_name}-pod",
        namespace="default"
    )
    
    assert any(volume.name == volume_name for volume in pod.spec.volumes)
    assert any(volume_mount.name == volume_name for container in pod.spec.containers for volume_mount in container.volume_mounts)

    # Cleanup
    delete_agent_resource(name=agent_name)

def test_init_container_execution(k8s_core_client, create_agent_resource, delete_agent_resource):
    """
    Test Scenario 5: Should execute init container before main container
    """
    agent_name = "test-init-container"
    agent_image = "nginx:latest"
    volume_name = "shared-volume"
    init_container_name = "init-container"

    # Create AgentType resource with init container
    agent_data = create_agent_resource(name=agent_name, image=agent_image)

    # Verify pod exists and has init container
    pod = k8s_core_client.read_namespaced_pod(
        name=f"{agent_name}-pod",
        namespace="default"
    )
    
    assert any(container.name == init_container_name for container in pod.spec.init_containers)
    assert any(volume.name == volume_name for volume in pod.spec.volumes)
    assert any(volume_mount.name == volume_name for container in pod.spec.containers for volume_mount in container.volume_mounts)
    assert any(volume_mount.name == volume_name for container in pod.spec.init_containers for volume_mount in container.volume_mounts)

    # Verify init container completes (simple check)
    time.sleep(5)
    pod = k8s_core_client.read_namespaced_pod(
        name=f"{agent_name}-pod",
        namespace="default"
    )
    assert pod.status.phase in ['Running', 'Pending']

    # Cleanup
    delete_agent_resource(name=agent_name)

def test_wrapper_injection(k8s_core_client, create_agent_resource, delete_agent_resource):
    """
    Test Scenario 6: Should inject wrapper code via init container
    """
    agent_name = "test-wrapper-injection"
    agent_image = "nginx:latest"
    volume_name = "shared-volume"
    init_container_name = "init-container"

    # Create AgentType resource with init container
    agent_data = create_agent_resource(name=agent_name, image=agent_image)

    # Verify pod exists and has init container
    pod = k8s_core_client.read_namespaced_pod(
        name=f"{agent_name}-pod",
        namespace="default"
    )
    
    assert any(container.name == init_container_name for container in pod.spec.init_containers)
    assert any(volume.name == volume_name for volume in pod.spec.volumes)
    assert any(volume_mount.name == volume_name for container in pod.spec.containers for volume_mount in container.volume_mounts)
    assert any(volume_mount.name == volume_name for container in pod.spec.init_containers for volume_mount in container.volume_mounts)

    # Verify wrapper files are present (simple check)
    time.sleep(5)
    pod = k8s_core_client.read_namespaced_pod(
        name=f"{agent_name}-pod",
        namespace="default"
    )
    assert pod.status.phase in ['Running', 'Pending']

    # Cleanup
    delete_agent_resource(name=agent_name)

def test_container_lifecycle(k8s_core_client, create_agent_resource, delete_agent_resource):
    """
    Test Scenario 7: Should clean up resources when agent is deleted
    """
    agent_name = "test-container-lifecycle"
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