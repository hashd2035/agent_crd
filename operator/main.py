import kopf
from kubernetes import client, config

@kopf.on.create('agents.example.com', 'v1', 'agenttypes', field='spec.agent')
def create_agent(spec, name, namespace, logger, **kwargs):
    """Create a pod when an AgentType resource is created"""
    try:
        agent_spec = spec.get('agent', {})
        image = agent_spec.get('image')
        
        if not image:
            raise kopf.PermanentError("Agent image must be specified")
        
        pod = client.V1Pod(
            metadata=client.V1ObjectMeta(
                name=f"{name}-pod",
                labels={'app': name}
            ),
            spec=client.V1PodSpec(
                containers=[
                    client.V1Container(
                        name="agent",
                        image=image
                    )
                ]
            )
        )
        
        api = client.CoreV1Api()
        created_pod = api.create_namespaced_pod(
            namespace=namespace,
            body=pod
        )
        
        logger.info(f"Created pod {created_pod.metadata.name}")
        return {'pod_name': created_pod.metadata.name}
        
    except Exception as e:
        logger.error(f"Error creating agent pod: {str(e)}")
        raise kopf.PermanentError(f"Failed to create agent pod: {str(e)}")

if __name__ == "__main__":
    kopf.configure(verbose=True)
    kopf.run(clusterwide=True)
