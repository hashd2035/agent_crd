# Plans

1. Architecture & Evolution (including folder structure for each step)
2. CRD Design & Evolution (focusing on extensibility)
3. Kustomization Strategy (for all variations)
4. Test Strategy (automated tests)
5. Development/Production Pipeline

# How each sections on the plan are presented
- All 5 plans are aligned each other
- Each section builds on the previous one and the overall plan forms a coherent whole.
- To achive that, each section consists of 
    - Current step implementation
    - How it enables future features
    - How it connects with other sections
    - Required tests
    - Development vs Production considerations
- Code presented in this documentation is not concrete. It will be revised in implementation_details.md

## 1. Architecture & Evolution 

### Section 1: Architecture & Evolution

#### Overview
Progressive implementation plan showing how the architecture evolves to support:
- User container/code injection
- Tool management via sidecar
- Memory configurations
- LLM API integrations via sidecar
- Development and Production paths

#### Base Structure (Common across all steps)
```plaintext
agent_crd/
├── .github/
│   └── workflows/              # CI/CD pipelines
├── hack/                       # Development and build scripts
│   ├── kind-with-registry.sh
│   └── run-integration-tests.sh
└── tests/                      # Common test configurations
    └── integration/
        └── test-framework/
```

#### Step-by-Step Evolution

##### Step 1: Basic Agent Infrastructure
Goal: Set up basic CRD and operator with testing framework

```plaintext
agent_crd/
├── base/
│   ├── crds/
│   │   ├── kustomization.yaml
│   │   └── agent.yaml         # Basic CRD definition
│   ├── operator/
│   │   ├── kustomization.yaml
│   │   └── deployment.yaml    # Basic operator deployment
│   └── kustomization.yaml     # Combines CRDs and operator
├── config/
│   ├── dev/                   # Development configuration
│   │   ├── kustomization.yaml # Dev-specific settings
│   │   └── patches/
│   │       └── operator_resources.yaml
│   └── test/                  # Test configuration
│       ├── kustomization.yaml
│       └── test_agents/       # Test agent definitions
│           └── basic_agent.yaml
├── operator/
│   ├── pkg/
│   │   ├── apis/
│   │   │   └── agenttype/     # API types
│   │   └── controller/        # Basic controller logic
│   ├── cmd/
│   │   └── manager/          # Operator entrypoint
│   └── tests/
│       ├── unit/
│       └── integration/
└── Tiltfile

Key Features:
- Basic CRD structure
- Simple operator
- Test framework setup
- Development environment
```

##### Step 2: User Container Integration & Environment Injection
Goal: Support user container injection and environment setup via init container

```plaintext
agent_crd/
├── base/
│   ├── crds/
│   │   └── agent.yaml         # Added container spec, and environment injection
│   └── operator/
│       └── deployment.yaml    # Enhanced operator
├── config/
│   ├── dev/
│   │   └── samples/          # (+) Sample containers
│   └── test/
│       └── test_agents/
│           ├── custom_container.yaml
│           └── validation_tests.yaml
├── operator/
│   ├── pkg/
│   │   ├── environment/        # (+) Environment handling
│   │   │   ├── injector.go
│   │   │   └── validator.go
│   │   └── controller/
│   └── tests/
│       └── environment/        # (+) Environment tests
└── examples/
    └── containers/          # (+) Example containers

Key Changes:
- Container specification in CRD
- Extensible init container for environment setup
- Environment validation
- Environment injection logic
- Environment-specific tests
```

##### Step 3: Tool Management via Sidecar
Goal: Support tool configuration, installation, and discovery via sidecar

```plaintext
agent_crd/
├── base/
│   ├── crds/
│   │   └── agent.yaml         # Added tool spec
│   ├── tools/                # (+) Tool definitions
│   │   ├── kustomization.yaml
│   │   └── base_tools.yaml
│   └── operator/
├── config/
│   ├── tools/               # (+) Tool configurations
│   │   ├── development.yaml
│   │   └── production.yaml
│   └── test/
│       └── test_agents/
│           └── tool_tests.yaml
├── operator/
│   ├── pkg/
│   │   ├── tools/           # (+) Tool management
│   │   │   ├── installer.go
│   │   │   ├── registry.go
│   │   │   └── proxy.go
│   │   └── controller/
│   └── tests/
│       └── tools/           # (+) Tool tests

Key Changes:
- Tool specification in CRD
- Sidecar container for tool discovery & access
- Tool installation logic in sidecar
- Tool registry
- Tool-specific tests
```

