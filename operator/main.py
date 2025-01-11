import kopf
from kubernetes import client
from kubernetes.client.rest import ApiException
import datetime
from datetime import timezone
import logging
import json
from kubernetes.client import V1Pod
from utils.volume import get_volume_mounts
from containers.agent import create_agent_container
from containers.sidecar import create_sidecar_from_spec, validate_sidecar_spec
from containers.init import create_init_container

@kopf.on.create('agents.example.com', 'v1', 'agenttypes')
def create_agent(spec, name, namespace, logger, body, **kwargs):
    """Create a pod when an AgentType resource is created"""
    api = client.CoreV1Api()
    
    logger.setLevel(logging.DEBUG)
    
    try:
        # Log the full incoming resource
        logger.info(f"Received AgentType resource creation request:")
        logger.info(f"Name: {name}")
        logger.info(f"Namespace: {namespace}")
        # logger.info(f"Full body: {json.dumps(body, indent=2)}") <- REMOVED
        logger.info(f"Spec content: {spec}") # Changed this
        
        # Extract specifications
        agent_spec = spec.get('agent', {})
        sidecar_spec = spec.get('sidecar')
        
        logger.info(f"Extracted agent spec: {json.dumps(agent_spec, indent=2)}")
        logger.info(f"Extracted sidecar spec: {json.dumps(sidecar_spec, indent=2) if sidecar_spec else 'No sidecar spec'}")
        
        # Create containers list starting with main agent
        containers = [create_agent_container(
            image=agent_spec['image'],
            env_vars=agent_spec.get('environment', {}).get('variables', [])
        )]
        
        logger.info("Created main agent container configuration")
        
        # Add sidecar if specified
        if sidecar_spec:
            logger.info(f"Processing sidecar configuration: {json.dumps(sidecar_spec, indent=2)}")
            
            try:
                validate_sidecar_spec(sidecar_spec)
                sidecar = create_sidecar_from_spec(sidecar_spec)
                containers.append(sidecar)
                logger.info(f"Added sidecar container: {json.dumps(sidecar, indent=2)}")
            except ValueError as e:
               logger.error(f"Invalid sidecar configuration: {str(e)}")
               raise kopf.PermanentError(f"Failed to create sidecar container: {str(e)}")
           
        # Create pod configuration
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
                'initContainers': [create_init_container()],
                'containers': containers
            }
        }
        
        logger.info(f"Created pod configuration: {json.dumps(pod, indent=2)}")
        
        # Create pod
        created_pod = api.create_namespaced_pod(
            namespace=namespace,
            body=pod
        )
        
        logger.info(f"Successfully created pod {created_pod.metadata.name}")
        logger.debug("Pod details:")
        logger.debug(f"  Name: {created_pod.metadata.name}")
        logger.debug(f"  Namespace: {created_pod.metadata.namespace}")
        logger.debug(f"  Phase: {created_pod.status.phase if created_pod.status else 'Unknown'}")
        logger.debug(f"  Containers: {[c.name for c in created_pod.spec.containers]}")
        
        return {
            'pod_name': created_pod.metadata.name,
            'namespace': created_pod.metadata.namespace,
            'uid': created_pod.metadata.uid,
            'status': 'created'
        }

    except Exception as e:
        logger.error(f"Error creating agent pod: {str(e)}")
        logger.error(f"Error details:", exc_info=True)
        raise kopf.PermanentError(f"Failed to create agent pod: {str(e)}")

def main():
    settings = kopf.OperatorSettings()
    settings.persistence.progress_storage = kopf.StatusProgressStorage(field='status.conditions')
    kopf.configure(settings, verbose=True)
    kopf.run(clusterwide=True)

if __name__ == "__main__":
    main()