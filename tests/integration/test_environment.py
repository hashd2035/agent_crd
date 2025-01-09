import pytest
from kubernetes import client
import time

def test_environment_variables(k8s_core_client, create_agent_resource, delete_agent_resource):
    """Test environment variables injection"""
    agent_name = "test-env-vars"
    agent_image = "nginx:latest"
    test_vars = [
        {'name': 'TEST_VAR', 'value': 'test_value'},
        {'name': 'ANOTHER_VAR', 'value': 'another_value'}
    ]

    # Create AgentType with environment variables
    agent_data = create_agent_resource(
        name=agent_name,
        image=agent_image,
        environment={
            'variables': test_vars
        }
    )

    # Wait for pod to be ready
    time.sleep(5)

    # Get pod and verify environment variables
    pod = k8s_core_client.read_namespaced_pod(
        name=f"{agent_name}-pod",
        namespace="default"
    )

    # Debug output
    print(f"Pod spec: {pod.spec}")
    print(f"Container env: {pod.spec.containers[0].env}")

    # Check environment variables in main container
    container = pod.spec.containers[0]
    env_vars = {env.name: env.value for env in container.env} if container.env else {}

    # Verify each expected variable
    for var in test_vars:
        assert env_vars.get(var['name']) == var['value'], f"Environment variable {var['name']} not set correctly"
    
    # Cleanup
    delete_agent_resource(name=agent_name)

def test_sdk_installation(k8s_core_client, create_agent_resource, delete_agent_resource):
    """Test SDK installation in init container"""
    agent_name = "test-sdk-install"
    agent_image = "python:3.9-slim"
    
    # Create AgentType with SDK requirements
    agent_data = create_agent_resource(
        name=agent_name,
        image=agent_image,
        environment={
            'sdk': {
                'runtime': 'python',
                'version': '3.9',
                'packages': ['requests', 'pandas']
            }
        }
    )

    # Wait for pod to be ready
    time.sleep(5)
    
    # Get pod and verify init container completed
    pod = k8s_core_client.read_namespaced_pod(
        name=f"{agent_name}-pod",
        namespace="default"
    )
    
    # Verify init container status
    init_container_statuses = pod.status.init_container_statuses or []
    assert any(status.state.terminated and status.state.terminated.exit_code == 0 
              for status in init_container_statuses)
    
    # Cleanup
    delete_agent_resource(name=agent_name) 