# STLab02 — EduCommerce Test Case Execution

**Course:** Software Testing  
**Assignment:** STLab02 – Test Case Execution  
**Student ID:** 20110112  
**Student:** Đỗ Thành Vinh  
**Selected REQs:** REQ-02, REQ-07, REQ-09, REQ-10, REQ-15  
**Baseline P3:** 1A / 2A / 3A — 5 REQs, CSV + HTML dashboard, original application source unchanged.

## Project files and P6 Colab execution output

| File | Purpose |
|---|---|
| `ecommerce_app.py` | **Original** EduCommerce source extracted from the Instruction, section 2.6, without business logic edits |
| `test_runner.py` | Student-level data-driven test runner; supports the five selected REQs |
| `test_cases.csv` | 33 original requirement-based cases; retains untouched expected values |
| `traceability_design.csv` | REQ→COND→TS→TC planning matrix |
| `STLab02_EduCommerce.ipynb` | Notebook with the completed Google Colab run and cell outputs |
| `requirement_analysis.md` | Requirement Analysis, conditions, scenarios, case trace and risk notes |
| `code_explanation.md` | Technical explanation of fixture, CSV reader, dispatch, assertion and reporter |
| `problem_solving_answers.md` | Part 3: eight scenarios, expected/risk, file/function, change implications and test ideas |
| `interview_answers.md` | Part 4: 20 interviews + three code-review responses |
| `reports/test_execution.csv` | **COLAB P6 EXECUTION** raw case execution; subject to independent P7 verification |
| `reports/test_summary.csv` | Per-requirement result counts from Colab execution |
| `reports/traceability_execution.csv` | Design-to-run trace from Colab execution |
| `reports/test_dashboard.html` | Standalone HTML (tables + bar chart), Colab execution |
| `reports/run_metadata.json` | Colab execution time and counts |

**Important:** This is a **P6 technical package synchronized with the observed Colab execution on 2026-10-27 14:42:26 UTC** (33 loaded, 33 PASS, 0 FAIL, 0 BLOCKED). These are real runner outputs and an executed notebook, not an independent P7 oracle audit, a completed P8 evidence collection, or the P9 PDF draft. Do not submit this package alone as the final assignment.

## How to run on Google Colab (required for the assignment)

1. Go to https://colab.research.google.com and upload/open `STLab02_EduCommerce.ipynb` (File → Upload notebook).
2. Run the first cell; verify the Python version and current directory.
3. On the **Upload source and CSV** cell, select the three files from the same extracted ZIP: `ecommerce_app.py`, `test_runner.py`, `test_cases.csv`.
4. Run the **test runner** cell. Review each line, especially FAIL/BLOCKED; take a real screenshot of the run with timestamp/summary (E07).
5. Run the result summary and dashboard cells; review `reports/test_execution.csv`, `reports/test_summary.csv` and `reports/test_dashboard.html`.
6. Run the last cell to download `STLab02_Colab_Execution.zip` and send this output or source screenshots in the chat to verify that the Colab run matches the technical files.
7. Keep the 3 original source/data files separately: the Colab archive only includes **execution outputs**.

**Colab runtime is temporary.** Your local VS Code folder under `Work/HK1_2627/Software Testing/Labs/ST-Lab02/` is the persistent source-of-truth location; upload the files from there when needed. If you rerun Colab, refresh the `reports/` files with that new run together so all timestamps agree. The test input `test_cases.csv` is not modified by the runner.

## Local test run in VS Code / PowerShell (optional)

Python 3.10+ and pandas are required to run the current `test_runner.py`.

```powershell
cd "Work\HK1_2627\Software Testing\Labs\ST-Lab02"
py -3 -m pip install pandas
py -3 test_runner.py
```

If you open VS Code directly in `Labs/ST-Lab02`, simply run `py -3 test_runner.py` from its terminal. Do not run the `pip install` command if pandas is already installed. The optional local run does **not** replace the required Google Colab execution.

### How results are calculated

- PASS: actual matches all keys specified in `expected_json` (including expected business exceptions).
- FAIL: valid test case disagrees with acceptance-rule expected, or an unexpected application error occurs.
- BLOCKED: case cannot be meaningfully executed due to missing/malformed data, duplicate ID, unsupported fixture or schema/dispatch issue.
- Counts: `loaded = pass + fail + blocked`; a parsing failure must not disappear from report rows.
- Pass rate among executed cases: `PASS / (PASS + FAIL)`. Also inspect BLOCKED separately; 100% here does **not** prove all input rows executed.

The mandatory CSV columns are:

```text
test_case_id, requirement_id, condition_id, scenario_id, title, priority, precondition, fixture_key, input_json, expected_type, expected_json, execution_status, actual_result, error_message, evidence_reference
```

Two extra documentation columns (`case_type` and `test_steps`) make individual test cases easier to read. The last four execution-related columns in the source CSV intentionally remain blank; the runner writes actual outputs into `reports/` instead.

## GitHub repository handoff (Task T13 / P6)

GitHub account connection is already available, but a separate **Lab02 repository has not been created**. Create an accessible repository for the course and upload the project files. The Colab results in this package are available for P6 handoff. The submission must have `ecommerce_app.py`, `test_runner.py`, `test_cases.csv`, `README.md`, source documents and execution report. Check that the repository is accessible without a login if a public link is required, and never commit secrets or personal tokens. The final PDF and its GitHub link are a later P9–P11 task.

## Source attribution and limits

- `ecommerce_app.py`: verbatim code block from `STLab02 - Test Case Execution (Instruction)(1).docx` §2.6. No intended fixes to source logic.
- `test_runner.py`, CSV and all supporting notes: new P6 work based on the Requirement and acceptance rules.
- The application is in-memory, no persistent database, real payment gateway, or concurrency simulation.
- REQ-06/REQ-08/REQ-11 appear in the Instruction as worked examples and are **not** among the five newly selected REQs.
- Source code may contain defects outside selected REQs. A 100% local PASS does not establish full product correctness.

## Scope / evidence handoff

- P6: create and hand off source, data, notebook, reports and written Part 3/4 answers.
- P7: independently verify outputs, reproduce suspected defects, check regressions and correct verified technical issues.
- P8: complete screenshots E01–E10 and evidence descriptions.
- P9: compose the PDF report draft.
- P10: final candidate review and report/repository synchronization.
- P11: independent grading-style audit; submit only when permitted.

## P6 Colab handoff record

The five files in `reports/` in this synchronized copy were read from the submitted `STLab02_Colab_Execution.zip`. The notebook was read from the submitted `STLab02_EduCommerce(1).ipynb`. The original `ecommerce_app.py`, `test_runner.py`, and `test_cases.csv` are byte-for-byte the same as the prior P6 project package. Colab run timestamp: `2026-10-27T14:42:26+00:00`; status: 33 PASS, 0 FAIL, 0 BLOCKED. P7 must still independently review test correctness and completeness. Two untested risks for the no-FAIL branch are documented in `requirement_analysis.md` §F.
