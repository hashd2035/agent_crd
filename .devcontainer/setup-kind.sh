#!/bin/bash
set -o errexit

# Create registry container unless it already exists
reg_name='kind-registry'
reg_port='5001'
if [ "$(docker inspect -f '{{.State.Running}}' ${reg_name} 2>/dev/null || true)" != 'true' ]; then
  docker run \
    -d --restart=always -p "${reg_port}:5000" --name "${reg_name}" \
    registry:2
fi

# Create kind cluster
kind create cluster --config=.devcontainer/kind-config.yaml

# Connect the registry to the cluster network
docker network connect "kind" "${reg_name}" || true

# Document the local registry
kubectl apply -f - <<REGISTRY_EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: local-registry-hosting
  namespace: kube-public
data:
  localRegistryHosting.v1: |
    host: "localhost:${reg_port}"
    help: "https://kind.sigs.k8s.io/docs/user/local-registry/"
REGISTRY_EOF

# Wait for the registry to be ready
until curl -s "http://localhost:${reg_port}/v2/_catalog" > /dev/null; do
  echo "Waiting for registry at localhost:${reg_port} ..."
  sleep 1
done

echo "Registry is ready!"
