import kopf
from kubernetes import client
from kubernetes.client.rest import ApiException
import datetime
from datetime import timezone
import logging
import json
from kubernetes.client import V1Pod, V1PodSpec, V1Container, V1Volume, V1VolumeMount

@kopf.on.create('agents.example.com', 'v1', 'agenttypes')
def create_agent(spec, name, namespace, logger, body, **kwargs):
    """Create a pod when an AgentType resource is created"""
    api = client.CoreV1Api()
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
        
        agent_spec = spec.get('agent', {})
        image = agent_spec.get('image')
        
        # Debug log before init container creation
        logger.info("Creating init containers")
        
        # Debug environment variables
        env_vars = spec.get('agent', {}).get('environment', {}).get('variables', [])
        logger.info(f"Environment variables from spec: {env_vars}")
        logger.info(f"Full spec: {spec}")
        logger.info(f"Agent spec: {spec.get('agent', {})}")
        logger.info(f"Environment spec: {spec.get('agent', {}).get('environment', {})}")

        # Create init containers using V1Container
        init_containers = [
            V1Container(
                name='init-wrapper',
                image='busybox:latest',
                command=['sh', '-c'],
                args=['echo \'console.log("wrapped");\' > /shared/wrapper.js'],
                volume_mounts=[V1VolumeMount(
                    name='shared-volume',
                    mount_path='/shared'
                )]
            )
        ]

        # Create pod spec with all necessary configuration
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
                'volumes': [{
                    'name': 'shared-volume',
                    'emptyDir': {}
                }],
                'initContainers': [{
                    'name': 'init-wrapper',
                    'image': 'busybox:latest',
                    'command': ['sh', '-c'],
                    'args': ['echo \'console.log("wrapped");\' > /shared/wrapper.js'],
                    'volumeMounts': [{
                        'name': 'shared-volume',
                        'mountPath': '/shared'
                    }]
                }],
                'containers': [{
                    'name': 'agent',
                    'image': image,
                    'volumeMounts': [{
                        'name': 'shared-volume',
                        'mountPath': '/shared'
                    }],
                    'env': [
                        {
                            'name': var['name'],
                            'value': var['value']
                        } for var in agent_spec.get('environment', {}).get('variables', [])
                    ] if agent_spec.get('environment', {}).get('variables') else None
                }]
            }
        }
        
        # Create pod and capture response
        created_pod = api.create_namespaced_pod(
            namespace=namespace,
            body=pod
        )
        
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