##### Step 4: Memory & API Configuration
Goal: Add memory management for all containers and LLM API integration via sidecar

```plaintext
agent_crd/
├── base/
│   ├── crds/
│   │   └── agent.yaml         # Added memory & API specs
│   └── operator/
├── config/
│   ├── api/                 # (+) API configurations
│   │   ├── development.yaml
│   │   └── production.yaml
│   └── memory/             # (+) Memory profiles
│       ├── small.yaml
│       ├── medium.yaml
│       └── large.yaml
├── operator/
│   ├── pkg/
│   │   ├── memory/         # (+) Memory management
│   │   └── api/           # (+) API integration
│   └── tests/
│       ├── memory/
│       └── api/

Key Changes:
- Memory specification in CRD for all containers (main, init, sidecar)
- API configuration in CRD
- Resource management
- API integration tests in sidecar
```

##### Step 5: Production Hardening
Goal: Production-ready deployment with full test coverage

```plaintext
agent_crd/
├── base/
│   └── monitoring/          # (+) Monitoring setup
├── config/
│   ├── prod/
│   │   ├── kustomization.yaml
│   │   └── overlays/       # Production overlays
│   └── test/
│       └── e2e/            # (+) E2E test suite
├── deploy/                 # (+) Deployment tools
│   ├── production/
│   └── staging/
└── docs/                   # (+) Documentation
    ├── deployment/
    └── development/

Key Changes:
- Production configurations
- Monitoring integration
- Comprehensive E2E tests
- Deployment documentation
```

#### Key Design Decisions

1. Separation of Concerns:
   - Clear separation between operator, CRD, and containers.
   - Modular tool management via sidecar
   - Configurable memory/API settings
   - Extensible init container for environment injection

2. Extensibility:
   - CRD structured for future additions
   - Modular tool definitions
   - Flexible API configurations
   - Extensible init container

3. Testing Strategy:
   - Unit tests per component
   - Integration tests per feature
   - E2E tests for workflows

4. Development Experience:
   - Tilt for local development
   - Sample configurations
   - Quick feedback loop

5. Production Readiness:
   - Proper resource management
   - Monitoring integration
   - Security considerations

#### Next Sections Preview
1. CRD Design & Evolution
2. Kustomization Strategy
3. Test Strategy
4. Development/Production Pipeline

This section outlines how our architecture will evolve through each step, ensuring:

1. No rearchitecting needed for new features
2. Clear testing strategy at each step
3. Support for both development and production
4. Proper separation of concerns

The structure supports all our requirements:

- User container/code injection (Step 2)
- Tool management via sidecar (Step 3)
- Memory and API configurations via sidecar (Step 4)
- Production deployment (Step 5)
- Extensible init container for environment injection (Step 2)


## 2. CRD Design & Evolution (focusing on extensibility)

### Section 2: CRD Design & Evolution

#### Overview
Shows how the CRD evolves through each step while maintaining backward compatibility and extensibility.

#### Evolution Steps

##### Step 1: Basic Agent CRD
```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: agenttypes.agents.example.com
spec:
  group: agents.example.com
  names:
    kind: AgentType
    plural: agenttypes
    singular: agenttype
    shortNames:
      - at
  scope: Namespaced
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          required: ["spec"]
          properties:
            spec:
              type: object
              required: ["agent"]
              properties:
                agent:
                  type: object
                  required: ["image"]
                  properties:
                    image:
                      type: string
                    name:
                      type: string
                      default: "agent"
            status:
              type: object
              properties:
                phase:
                  type: string
                message:
                  type: string
      additionalPrinterColumns:
        - name: Status
          type: string
          jsonPath: .status.phase
        - name: Age
          type: date
          jsonPath: .metadata.creationTimestamp

Example Usage:
```yaml
apiVersion: agents.example.com/v1
kind: AgentType
metadata:
  name: basic-agent
spec:
  agent:
    image: nginx:latest
    name: web-agent
