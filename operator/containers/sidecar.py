from typing import Dict, Optional, List
from ..utils.volume import get_volume_mounts

def create_sidecar_container(
    image: str,
    name: str = "tool-manager",
    command: Optional[List[str]] = None,
    args: Optional[List[str]] = None,
    resources: Optional[Dict] = None,
    env_vars: Optional[List[Dict]] = None
) -> Dict:
    """Create a sidecar container configuration.
    
    Args:
        image: Docker image for the sidecar container
        name: Name of the sidecar container (default: tool-manager)
        command: Optional command to run in the container
        args: Optional arguments for the command
        resources: Optional resource requirements (CPU/memory requests/limits)
        env_vars: Optional list of environment variables
        
    Returns:
        Dict containing the sidecar container configuration
    """
    container = {
        'name': name,
        'image': image,
        'volumeMounts': get_volume_mounts()
    }

    # Add optional command and args if provided
    if command:
        container['command'] = command
    if args:
        container['args'] = args

    # Add resource requirements if specified
    if resources:
        container['resources'] = resources

    # Add environment variables if specified
    if env_vars:
        container['env'] = [
            {
                'name': var['name'],
                'value': var['value']
            } for var in env_vars
        ]

    return container

def validate_sidecar_spec(spec: Dict) -> None:
    """Validate the sidecar specification.
    
    Args:
        spec: Sidecar specification dictionary from the CRD
        
    Raises:
        ValueError: If required fields are missing or invalid
    """
    if not spec.get('image'):
        raise ValueError("Sidecar container must specify an image")

    # Validate resource specifications if present
    if 'resources' in spec:
        resources = spec['resources']
        if not isinstance(resources, dict):
            raise ValueError("Resources must be a dictionary")
        
        for section in ['requests', 'limits']:
            if section in resources:
                if not isinstance(resources[section], dict):
                    raise ValueError(f"Resource {section} must be a dictionary")
                
                for resource_type in resources[section]:
                    if resource_type not in ['cpu', 'memory']:
                        raise ValueError(f"Invalid resource type: {resource_type}")

def create_sidecar_from_spec(spec: Dict) -> Dict:
    """Create a sidecar container configuration from a CRD spec.
    
    Args:
        spec: Sidecar specification from the CRD
        
    Returns:
        Dict containing the sidecar container configuration
        
    Raises:
        ValueError: If the specification is invalid
    """
    if not isinstance(spec, dict):
        raise ValueError("Sidecar spec must be a dictionary")
    
    if 'image' not in spec:
        raise ValueError("Sidecar spec must include an image")
        
    container = {
        'name': spec.get('name', 'tool-manager'),
        'image': spec['image'],
        'volumeMounts': get_volume_mounts()
    }
    
    # Add command if specified
    if 'command' in spec:
        container['command'] = spec['command']
        
    # Add args if specified
    if 'args' in spec:
        container['args'] = spec['args']
        
    # Add resources if specified
    if 'resources' in spec:
        container['resources'] = spec['resources']
        
    # Add environment variables if specified
    if 'environment' in spec and 'variables' in spec['environment']:
        container['env'] = [
            {'name': var['name'], 'value': var['value']}
            for var in spec['environment']['variables']
        ]
        
    return container