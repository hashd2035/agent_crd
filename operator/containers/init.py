from ..utils.volume import get_volume_mounts

def create_init_container():
    """Create the init container configuration"""
    return {
        'name': 'init-wrapper',
        'image': 'busybox:latest',
        'command': ['sh', '-c'],
        'args': ['echo \'console.log("wrapped");\' > /shared/wrapper.js'],
        'volumeMounts': get_volume_mounts()
    }
