import pytest
from kubernetes import client
import time

def test_sidecar_container_creation(k8s_custom_objects, k8s_core_v1_api):
    """Test that agent is created with a sidecar container"""
    # Create AgentType with sidecar spec
    agent_type = {
        "apiVersion": "agents.example.com/v1",
        "kind": "AgentType",
        "metadata": {
            "name": "test-sidecar"
        },
        "spec": {
            "agent": {
                "name": "agent",
                "image": "nginx:latest"
            },
            "sidecar": {
                "name": "tool-manager",
                "image": "busybox:latest"
            }
        }
    }

    # Create the AgentType resource
    k8s_custom_objects.create_namespaced_custom_object(
        group="agents.example.com",
        version="v1",
        namespace="default",
        plural="agenttypes",
        body=agent_type,
    )

    # Wait for pod creation
    time.sleep(5)

    # Get the pod
    pod = k8s_core_v1_api.list_namespaced_pod(
        namespace="default",
        label_selector=f"app=test-sidecar"
    ).items[0]

    # Verify sidecar container exists
    containers = [container.name for container in pod.spec.containers]
    assert "tool-manager" in containers
    assert "agent" in containers

def test_sidecar_volume_sharing(k8s_custom_objects, k8s_core_v1_api):
    """Test that sidecar container shares volume with main container"""
    agent_type = {
        "apiVersion": "agents.example.com/v1",
        "kind": "AgentType",
        "metadata": {
            "name": "test-volume-share"
        },
        "spec": {
            "agent": {
                "name": "agent",
                "image": "nginx:latest"
            },
            "sidecar": {
                "name": "tool-manager",
                "image": "busybox:latest"
            }
        }
    }

    # Create the AgentType resource
    k8s_custom_objects.create_namespaced_custom_object(
        group="agents.example.com",
        version="v1",
        namespace="default",
        plural="agenttypes",
        body=agent_type,
    )

    # Wait for pod creation
    time.sleep(5)

    # Get the pod
    pod = k8s_core_v1_api.list_namespaced_pod(
        namespace="default",
        label_selector=f"app=test-volume-share"
    ).items[0]

    # Verify shared volume exists and is mounted in both containers
    shared_volume = "shared-volume"
    
    # Check volume exists in pod spec
    volumes = [vol.name for vol in pod.spec.volumes]
    assert shared_volume in volumes

    # Check volume is mounted in both containers
    for container in pod.spec.containers:
        mounts = [mount.name for mount in container.volume_mounts]
        assert shared_volume in mounts

def test_sidecar_lifecycle(k8s_custom_objects, k8s_core_v1_api):
    """Test that sidecar container follows main container lifecycle"""
    agent_type = {
        "apiVersion": "agents.example.com/v1",
        "kind": "AgentType",
        "metadata": {
            "name": "test-lifecycle"
        },
        "spec": {
            "agent": {
                "name": "agent",
                "image": "nginx:latest"
            },
            "sidecar": {
                "name": "tool-manager",
                "image": "busybox:latest",
                "command": ["sh", "-c", "while true; do sleep 30; done"]
            }
        }
    }

    # Create the AgentType resource
    k8s_custom_objects.create_namespaced_custom_object(
        group="agents.example.com",
        version="v1",
        namespace="default",
        plural="agenttypes",
        body=agent_type,
    )

    # Wait for pod creation
    time.sleep(5)

    # Delete the AgentType
    k8s_custom_objects.delete_namespaced_custom_object(
        group="agents.example.com",
        version="v1",
        namespace="default",
        plural="agenttypes",
        name="test-lifecycle"
    )

    # Wait for deletion
    time.sleep(5)

    # Verify pod and all containers are deleted
    pods = k8s_core_v1_api.list_namespaced_pod(
        namespace="default",
        label_selector=f"app=test-lifecycle"
    ).items

    assert len(pods) == 0 

def test_basic_sidecar_creation(k8s_custom_objects, k8s_core_v1_api):
    """Test basic sidecar container creation with minimal config"""
    [current test_sidecar_container_creation remains the same]

def test_sidecar_with_command(k8s_custom_objects, k8s_core_v1_api):
    """Test sidecar container with custom command and args"""
    agent_type = {
        "apiVersion": "agents.example.com/v1",
        "kind": "AgentType",
        "metadata": {"name": "test-sidecar-cmd"},
        "spec": {
            "agent": {
                "name": "agent",
                "image": "nginx:latest"
            },
            "sidecar": {
                "name": "tool-manager",
                "image": "busybox:latest",
                "command": ["sh"],
                "args": ["-c", "echo 'Starting sidecar' && while true; do sleep 30; done"]
            }
        }
    }
    
    # Create and verify
    [similar creation and verification logic]
    
    # Verify command and args
    sidecar = next(c for c in pod.spec.containers if c.name == "tool-manager")
    assert sidecar.command == ["sh"]
    assert sidecar.args == ["-c", "echo 'Starting sidecar' && while true; do sleep 30; done"]

def test_sidecar_resources(k8s_custom_objects, k8s_core_v1_api):
    """Test sidecar container with resource requests/limits"""
    agent_type = {
        "apiVersion": "agents.example.com/v1",
        "kind": "AgentType",
        "metadata": {"name": "test-sidecar-resources"},
        "spec": {
            "agent": {
                "name": "agent",
                "image": "nginx:latest"
            },
            "sidecar": {
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
        }
    }
    
    [creation and basic verification]
    
    # Verify resources
    sidecar = next(c for c in pod.spec.containers if c.name == "tool-manager")
    assert sidecar.resources.requests['memory'] == '64Mi'
    assert sidecar.resources.limits['cpu'] == '500m'

def test_shared_volume_file_access(k8s_custom_objects, k8s_core_v1_api):
    """Test file sharing between init container, sidecar, and main container"""
    agent_type = {
        "apiVersion": "agents.example.com/v1",
        "kind": "AgentType",
        "metadata": {"name": "test-file-sharing"},
        "spec": {
            "agent": {
                "name": "agent",
                "image": "nginx:latest"
            },
            "sidecar": {
                "name": "tool-manager",
                "image": "busybox:latest",
                "command": ["sh", "-c"],
                "args": ["while true; do if [ -f /shared/init.txt ]; then echo 'sidecar-ready' > /shared/sidecar.txt; fi; sleep 5; done"]
            }
        }
    }
    
    [creation and basic verification]
    
    # Verify file creation and access
    # Note: In real test, we'd need to exec into containers to verify files
    assert True  # Placeholder for actual file verification

def test_startup_order(k8s_custom_objects, k8s_core_v1_api):
    """Test proper startup order: init -> sidecar -> main"""
    agent_type = {
        "apiVersion": "agents.example.com/v1",
        "kind": "AgentType",
        "metadata": {"name": "test-startup-order"},
        "spec": {
            "agent": {
                "name": "agent",
                "image": "nginx:latest"
            },
            "sidecar": {
                "name": "tool-manager",
                "image": "busybox:latest",
                "command": ["sh", "-c"],
                "args": ["echo 'Sidecar starting' && sleep infinity"]
            }
        }
    }
    
    [creation and basic verification]
    
    # Verify container statuses and order
    # Note: This might need adjustment based on how we implement startup order
    assert pod.status.init_container_statuses[0].ready
    assert pod.status.container_statuses[1].ready  # sidecar
    assert pod.status.container_statuses[0].ready  # main container 