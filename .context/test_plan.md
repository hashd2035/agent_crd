## Test Scenarios
1. Test 1 (Basic Agent Creation):
    - Create AgentType with basic nginx image
    - Verify pod is created
    - Verify pod is running
    - Verify pod has correct labels
2. Test 2 (Agent Deletion):
    - Create AgentType
    - Verify pod exists
    - Delete AgentType
    - Verify pod is removed
3. Test 3 (Invalid Configuration)
    - Create AgentType without image
    - Verify appropriate error message
    - Verify no pod is created
4. Test 4 (test_volume_creation):
    - Creates an AgentType resource.
    - Verifies that the pod has a volume with the specified name.
    - Verifies that the main container has a volume mount with the specified name.
    - Cleans up the resource.
5. Test 5 (test_init_container_execution):
    - Creates an AgentType resource with an init container.
    - Verifies that the pod has an init container with the specified name.
    - Verifies that the pod has a volume with the specified name.
    - Verifies that both init and main containers have volume mounts with the specified name.
    - Verifies that the pod is in a running or pending state after a short wait.
    - Cleans up the resource.
6. Test 6 (test_wrapper_injection):
    - Creates an AgentType resource with an init container.
    - Verifies that the pod has an init container with the specified name.
    - Verifies that the pod has a volume with the specified name.
    - Verifies that both init and main containers have volume mounts with the specified name.
    - Verifies that the pod is in a running or pending state after a short wait.
    - Cleans up the resource.
7. Test 7 (test_container_lifecycle):
    - This test is similar to test_delete_agent, but it is added to make sure that we are testing the lifecycle of the container.
    - Creates an AgentType resource.
    - Verifies that the pod exists.
    - Deletes the AgentType resource.
    - Verifies that the pod is removed.Let