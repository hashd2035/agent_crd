import kopf
from kubernetes import client
from kubernetes.client.rest import ApiException
import datetime
from datetime import timezone
import logging
import json
from .handlers.create import create_agent_pod

@kopf.on.create('agents.example.com', 'v1', 'agenttypes')
def create_agent(spec, name, namespace, logger, body, **kwargs):
    """Create a pod when an AgentType resource is created"""
    custom_api = client.CustomObjectsApi()
    
    logger.setLevel(logging.DEBUG)

    isItString = datetime.datetime.utcnow().isoformat()
    logger.info(f"is it a string? {isItString} {isinstance(isItString, str)}")
    
    def set_status(phase, reason=None, message=None, status_type="Created"):
        conditions = [{
            'type': status_type,
            'status': phase,
            'lastTransitionTime': datetime.datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
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
        # Add immediate debug log to track process start
        logger.info("Starting pod creation handler")
        
        # Create owner reference
        owner_ref = {
            'apiVersion': 'agents.example.com/v1',
            'kind': 'AgentType',
            'name': name,
            'uid': body['metadata']['uid'],
            'controller': True,
            'blockOwnerDeletion': True
        }
        
        # Create pod using handler
        created_pod = create_agent_pod(name, namespace, spec, owner_ref)
        
        # Keep all the useful debug logs
        logger.info(f"Created pod {created_pod.metadata.name}")
        logger.debug(f"Pod details:")
        logger.debug(f"  Name: {created_pod.metadata.name}")
        logger.debug(f"  Namespace: {created_pod.metadata.namespace}")
        logger.debug(f"  Phase: {created_pod.status.phase if created_pod.status else 'Unknown'}")
        
        # Return a dict with string values only
        return {
            'pod_name': str(created_pod.metadata.name),
            'namespace': str(created_pod.metadata.namespace),
            'uid': str(created_pod.metadata.uid),
            'status': 'created'
        }

    except Exception as e:
        logger.error(f"Error creating agent pod: {str(e)}")
        raise kopf.PermanentError(f"Failed to create agent pod: {str(e)}")

def main():
    settings = kopf.OperatorSettings()
    settings.persistence.progress_storage = kopf.StatusProgressStorage(field='status.conditions')
    kopf.configure(settings, verbose=True)
    kopf.run(clusterwide=True)

if __name__ == "__main__":
    main()