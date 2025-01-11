import pytest
from kubernetes import client
import time

# In tests/integration/test_sidecar_container.py

def test_sidecar_container_creation(k8s_core_client, create_agent_resource, delete_agent_resource):
    """Test basic sidecar container creation"""
    agent_name = "test-sidecar"
    # Create AgentType with sidecar spec
    agent_data = create_agent_resource(
        name=agent_name,
        image="nginx:latest",
        sidecar={
            "name": "tool-manager",
            "image": "busybox:latest"
        }
    )

    # Wait for pod creation
    time.sleep(5)

    # Get the pod
    pod = k8s_core_client.read_namespaced_pod(
       name=f"{agent_name}-pod",
       namespace="default"
    )

    # Debug output
    print(f"Pod spec: {pod.spec}")
    print(f"Container names: {[c.name for c in pod.spec.containers]}")

    # Verify sidecar container exists
    containers = [container.name for container in pod.spec.containers]
    assert "tool-manager" in containers
    assert "agent" in containers  # Main container should also exist
    # Cleanup
    delete_agent_resource(name=agent_name)

def test_sidecar_with_command(k8s_core_client, create_agent_resource, delete_agent_resource):
    """Test sidecar container with custom command and args"""
    agent_name = "test-sidecar-cmd"
    agent_data = create_agent_resource(
        name=agent_name,
        image="nginx:latest",
        sidecar={
            "name": "tool-manager",
            "image": "busybox:latest",
            "command": ["sh"],
            "args": ["-c", "echo 'Starting sidecar'"]
        }
    )

    # Allow more time for pod to be fully created
    time.sleep(10)

    # Get pod
    pod = k8s_core_client.read_namespaced_pod(
        name=f"{agent_name}-pod",
        namespace="default"
    )

    # Debug output
    print(f"Pod containers: {[c.name for c in pod.spec.containers]}")

    # Find sidecar container
    sidecar = next(c for c in pod.spec.containers if c.name == "tool-manager")
    
    # Verify command and args
    assert sidecar.command == ["sh"]
    assert sidecar.args == ["-c", "echo 'Starting sidecar'"]
    delete_agent_resource(name=agent_name)

def test_sidecar_resources(k8s_core_client, create_agent_resource, delete_agent_resource):
    """Test sidecar container with resource requests/limits"""
    agent_name = "test-sidecar-resources"
    agent_data = create_agent_resource(
        name=agent_name,
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
        name=f"{agent_name}-pod",
        namespace="default"
    )

    # Verify resources
    sidecar = next(c for c in pod.spec.containers if c.name == "tool-manager")
    assert sidecar.resources.requests['memory'] == '64Mi'
    assert sidecar.resources.requests['cpu'] == '250m'
    assert sidecar.resources.limits['memory'] == '128Mi'
    assert sidecar.resources.limits['cpu'] == '500m'
    delete_agent_resource(name=agent_name)

def test_shared_volume_file_access(k8s_core_client, create_agent_resource, delete_agent_resource):
    """Test file sharing between init container, sidecar, and main container"""
    agent_name = "test-file-sharing"
    agent_data = create_agent_resource(
        name=agent_name,
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
        name=f"{agent_name}-pod",
        namespace="default"
    )

    # Verify volume mounts
    sidecar = next(c for c in pod.spec.containers if c.name == "tool-manager")
    agent = next(c for c in pod.spec.containers if c.name == "agent")
    
    assert any(vm.name == "shared-volume" for vm in sidecar.volume_mounts)
    assert any(vm.name == "shared-volume" for vm in agent.volume_mounts)

    delete_agent_resource(name=agent_name)

def test_sidecar_env_vars(k8s_core_client, create_agent_resource, delete_agent_resource):
    """Test sidecar environment variables injection"""
    agent_name = "test-sidecar-env"
    test_vars = [
        {'name': 'SIDECAR_VAR', 'value': 'sidecar_value'},
        {'name': 'ANOTHER_VAR', 'value': 'another_value'}
    ]
    
    # Create AgentType with sidecar with environment variables
    agent_data = create_agent_resource(
        name=agent_name,
        image="nginx:latest",
        sidecar={
             "name": "tool-manager",
             "image": "busybox:latest",
             "environment": {
                "variables": test_vars
            }
        }
    )
    
    time.sleep(5)
    
     # Get the pod
    pod = k8s_core_client.read_namespaced_pod(
       name=f"{agent_name}-pod",
       namespace="default"
    )

    # Check environment variables in sidecar container
    sidecar = next(c for c in pod.spec.containers if c.name == "tool-manager")
    env_vars = {env.name: env.value for env in sidecar.env} if sidecar.env else {}
    
    for var in test_vars:
        assert env_vars.get(var['name']) == var['value'], f"Environment variable {var['name']} not set correctly"
    
    delete_agent_resource(name=agent_name)

def test_invalid_sidecar_config(k8s_core_client, create_agent_resource, delete_agent_resource):
  """Test sidecar invalid spec handling"""
  agent_name = "test-sidecar-invalid"
  with pytest.raises(client.exceptions.ApiException) :
        create_agent_resource(
          name=agent_name,
          image="nginx:latest",
            sidecar={
                "name": "tool-manager"
            }
        )
  with pytest.raises(client.exceptions.ApiException):
        create_agent_resource(
          name=agent_name,
          image="nginx:latest",
            sidecar={
                "name": "tool-manager",
                 "image": "busybox:latest",
                "resources": 'invalid'
            }
        )
  
  with pytest.raises(client.exceptions.ApiException) :
        create_agent_resource(
          name=agent_name,
          image="nginx:latest",
            sidecar={
                "name": "tool-manager",
                 "image": "busybox:latest",
                "resources": { "requests": "invalid"}
            }
        )

  with pytest.raises(client.exceptions.ApiException) :
        create_agent_resource(
          name=agent_name,
          image="nginx:latest",
            sidecar={
                "name": "tool-manager",
                 "image": "busybox:latest",
                "resources": { "requests": { "cpu": 100 }}
            }
        )
  delete_agent_resource(name=agent_name)


def test_basic_container_creation(k8s_core_client, create_agent_resource, delete_agent_resource):
    """Test basic agent container creation"""
    agent_name = "test-agent-basic"
    # Create AgentType with basic spec
    agent_data = create_agent_resource(
        name=agent_name,
        image="nginx:latest",
    )

    # Wait for pod to be ready
    time.sleep(5)
    
    # Get pod and verify main container is created.
    pod = k8s_core_client.read_namespaced_pod(
       name=f"{agent_name}-pod",
       namespace="default"
    )
    
    # Verify agent container exists
    containers = [container.name for container in pod.spec.containers]
    assert "agent" in containers
    # Cleanup
    delete_agent_resource(name=agent_name)