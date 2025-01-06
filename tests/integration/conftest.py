import pytest
from kubernetes import client, config

@pytest.fixture
def k8s_client():
    # Load kube config
    config.load_kube_config()
    return client.CustomObjectsApi()
