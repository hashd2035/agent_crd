# Set registry
default_registry(
    'localhost:5001',
    host_from_cluster='kind-registry:5000',
    single_name='agent-operator'
)

# Allow kind cluster
allow_k8s_contexts('kind-dev')

# Load base configuration using kustomize
k8s_yaml(kustomize('base'))

# Build and deploy the operator
docker_build(
    'agent-operator',
    './operator',
    live_update=[
        sync('./operator', '/app')
    ]
)
