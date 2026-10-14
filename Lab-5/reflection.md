# Reflection — Static Code Analysis

> **Important:** The repository README says to answer the four reflection questions from the lab handout, but those questions are not included in the repository. The answers below cover the main learning outcomes of this lab. If the handout uses specific questions, replace these headings with the exact questions and adapt the answers accordingly.

## 1. What problems did the static analysis tools identify?

Pylint, Flake8 and Bandit examine different aspects of the program. Pylint checks code quality, naming, documentation and suspicious patterns. Flake8 checks style and common programming errors. Bandit focuses on security risks. In the original warehouse stock manager, the main concerns included the use of `eval()` for formula evaluation, a hard-coded supervisor password, a mutable default list, broad exception handling, manually managed files, and inconsistent validation of SKUs and quantities. Some logic errors, such as attempting to remove more stock than is available, also required reading and running the program because a static-analysis warning alone does not prove that the behaviour is correct or incorrect.

## 2. Which issues were fixed, and how?

The revised program removes unrestricted `eval()` and parses formulas using a restricted set of arithmetic operations. It reads the supervisor password from the `WAREHOUSE_SUPERVISOR_PASSWORD` environment variable instead of embedding a password in the source. The mutable default argument was replaced with `None`, with history recorded only when a list is explicitly provided. Broad exception suppression was replaced with validation and a clear `InventoryError`. File operations use context managers and UTF-8 encoding. Stock quantities and SKU values are validated, unknown SKUs and insufficient stock are reported, and JSON data is validated before replacing the in-memory inventory. Unused calculations were removed and functions were renamed using standard snake_case naming.

## 3. What are the limitations of static analysis tools?

Static analysis can identify suspicious code patterns without executing the program, but it cannot guarantee that the program is correct, secure or suitable for every real-world situation. It may miss business-logic errors, invalid assumptions, unexpected input combinations and problems that only occur at runtime. It can also report findings that need human judgement. Therefore, static analysis should be combined with running the program, testing normal and invalid inputs, checking saved data, and reviewing the changes.

## 4. What did you learn from this lab?

This lab demonstrated that code quality and security are more than formatting. Unsafe dynamic evaluation, hard-coded credentials, weak error handling and inadequate input validation can create real reliability and security problems. Small changes such as context managers, explicit exceptions, type and quantity checks, and safer formula parsing make the code easier to maintain and safer to use. After making changes, all three analysis tools should be run again and their final reports saved. The final program should also be executed and tested to confirm that the improvements have not broken its warehouse stock functionality.
