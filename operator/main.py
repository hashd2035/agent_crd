import kopf
from kubernetes import client
from kubernetes.client.rest import ApiException
import datetime
import logging

@kopf.on.create('agents.example.com', 'v1', 'agenttypes')
def create_agent(spec, name, namespace, logger, body,  **kwargs):
    """Create a pod when an AgentType resource is created"""
    api = client.CoreV1Api()
    custom_api = client.CustomObjectsApi()
    
    def set_status(phase, reason=None, message=None, status_type="Created"):
        conditions = [{
            'type': status_type,
            'status': phase,
            'lastTransitionTime': datetime.datetime.utcnow().isoformat(),
            'reason': reason,
            'message': message
        }]
        try:
            custom_api.patch_namespaced_custom_object_status(
                group="agents.example.com",
                version="v1",
                name=name,
                namespace=namespace,
                plural="agenttypes",
                body={'status': {'conditions': conditions}},
                field_manager='kopf'
            )
        except ApiException as e:
            logger.error(f"Error updating status: {e}")
    
    def create_event(event_type, reason, message):
        if event_type == 'Normal':
            logger.info(f"Event: {reason} - {message}")
        elif event_type == 'Warning':
            logger.warning(f"Event: {reason} - {message}")
        elif event_type == 'Error':
            logger.error(f"Event: {reason} - {message}")
    
    settings = kopf.OperatorSettings()
    settings.persistence.progress_storage = kopf.StatusProgressStorage(field='status.conditions')


    try:
        set_status(phase='True', reason='PodCreation', message='Starting pod creation', status_type='Created')
        create_event(event_type='Normal', reason='PodCreation', message='Starting pod creation')
        # First try to delete any existing pod with the same name
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
                create_event(event_type='Warning', reason='PodDeletionFailed', message=f"Error deleting existing pod: {e}")

        # Then create the new pod
        agent_spec = spec.get('agent', {})
        image = agent_spec.get('image')
        init_containers = agent_spec.get('initContainers', [])
        
        if not image:
            set_status(phase='False', reason='MissingImage', message='Agent image must be specified', status_type='Created')
            create_event(event_type='Warning', reason='MissingImage', message='Agent image must be specified')
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
                    'uid': body['metadata']['uid'],
                    'controller': True,
                    'blockOwnerDeletion': True
                }]
            },
            'spec': {
                'initContainers': init_containers,
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
        set_status(phase='True', reason='PodCreated', message=f'Pod {created_pod.metadata.name} is created', status_type='Ready')
        create_event(event_type='Normal', reason='PodCreated', message=f'Pod {created_pod.metadata.name} is created')
        
    except Exception as e:
        logger.error(f"Error creating agent pod: {str(e)}")
        set_status(phase='False', reason='PodCreationFailed', message=f"Failed to create agent pod: {str(e)}", status_type='Created')
        create_event(event_type='Error', reason='PodCreationFailed', message=f"Failed to create agent pod: {str(e)}")
        raise kopf.PermanentError(f"Failed to create agent pod: {str(e)}")

def main():
    settings = kopf.OperatorSettings()
    settings.persistence.progress_storage = kopf.StatusProgressStorage(field='status.conditions')
    kopf.configure(settings, verbose=True)
    kopf.run(clusterwide=True)

if __name__ == "__main__":
    main()