from kubernetes import client
from ..containers.agent import create_agent_container
from ..containers.init import create_init_container
from ..utils.volume import get_volume_config

def create_agent_pod(name, namespace, spec, owner_ref):
    """Create a pod with agent and init containers"""
    api = client.CoreV1Api()

    # Get configurations
    agent_spec = spec.get('agent', {})
    image = agent_spec.get('image')
    env_vars = agent_spec.get('environment', {}).get('variables', [])

    # Create pod spec
    pod = {
        'apiVersion': 'v1',
        'kind': 'Pod',
        'metadata': {
            'name': f"{name}-pod",
            'namespace': namespace,
            'labels': {
                'app': name,
                'managed-by': 'agent-operator'
            },
            'ownerReferences': [owner_ref]
        },
        'spec': {
            'volumes': get_volume_config(),
            'initContainers': [create_init_container()],
            'containers': [create_agent_container(image, env_vars)]
        }
    }

    # Create pod
    return api.create_namespaced_pod(
        namespace=namespace,
        body=pod
    )