```

### Step 2: User Container Integration & Environment Injection
```yaml
spec:
  versions:
    - name: v1
      schema:
        openAPIV3Schema:
          properties:
            spec:
              properties:
                agent:
                  properties:
                    type:
                      type: string
                      enum: ["container", "code"]
                    container:
                      type: object
                      properties:
                        image:
                          type: string
                        pullPolicy:
                          type: string
                        securityContext:
                          type: object
                    code:
                      type: object
                      properties:
                        source:
                          type: object
                          properties:
                            type:
                              type: string
                              enum: ["git", "local"]
                            repository:
                              type: string
                            path:
                              type: string
                        runtime:
                          type: string
                          enum: ["python", "nodejs"]
                        version:
                          type: string
                    environment:      # <--- ADD THIS
                      type: object
                      properties:
                          variables:
                            type: array
                            items:
                                type: object
                                properties:
                                    name:
                                      type: string
                                    value:
                                      type: string
                          sdk:
                            type: object
                            properties:
                                runtime:
                                  type: string
                                  enum: ["python", "nodejs"]
                                version:
                                   type: string
                                packages:
                                  type: array
                                  items:
                                     type: string
                          glueCode:
                            type: object
                            properties:
                                source:
                                  type: string

Example Usage:
```yaml
# Container-based agent
apiVersion: agents.example.com/v1
kind: AgentType
metadata:
  name: container-agent
spec:
  agent:
    type: container
    container:
      image: custom-agent:latest
      pullPolicy: Always
    environment:
      variables:
        - name: API_KEY
          value: "secret-key"
      sdk:
        runtime: python
        version: "3.9"
        packages:
          - requests
          - pandas


# Code-based agent
apiVersion: agents.example.com/v1
kind: AgentType
metadata:
  name: code-agent
spec:
  agent:
    type: code
    code:
      source:
        type: git
        repository: https://github.com/example/agent
        path: /src
      runtime: python
      version: "3.9"
    environment:
      glueCode:
         source: /shared/gluecode.py
```

### Step 3: Tool Management via Sidecar
```yaml
spec:
  versions:
    - name: v1
      schema:
        openAPIV3Schema:
          properties:
            spec:
              properties:
                tools:
                  type: object
                  properties:
                    required:
                      type: array
                      items:
                        type: string
                    optional:
                      type: array
                      items:
                        type: string
                    custom:
                      type: array
                      items:
                        type: object
                        properties:
                          name:
                            type: string
                          version:
                            type: string
                          source:
                            type: string

Example Usage:
```yaml
apiVersion: agents.example.com/v1
kind: AgentType
metadata:
  name: tooled-agent
spec:
  agent:
    type: container
    container:
      image: base-agent:latest
  tools:
    required:
      - python
      - git
    optional:
      - kubectl
    custom:
      - name: custom-tool
        version: "1.0"
        source: "https://example.com/tools/custom-tool"
```

##### Step 4: Memory & API Configuration
```yaml
spec:
  versions:
    - name: v1
      schema:
        openAPIV3Schema:
          properties:
            spec:
              properties:
                memory:
                  type: object
                  properties:
                    size:
                      type: string
                    type:
                      type: string
                      enum: ["redis", "inmemory"]
                    config:
                      type: object
                      x-kubernetes-preserve-unknown-fields: true
                llm:
                  type: object
                  properties:
                    providers:
                      type: array
                      items:
                        type: object
                        properties:
                          name:
                            type: string
                          type:
                            type: string
                          credentialsSecret:
                            type: string
                          config:
                            type: object
                            x-kubernetes-preserve-unknown-fields: true

Example Usage:
```yaml
apiVersion: agents.example.com/v1
kind: AgentType
metadata:
  name: full-agent
spec:
  agent:
    type: container
    container:
      image: advanced-agent:latest
  tools:
    required: ["python"]
  memory:
    size: "1Gi"
    type: redis
    config:
      persistence: true
  llm:
    providers:
      - name: main-llm
        type: anthropic
        credentialsSecret: anthropic-credentials
        config:
          model: claude-3
      - name: backup-llm
        type: openai
        credentialsSecret: openai-credentials
```

### Step 5: Production Features
```yaml
spec:
  versions:
    - name: v1
      schema:
        openAPIV3Schema:
          properties:
            spec:
              properties:
                monitoring:
                  type: object
                  properties:
                    enabled:
                      type: boolean
                    metrics:
                      type: array
                      items:
                        type: string
                security:
                  type: object
                  properties:
                    networkPolicy:
                      type: object
                    podSecurityContext:
                      type: object
                scaling:
                  type: object
                  properties:
                    minReplicas:
                      type: integer
                    maxReplicas:
                      type: integer
                    metrics:
                      type: array
                      items:
                        type: object

Example Usage:
```yaml
apiVersion: agents.example.com/v1
kind: AgentType
metadata:
  name: production-agent
