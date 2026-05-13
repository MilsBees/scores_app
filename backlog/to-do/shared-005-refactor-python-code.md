# Refactor Python Code for Maintainability

### Who

<!--Who does this benefit or who will this affect? Who should be able to view this?-->

- Developers maintaining the codebase

### What

<!--What problem needs addressing?-->

- The `views.py` files have grown large and contain many responsibilities (e.g., squash/views.py is 800+ lines)
- Complex calculations are mixed with view logic, making code harder to understand and test
- Similar patterns are repeated across different apps (squash, sjoelen, yamb)

### Why

<!--What value does this add?-->

- Smaller, focused files are easier to navigate and understand
- Separating business logic from views enables unit testing
- Following Django best practices improves maintainability

### Acceptance Criteria

<!--Testable done conditions; avoid implementation detail.-->

- [ ] Split large views.py files into logical modules (e.g., `views/statistics.py`, `views/crud.py`)
- [ ] Extract complex calculations into service functions or model methods
- [ ] Consider using Django class-based views where appropriate
- [ ] Remove code duplication across apps where possible
