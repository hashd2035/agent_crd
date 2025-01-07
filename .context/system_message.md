**Prompt/Guide for LLMs: Building Kubernetes Operators with Kopf, Kustomize, and Tilt - Avoiding Common Pitfalls**

**Context:**

This guide outlines common mistakes made while building a Kubernetes operator using the Kopf framework, while also leveraging Kustomize for configuration management and Tilt for local development, and integrating software engineering best practices. It is based on a real-world debugging scenario where a seemingly simple issue took several iterations to resolve due to incorrect assumptions, misinterpretations of documentation, a lack of incremental problem-solving, and neglecting broader software engineering principles.

**Key Mistakes to Avoid:**

1.  **Ignoring the Broader Context:**
    *   **Mistake:** Focusing solely on Kopf and disregarding the importance of Kustomize, Tilt, and overall project plans.
    *   **Best Practice:** Always consider the entire development ecosystem. Recognize that Kopf is a part of a larger project with other essential components. Ensure alignment between the operator, Kustomize configurations, and Tilt setup.
2.  **Ignoring Existing Plans and Requirements:**
    *   **Mistake:** Implementing features or fixes without a clear understanding of how they fit into the overall plan (e.g. `comprehensive_plan.md`) and requirements (`functinal_requirements.md`).
    *   **Best Practice:** Start with the requirements and the plan. Always refer to the project's requirements and implementation plans. Ensure every change directly aligns with a specific need or requirement and the plan. Follow the implementation steps on `implementation_details.md`.
3.  **Changing Scope Unnecessarily:**
    *   **Mistake:** Expanding the scope of a task without a clear justification or need, trying to implement more features than needed.
    *   **Best Practice:** Stick to the defined scope for the current step. If a new requirement or feature is identified, discuss it and get approval, before implementing it.
4.  **Building on Previous Steps:**
    *   **Mistake:** Attempting to replace or re-architect significant portions of the system, ignoring what has already been implemented.
    *   **Best Practice:** Implement each step incrementally, building upon the existing codebase. Only change previous implementation if it is absolutely necessary with explicit justification. Do not rewrite the whole things, instead, try to fix the current code.
5.  **Ignoring SOLID and 12-Factor Principles:**
    *   **Mistake:** Creating code that is hard to understand, test, extend and violates SOLID and 12-factor application principles (e.g., tightly coupled components, hard-coded values, not utilizing environment variables etc)
    *   **Best Practice:** Follow software engineering best practices, such as SOLID principles (Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion) and 12-factor app principles (e.g., code base, dependencies, config, backing services, logs, processes etc) to create modular, loosely coupled, maintainable, testable and extensible code. Make sure to follow a clean design.
6.  **Not Thinking About Tests:**
    *   **Mistake:** Implementing code without thinking about testing it. Not having the tests at the first place.
    *   **Best Practice:** Develop a testing strategy before implementing any code changes. Write unit tests, integration tests, and end-to-end tests to ensure the code is working as expected and is also resilient to unexpected behaviors. Also make sure to implement both happy and unhappy paths during testing.

7.  **Incorrect Assumptions About Framework Behavior:**
    *   **Mistake:** Assuming complete control over the resource status and believing it is possible to fully prevent `kopf` from adding data.
    *   **Best Practice:** Always consult the documentation to understand the framework's intended behavior. Frameworks often have their own way of managing state, and trying to fight that is counter-productive.
8.  **Misinterpreting Documentation:**
    *   **Mistake:** Focusing only on the parts of the documentation that seem to support initial (incorrect) assumptions, and not deeply studying it.
    *   **Best Practice:** Review the documentation thoroughly, including related sections, to build a complete picture of how the framework operates and to understand how the components interact with each other.
9.  **Jumping to Code Changes Without Understanding:**
    *   **Mistake:** Trying different code fixes without having a solid understanding of why the issue occurs. Trying to implement quick fixes without fully understanding the framework leads to a trial-and-error approach and wasted effort.
    *   **Best Practice:** Before making changes, always start with a clear understanding of the underlying cause of the problem. Read documentation, and try to form a mental model of the problem.
10. **Lack of Incremental Problem Solving:**
    *   **Mistake:** Implementing large code changes without verifying intermediate steps. This makes it difficult to diagnose what part of the code is causing the problem.
    *   **Best Practice:** Break down complex problems into smaller, manageable steps. Verify each step before moving to the next, allowing for easier isolation of the issues.
11. **Not Tracking Thought Process:**
    *   **Mistake:** Trying different things without tracking what changes were done and what assumptions were made. This often leads to repeating the same mistakes and losing context of the previous attempts.
    *   **Best Practice**: Keep a list of the assumptions and actions taken, so when you get stuck, you can re-evaluate based on what you have done before.
12. **Not Asking for Help:**
    * **Mistake**: I was under the assumption that I knew it all, and did not consult the documentation when I was facing problems and did not ask for help when I was stuck.
    * **Best Practice**: Always consult documentation and seek help when you are stuck, this helps you move forward with a clear understanding.

**Best Practices for Development:**

1.  **Start with the Plan:** Refer to the `comprehensive_plan.md` and `implementation_details.md` before starting every task. Implement each step in order, and do not jump to future steps or change previous steps unless they are necessary.
2.  **Leverage Kustomize:** Use Kustomize to manage different environments (dev/prod) and configurations. Keep the base configs and create overlays for different environments and customizations.
3.  **Use Tilt for Local Development:** Utilize Tilt's live reload and debugging features for fast feedback and an efficient local development experience.
4.  **Follow 12-Factor App Principles:** Design the operator to be stateless, config-driven, and easily deployable across different environments.
5.  **Apply SOLID Principles:** Use single responsibility principle to write modular code, and other SOLID principles to achieve maintainable, extensible and scalable design.
6.  **Test Thoroughly:** Write unit, integration, and end-to-end tests to cover all important scenarios. Write tests that verify both the happy path and unhappy paths.
7.  **Keep It Simple and Minimal:** Implement the minimal set of features that are required to fulfill the current step in the plan. Do not try to do more than required.
8.  **Proper Logging:** Implement proper logging with different logging levels so that the code is easier to debug.
9.  **Clean Code Design:** Write code that is easy to understand and easy to extend in future.
10.  **Version Control:** Use version control properly and keep track of all changes. Do not commit incomplete or unstable code.
11.  **Review Changes:** Review all changes before committing them. Get feedback from others to improve the quality of the code.

**Specific Guidance for Status Updates and Events in Kopf:**

*   **Status Updates:** To fully control status, use `patch_namespaced_custom_object_status` function to patch the full status, and `kopf.StatusProgressStorage` to manage where kopf persists state. Do not rely on `kopf` to automatically merge handler results into status. Set `field_manager='kopf'` to prevent overwriting of status.
*   **Events:** Use `logger.info`, `logger.warning`, and `logger.error` for logging, and don't use the `kopf.event` function or shortcut functions for this purpose. Use `kopf.event` for creating Kubernetes events, if that is required.

**How to Use This Guide:**

*   Before implementing any change, carefully review this guide and any other project documents, such as `comprehensive_plan.md`, `implementation_details.md` and the requirements in `functional_requirements.md`.
*   If you get stuck, go back to the beginning of this guide and try to understand where you missed the mark.
*   Ask questions and seek help from others if you are unsure or cannot grasp the meaning of documentation.

This comprehensive guide should help any LLM (including a new instance of myself) and other developers avoid the common mistakes that I made, and also follow best practices for developing the operator. Please commit to follow this and to not repeat the same mistakes.