spec:
  agent:
    type: container
    container:
      image: production-agent:latest
  tools:
    required: ["python"]
  memory:
    size: "2Gi"
    type: redis
  llm:
    providers:
      - name: production-llm
        type: anthropic
        credentialsSecret: prod-anthropic-creds
  monitoring:
    enabled: true
    metrics:
      - memory_usage
      - api_latency
  security:
    networkPolicy:
      allowedNamespaces:
        - default
        - monitoring
  scaling:
    minReplicas: 2
    maxReplicas: 5
    metrics:
      - type: Resource
        resource:
          name: cpu
          target:
            type: Utilization
            averageUtilization: 80
```

#### Key Design Principles

1. Backward Compatibility:
   - All fields optional except core agent spec
   - Default values for backward compatibility
   - Version management through CRD versions

2. Extensibility:
   - Generic configs using x-kubernetes-preserve-unknown-fields
   - Extensible enums for types
   - Custom tool support
   - Extensible init container for environment injection

3. Validation:
   - Strict enums where needed
   - Required fields clearly marked
   - Type validation for all fields

4. Production Ready:
   - Security context support
   - Resource management
   - Monitoring integration

#### Status Subresource
```yaml
status:
  type: object
  properties:
    phase:
      type: string
      enum:
        - Pending
        - Running
        - Failed
        - Succeeded
    conditions:
      type: array
      items:
        type: object
        properties:
          type:
            type: string
          status:
            type: string
          lastTransitionTime:
            type: string
          reason:
            type: string
          message:
            type: string
    toolStatus:
      type: object
    memoryStatus:
      type: object
    llmStatus:
      type: object
```

This section shows the complete CRD evolution path, ensuring:

1. Clean progression through features
2. Extensibility for future additions
3. Backward compatibility
4. Production-ready features

Each step builds on the previous one while maintaining the ability to:

- Inject user containers/code
- Manage tools flexibly
- Configure memory and APIs
- Support production requirements
- Provide extensible environment setup using init container

#### Migration Strategy
1. Use CRD versions for major changes
2. Provide conversion webhooks when needed
3. Document upgrade paths

## 3. Kustomization Strategy (for all variations)

### Section 3: Kustomization Strategy

#### Overview
Define how Kustomize will be used to manage:
- Different environments (dev/prod)
- Agent variations
- Resource configurations
- Local development with Tilt

#### Base Configurations

##### Core Components Base
- CRD definitions
- RBAC settings
- Operator deployment
- Common labels and annotations

##### Agent Base Variants
1. Container-based agents
   - Base container settings
   - Common volume mounts
   - Default resource limits

2. Code-based agents
   - Runtime environments
   - Build configurations
   - Source management

##### Tool Sets Base
- Common development tools
- Language-specific tools
- Custom tool templates

#### Overlay Strategy

##### Environment Overlays
```plaintext
config/
├── dev/
│   ├── kustomization.yaml
│   ├── resource-limits/
│   ├── debug-tools/
│   └── local-storage/
├── staging/
│   ├── kustomization.yaml
│   ├── monitoring/
│   └── test-data/
└── prod/
    ├── kustomization.yaml
    ├── high-availability/
    ├── security/
    └── monitoring/
```

##### Agent Type Overlays
```plaintext
agents/
├── python/
│   ├── data-science/
│   ├── web-service/
│   └── batch-processor/
├── nodejs/
│   ├── api-server/
│   └── worker/
└── custom/
    └── templates/
```

##### Feature Overlays
```plaintext
features/
├── memory/
│   ├── small/
│   ├── medium/
│   └── large/
├── tools/
│   ├── minimal/
│   ├── standard/
│   └── complete/
└── apis/
    ├── development/
    └── production/
