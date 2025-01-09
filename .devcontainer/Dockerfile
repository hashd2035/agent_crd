FROM mcr.microsoft.com/devcontainers/python:3.9

# Install necessary packages
RUN apt-get update && apt-get install -y \
    curl \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*


# Install Go-Task (https://taskfile.dev/#/installation)
RUN curl -fsSL https://github.com/go-task/task/releases/download/v3.34.1/task_linux_amd64.tar.gz -o task.tar.gz; \
    tar -xf task.tar.gz -C /usr/local/bin task && \
    rm task.tar.gz

ENV PATH=/home/vscode/.local/bin:$PATH

# Install Tilt
RUN curl -fsSL https://raw.githubusercontent.com/tilt-dev/tilt/master/scripts/install.sh | bash

# Install kustomize
RUN curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash && \
    mv kustomize /usr/local/bin/

# Install kind
RUN curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-arm64 && \
    chmod +x ./kind && \
    mv ./kind /usr/local/bin/

WORKDIR /workspaces/agent_crd
