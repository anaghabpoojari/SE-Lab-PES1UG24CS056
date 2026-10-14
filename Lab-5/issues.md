# Static Code Analysis — Issues Found

## Issue Table

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| Unsafe formula evaluation | Security — High | 57, 74 | `eval()` can execute arbitrary Python expressions rather than restricting the operation to a safe calculation. | Replace `eval()` with a restricted formula parser and remove unnecessary dynamic evaluation. |
| Hard-coded supervisor password | Security — Medium | 8 | Credentials are stored directly in source code. | Use configurable credentials and document the authentication limitations. |
| Mutable default argument | Code quality — Medium | 10 | The `history=[]` default list can be shared across function calls. | Use `None` as the default and initialize the list inside the function. |
| Broad exception handling | Reliability — Medium | 16–22 | A bare `except` silently suppresses errors during stock removal. | Validate inputs and handle expected exceptions explicitly. |
| Unused variable | Code quality | 50 | `total_units` is calculated but never used. | Remove the unused calculation or use it meaningfully in a report. |
| Unmanaged file resources | Reliability | 30–39, 58–60 | Files are manually closed, which can fail to happen if an exception occurs. | Use context managers with `with open(...)`. |

## Verification

After applying the fixes, rerun Pylint, Bandit and Flake8. Update the line numbers and descriptions to match the final code and record which issues have been resolved.