```

#### Patch Strategies

##### 1. Resource Management
- Memory configurations
- CPU allocations
- Storage requirements
- Scaling parameters

##### 2. Tool Integration
- Tool selection
- Version management
- Custom tool addition
- Build requirements

##### 3. Security Settings
- Network policies
- Pod security
- API access
- Resource isolation

##### 4. Monitoring
- Metrics collection
- Log aggregation
- Tracing setup
- Alert configurations

#### Development Strategy

##### Local Development (Tilt)
1. Base Components:
   - Local resource limits
   - Debug configurations
   - Fast reload settings

2. Development Tools:
   - Debug tools
   - Testing utilities
   - Local monitoring

3. Sample Configurations:
   - Example agents
   - Test data
   - Quick start templates

##### Testing Configurations
1. Unit Test Environment:
   - Minimal resources
   - Mock services
   - Test data volumes

2. Integration Test Setup:
   - Service dependencies
   - Shared resources
   - Test networks

3. End-to-End Testing:
   - Production-like setup
   - Full feature set
   - Performance testing

#### Production Strategy

##### 1. High Availability
- Resource replication
- Failover configurations
- Load balancing
- State management

##### 2. Security
- Network policies
- Pod security policies
- Secret management
- Access controls

##### 3. Monitoring
- Production metrics
- Logging setup
- Alerting rules
- Dashboard configurations

#### Implementation Plan

##### Step 1: Basic Setup
- Core CRD base
- Simple development overlay
- Basic Tilt configuration

##### Step 2: Agent Variants & Environment Setup
- Container base configuration
- Code injection overlays
- Resource management
- Extensible init container for env setup

##### Step 3: Tool Management
- Tool set definitions
- Version management
- Custom tool support
- Sidecar implementation for tool discovery

##### Step 4: Memory & APIs
- Memory profiles
- API configurations
- Security settings

##### Step 5: Production Ready
- High availability
- Monitoring setup
- Security configurations

#### Validation Strategy

##### 1. Configuration Validation
- Resource consistency
- Security compliance
- Dependency checking

##### 2. Environment Validation
- Context verification
- Resource availability
- Permission validation

##### 3. Update Strategy
- Rolling updates
- Version compatibility
- Rollback procedures

#### Key Considerations

1. Modularity:
   - Independent feature overlays
   - Composable configurations
   - Reusable components

2. Maintainability:
   - Clear structure
   - Documentation
   - Version control

3. Flexibility:
   - Easy customization
   - Feature toggling
   - Environment specifics

4. Security:
   - Environment isolation
   - Resource protection
   - Access control

This section outlines how we'll use Kustomize to:

1. Manage different environments and configurations
2. Support various agent types and features
3. Handle development and production needs
4. Maintain security and stability

The strategy ensures:

- Clean separation of concerns
- Easy customization
- Development efficiency
- Production readiness

## 4. Test Strategy (automated tests)

### Section 4: Focused Test Strategy

#### Core Test Scenarios by Step

##### Step 1: Basic Agent Infrastructure
Purpose: Verify basic agent creation and management

Test Scenarios:
1. Basic Agent Creation
   ```python
   Test "Should create a basic agent pod"
   - Create AgentType with basic nginx image
   - Verify pod is created
   - Verify pod is running
   - Verify pod has correct labels
   ```

2. Agent Deletion
   ```python
   Test "Should clean up resources when agent is deleted"
   - Create AgentType
   - Verify pod exists
   - Delete AgentType
   - Verify pod is removed
   ```

3. Invalid Configuration
   ```python
   Test "Should handle missing image properly"
   - Create AgentType without image
   - Verify appropriate error message
   - Verify no pod is created
   ```

##### Step 2: User Container Integration & Environment Injection
Purpose: Verify init container setup, volume sharing, and environment setup

Test Scenarios:
1. Volume Creation
   ```python
   Test "Should create shared volume"
   - Create AgentType with volume spec
   - Verify volume is created
   - Verify volume is mounted in both containers
   ```

2. Init Container Execution
   ```python
   Test "Should execute init container before main container"
   - Create AgentType with init container
   - Verify init container completes
   - Verify main container starts after init
   - Verify shared volume contains expected files
   ```
3. Environment Variables Injection
   ```python
   Test "Should inject environment variables"
   - Create AgentType with environment variable spec
   - Verify environment variables are available in main container
   ```
4. SDK Installation
   ```python
   Test "Should install SDKs"
   - Create AgentType with SDK installation
   - Verify SDKs are installed in shared volume
   ```
5. Glue Code Injection
  ```python
  Test "Should inject glue code"
    - Create AgentType with glue code source
    - Verify glue code is injected in the shared volume
  ```

##### Step 3: Tool Management via Sidecar
Purpose: Verify sidecar container setup and tool discovery

Test Scenarios:
1. Sidecar Creation
   ```python
   Test "Should create sidecar container"
   - Create AgentType with sidecar spec
   - Verify main container and sidecar exist
   - Verify sidecar is running
   ```

2. Inter-container Communication
   ```python
   Test "Should enable main-sidecar communication"
   - Create AgentType with both containers
   - Verify network connectivity between containers
   - Verify basic proxy functionality
   ```
3. Tool Discovery
  ```python
  Test "Should discover tool"
    - Create AgentType with tool requirements
    - Verify sidecar discovers and installs requested tool
  ```

#### Test Implementation

##### Structure
```plaintext
tests/
├── integration/              # Main test directory
│   ├── steps/               # Tests organized by step
│   │   ├── step1_test.go   # Basic agent tests
│   │   ├── step2_test.go   # Volume & Environment tests
│   │   ├── step3_test.go   # Sidecar & Tool tests
│   │   └── step4_test.go   # Memory & API tests
│   └── utils/              # Test utilities
        └── helpers.go      # Common test functions
