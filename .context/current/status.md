**Implementation Plan**

*   **Step 1: Basic Agent Infrastructure** (Completed)
*   **Step 2: User Container Integration & Environment Injection** (In Progress)
    *   2.1. Plan (Done)
    *   2.2. Test Cases (Done)
    *   2.3. Init Container Setup (Done)
    *   2.4. Shared Volume Setup (Done)
    *   2.5. Environment Injection (In Progress)
        *   2.5.1. Initial Implementation (Done)
        *   2.5.2. Extensible init container for environment setup (To Do)
        *   2.5.3. Move the previous wrapper injection logic to the extensible init container and make the tests pass (To Do)
    *   2.6. Test (To Do)
    *   2.7. Document (To Do)
*   **Step 3: Tool Management via Sidecar**
    *   Sidecar container setup.
    *   Tool discovery via registry.
    *   Tool installation in sidecar.
    *   Inter-container communication between main and sidecar.
*   **Step 4: Memory & API Configuration**
    *   Memory management for all containers.
    *   API integration via sidecar.
    *   API proxying (in sidecar).
*   **Step 5: Production Features**
    *   Security features (in sidecar).
    *   Monitoring integration (in sidecar).

**Next Steps**

1.  **Implement Extensible Init Container (Step 2.5.2)**
    *   Enhance the init container to support various environment setup options.
        *   Support environment variable injection.
        *   Support SDK installation.
        *   Support glue code injection.
    *   Make the init container configurable via the CRD.

2.  **Integrate Wrapper Logic into Init Container (Step 2.5.3)**
    *   Move the existing wrapper injection logic to the new extensible init container.
    *   Ensure all previous tests still pass with the updated logic.
   
3.  **Specific Tasks for Environment Injection:**
    *   Create tests to verify features in step 3. Let them fail for now.
    *   Make sure to execute tests after each step and move on to the next step, only when tests pass.
    *   Update CRD to reflect new `environment` section.
    *   Update operator logic to handle SDK installation, glue code, and environment variables.

    ```yaml
     spec:
       agent:
         environment:
           variables:
             - name: API_KEY
               value: secret-key
           sdk:
             runtime: python
             version: "3.9"
             packages:
               - requests
               - pandas
           glueCode:
             source: /shared/gluecode.py
     ```
    *   Implement the environment injection logic in the init container and make tests pass
    *   Add validation for `environment` configuration
    *   Add environment configuration options in the CRD spec
     
**For Each step**

1.  Make sure you have a full understanding of where we are
    *   run commandlines to see related pods, operator logs, etc.
    e.g.
        ```
        kubectl get agenttype test-agent -n default -o yaml
        kubectl logs -n default -l app=agent-operator -f
        ```
    *   run tests `pytest tests/integration/test_basic_agent.py -v`
2.  Suggest implementation with explanation
3.  Once completed, present this document again with updated information
4.  If not competed and if you are troubleshooting the same issue more than once, then, please present tracking log, each time you either fail or success, instead.