import pytest
from kubernetes import client
import time

def test_sidecar_container_creation(k8s_core_client, create_agent_resource, delete_agent_resource):
    """Test basic sidecar container creation"""
    # Create AgentType with sidecar spec
    agent_data = create_agent_resource(
        name="test-sidecar",
        image="nginx:latest",
        sidecar={
            "name": "tool-manager",
            "image": "busybox:latest"
        }
    )

    # Wait for pod creation
    time.sleep(5)

    # Get the pod
    pod = k8s_core_client.list_namespaced_pod(
        namespace="default",
        label_selector=f"app=test-sidecar"
    ).items[0]

    # Verify sidecar container exists
    containers = [container.name for container in pod.spec.containers]
    assert "tool-manager" in containers
    assert "agent" in containers

    # Cleanup
    delete_agent_resource(name="test-sidecar") 

def test_sidecar_with_command(k8s_core_client, create_agent_resource, delete_agent_resource):
    """Test sidecar container with custom command and args"""
    agent_data = create_agent_resource(
        name="test-sidecar-cmd",
        image="nginx:latest",
        sidecar={
            "name": "tool-manager",
            "image": "busybox:latest",
            "command": ["sh"],
            "args": ["-c", "echo 'Starting sidecar' && while true; do sleep 30; done"]
        }
    )

    time.sleep(5)
    pod = k8s_core_client.read_namespaced_pod(
        name=f"test-sidecar-cmd-pod",
        namespace="default"
    )

    # Verify command and args
    sidecar = next(c for c in pod.spec.containers if c.name == "tool-manager")
    assert sidecar.command == ["sh"]
    assert sidecar.args == ["-c", "echo 'Starting sidecar' && while true; do sleep 30; done"]

    delete_agent_resource(name="test-sidecar-cmd") 

def test_sidecar_resources(k8s_core_client, create_agent_resource, delete_agent_resource):
    """Test sidecar container with resource requests/limits"""
    agent_data = create_agent_resource(
        name="test-sidecar-resources",
        image="nginx:latest",
        sidecar={
            "name": "tool-manager",
            "image": "busybox:latest",
            "resources": {
                "requests": {
                    "memory": "64Mi",
                    "cpu": "250m"
                },
                "limits": {
                    "memory": "128Mi",
                    "cpu": "500m"
                }
            }
        }
    )

    time.sleep(5)
    pod = k8s_core_client.read_namespaced_pod(
        name=f"test-sidecar-resources-pod",
        namespace="default"
    )

    # Verify resources
    sidecar = next(c for c in pod.spec.containers if c.name == "tool-manager")
    assert sidecar.resources.requests['memory'] == '64Mi'
    assert sidecar.resources.requests['cpu'] == '250m'
    assert sidecar.resources.limits['memory'] == '128Mi'
    assert sidecar.resources.limits['cpu'] == '500m'

    delete_agent_resource(name="test-sidecar-resources")

def test_shared_volume_file_access(k8s_core_client, create_agent_resource, delete_agent_resource):
    """Test file sharing between init container, sidecar, and main container"""
    agent_data = create_agent_resource(
        name="test-file-sharing",
        image="nginx:latest",
        sidecar={
            "name": "tool-manager",
            "image": "busybox:latest",
            "command": ["sh", "-c"],
            "args": ["while true; do if [ -f /shared/init.txt ]; then echo 'sidecar-ready' > /shared/sidecar.txt; fi; sleep 5; done"]
        }
    )

    time.sleep(5)
    pod = k8s_core_client.read_namespaced_pod(
        name=f"test-file-sharing-pod",
        namespace="default"
    )

    # Verify volume mounts
    sidecar = next(c for c in pod.spec.containers if c.name == "tool-manager")
    agent = next(c for c in pod.spec.containers if c.name == "agent")
    
    assert any(vm.name == "shared-volume" for vm in sidecar.volume_mounts)
    assert any(vm.name == "shared-volume" for vm in agent.volume_mounts)

    delete_agent_resource(name="test-file-sharing")

def test_startup_order(k8s_core_client, create_agent_resource, delete_agent_resource):
    """Test proper startup order: init -> sidecar -> main"""
    agent_data = create_agent_resource(
        name="test-startup-order",
        image="nginx:latest",
        sidecar={
            "name": "tool-manager",
            "image": "busybox:latest",
            "command": ["sh", "-c"],
            "args": ["echo 'Sidecar starting' && sleep infinity"]
        }
    )

    time.sleep(5)
    pod = k8s_core_client.read_namespaced_pod(
        name=f"test-startup-order-pod",
        namespace="default"
    )

    # Verify container statuses and order
    assert pod.status.init_container_statuses[0].ready
    assert pod.status.container_statuses[1].ready  # sidecar
    assert pod.status.container_statuses[0].ready  # main container

    delete_agent_resource(name="test-startup-order") 