```

##### Test Framework
- Use Go testing framework
- Testing utilities in kind cluster
- Simple test runner script

##### Local Testing Process
1. Start local kind cluster
2. Apply CRD and operator
3. Run integration tests
4. Clean up resources

##### Test Running
```bash
# Run all tests
./run-tests.sh

# Run specific step
./run-tests.sh step1
```

This focused approach:
- Tests essential functionality only
- Provides concrete test scenarios
- Uses minimal infrastructure
- Can be run locally easily

## 5. Development/Production Pipeline

### Section 5: Development Pipeline

#### Local Development Setup

##### Prerequisites
```plaintext
- Python 3.9+
- kubectl
- kind/k3d
- Tilt
- kustomize
```

##### Development Workflow

1. Local Cluster Setup
```bash
# Create local cluster
k3d cluster create dev-cluster --registry-create dev-registry:0.0.0.0:5000

# Set context
kubectl config use-context k3d-dev-cluster
```

2. Project Structure for Development
```plaintext
agent_crd/
├── manifests/
│   ├── base/
│   │   ├── crd/
│   │   │   └── agenttype.yaml
│   │   └── kustomization.yaml
│   └── dev/
│       └── kustomization.yaml
├── operator/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── tests/
│   └── integration/
│       ├── conftest.py
│       └── test_*.py
└── Tiltfile
```

3. Tilt Configuration
```python
# Tiltfile
# Load CRD
k8s_yaml(kustomize('manifests/base'))

# Build and deploy operator
docker_build(
    'agent-operator',
    './operator',
    live_update=[
        sync('./operator', '/app')
    ]
)

# Load test resources
k8s_yaml('tests/integration/resources')

# Watch for changes
watch_file('./manifests')
watch_file('./operator')
```

#### Testing During Development

##### Running Tests
```bash
# From project root
pytest tests/integration/

# Run specific test
pytest tests/integration/test_basic_agent.py -v
```

### Test Resources
```plaintext
tests/integration/
├── conftest.py              # Test fixtures
├── resources/              # Test K8s resources
│   ├── basic-agent.yaml
│   └── test-volume.yaml
└── test_*.py              # Test files
```

##### Development Cycle
1. Start Development Environment
```bash
# Start Tilt
tilt up

# View logs
tilt logs
```

2. Development Loop
- Edit code
- Automatic reload via Tilt
- Run tests
- View results

#### Debugging Tools

##### Local Debugging
```bash
# View operator logs
kubectl logs -l app=agent-operator -f

# Check CRD
kubectl get agenttype

# Describe resources
kubectl describe agenttype <name>
```

##### Test Debugging
```bash
# Run tests with more detail
pytest -v -s tests/integration/

# Debug specific test
pytest tests/integration/test_basic_agent.py -v -k "test_create_agent"
```

#### Build and Push Flow

##### Local Registry
```bash
# Build image
docker build -t localhost:5000/agent-operator:dev ./operator

# Push to local registry
docker push localhost:5000/agent-operator:dev
```

##### Development Tags
- Use commit SHA for versioning during development
- Tag format: dev-{sha}
- Latest tag for current development

#### Key Development Features

1. Fast Feedback Loop
- Live reload with Tilt
- Quick test execution
- Immediate log access

2. Resource Management
- Clean up after tests
- Isolated test resources
- Development resource limits

3. Debugging Capability
- Direct log access
- Resource inspection
- Test debugging

4. Test Integration
- Pytest for testing
- Integration with Tilt
- Resource fixtures

This development pipeline:
- Focuses on local development
- Uses minimal required tools
- Provides fast feedback
- Supports our test strategy

