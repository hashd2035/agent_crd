from kubernetes.client import V1Volume, V1VolumeMount

def create_shared_volume(name="shared-volume"):
    """Create a shared volume configuration"""
    return V1Volume(
        name=name,
        empty_dir={}
    )

def create_volume_mount(volume_name="shared-volume", mount_path="/shared"):
    """Create a volume mount configuration"""
    return V1VolumeMount(
        name=volume_name,
        mount_path=mount_path
    )

def get_volume_config():
    """Get the volume configuration for the pod"""
    return [{
        'name': 'shared-volume',
        'emptyDir': {}
    }]

def get_volume_mounts():
    """Get the volume mounts for containers"""
    return [{
        'name': 'shared-volume',
        'mountPath': '/shared'
    }]
