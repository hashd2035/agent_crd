import kopf
from kubernetes import client
from kubernetes.client.rest import ApiException

@kopf.on.create('agents.example.com', 'v1', 'agenttypes')
def create_agent(spec, name, namespace, logger, **kwargs):
    """Create a pod when an AgentType resource is created"""
    try:
        # First try to delete any existing pod with the same name
        api = client.CoreV1Api()
        try:
            api.delete_namespaced_pod(
                name=f"{name}-pod",
                namespace=namespace
            )
            # Wait for pod deletion to complete
            import time
            time.sleep(2)
        except ApiException as e:
            if e.status != 404:  # Ignore 404 (Not Found) errors
                logger.warning(f"Error deleting existing pod: {e}")

        # Then create the new pod
        agent_spec = spec.get('agent', {})
        image = agent_spec.get('image')
        
        if not image:
            raise kopf.PermanentError("Agent image must be specified")
        
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
                'ownerReferences': [{
                    'apiVersion': 'agents.example.com/v1',
                    'kind': 'AgentType',
                    'name': name,
                    'uid': kwargs['body']['metadata']['uid'],
                    'controller': True,
                    'blockOwnerDeletion': True
                }]
            },
            'spec': {
                'containers': [{
                    'name': 'agent',
                    'image': image
                }]
            }
        }
        
        created_pod = api.create_namespaced_pod(
            namespace=namespace,
            body=pod
        )
        
        logger.info(f"Created pod {created_pod.metadata.name}")
        return {'pod_name': created_pod.metadata.name}
        
    except Exception as e:
        logger.error(f"Error creating agent pod: {str(e)}")
        raise kopf.PermanentError(f"Failed to create agent pod: {str(e)}")

def main():
    kopf.configure(verbose=True)
    kopf.run(clusterwide=True)

if __name__ == "__main__":
    main()
