from utils.volume import get_volume_mounts

def create_agent_container(image, env_vars=None):
    """Create the main agent container configuration"""
    container = {
        'name': 'agent',
        'image': image,
        'volumeMounts': get_volume_mounts()
    }
    
    if env_vars:
        container['env'] = [
            {
                'name': var['name'],
                'value': var['value']
            } for var in env_vars
        ]
    
    return container
