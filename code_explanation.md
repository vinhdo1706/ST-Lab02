# STLab02 – Part 2: Explanation of test code (P6 technical notes)

**Scope:** Explains the actual P6 code. Not a report draft or verified screenshot collection. Evidence E01–E10 is scheduled for P8.

## 1. Application baseline

`ecommerce_app.py` is extracted **without business-rule edits** from the Instruction's `%%writefile ecommerce_app.py` block (§2.6). It defines Catalog, Cart, Inventory, Promotions, Shipping, Payments, Checkout and `fixture()`. The original source is intentionally allowed to contain sample bugs; expected assertions follow acceptance rules rather than mirroring implementation.

## 2. Fixture/setup

`test_runner.fresh_state(fixture_key)` returns a fresh `Checkout`, `Customer` and `Cart` for **every** row. Fixture keys are `empty` or supported keys from the Instruction (`300k`, `499999`, `500k`, `600k`, `1000k`, `1500k`). For `empty`, product stocks start A=20, B=15, C=12 and the cart has no lines. For `300k`, B=1; `600k`, A=3. Independent fixtures prevent state contamination via product stock, voucher usage, orders, and payments.

## 3. CSV reader and validation

`pandas.read_csv(..., dtype=str, keep_default_na=False, encoding='utf-8-sig')` reads the CSV while protecting test identifiers and empty fields. `read_cases` checks mandatory column headers. Per row, `evaluate` checks unique ID, REQ/expected_type compatibility, trace IDs, then parses `input_json` and `expected_json` with `json.loads`. Invalid row data becomes **BLOCKED** and retains a result row; a file without the mandatory headers blocks the whole run with an explicit error and exit code 2, rather than reporting a misleading PASS.

## 4. Test dispatcher

`run_business_case` switches by `requirement_id` and invokes the real application function(s):

| REQ | Target | Checked return and state |
|---|---|---|
| REQ-02 | `Cart.add()` and `Cart.subtotal()` | exception, line SKUs/quantities, subtotal |
| REQ-07 | `Promotions.discount()` or `Checkout.place()` | expected voucher error, `customer.used_codes`, order_count, payment status |
| REQ-09 | `Shipping.calculate(Decimal(subtotal), area)` | exact shipping fee |
| REQ-10 | `Checkout.place()` | payment status, order_count, charges; declined must not create order |
| REQ-15 | `Checkout.place()` / `Inventory.reserve()` | stock_after of all SKUs, order_count, charge_count and exception |

Each test row contains explicit `input_json` and `expected_json` from the corresponding rule. A returned Order ID is not the sole assertion; outcome and side effects applicable to the selected requirement are checked.

## 5. Oracle/assertions and expected exception

`check_expected` recursively compares all keys declared by `expected_json` with actual values. This allows actual to contain additional diagnostic fields while still enforcing every stated expectation. `run_business_case` catches **expected business `ValueError`** from the application and returns `ValueError:MESSAGE` as a comparable actual. Therefore a correct exception can result in PASS; a missing/wrong exception results in FAIL.

## 6. try/except and status

- `PASS`: oracle matches actual on all expected keys.
- `FAIL`: business behavior differs from an unambiguous expected oracle, or an unexpected runtime exception occurred during a valid case.
- `BLOCKED`: test case cannot be executed reliably because test data, IDs, schema, fixture or dispatch are invalid. Data errors do not silently disappear.

Malformed CSV rows retain ID/REQ when available. **Do not equate a FAIL directly with confirmed software defect** before P7 replay/verification.

## 7. Reporter and traceability

The runner writes:

- `reports/test_execution.csv` – one row per CSV case with expected, actual, status, error, execution_time_ms, UTC timestamp and evidence reference;
- `reports/traceability_execution.csv` – REQ→COND→TS→TC→RUN and status;
- `reports/test_summary.csv` – counts by requirement;
- `reports/run_metadata.json` – totals, timestamp and selected requirements;
- `reports/test_dashboard.html` – self-contained HTML with a per-REQ SVG bar chart and test detail table.

`loaded = PASS + FAIL + BLOCKED`. `pass_rate_executed = PASS/(PASS+FAIL)` when denominator >0; BLOCKED is shown separately. This avoids a visually misleading 100% pass rate when some rows never ran. The input `test_cases.csv` is **never overwritten by the runner**.

## 8. Local trial vs Colab verification

A local Python run is a preliminary technical exercise in P6, not E07 Colab evidence. Colab must run the same three source/data files from the P6 package; its own execution output, timestamp and reports will then be collected. Actual FAILs, root cause and regression belong to P7; final evidence verification belongs to P8.
