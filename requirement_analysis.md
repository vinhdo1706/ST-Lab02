# STLab02 – Requirement Analysis & Test Design (P6 – technical artifact, not PDF report)

**Authoritative sources:** STLab02 Requirement (Part 1) + STLab02 Instruction (1.2, 2.6).
**Frozen P3 scope:** REQ-02, REQ-07, REQ-09, REQ-10, REQ-15. REQ-06/08/11 are worked examples and are not selected.

## A. Requirement analysis

| REQ | Module | Actor | Acceptance rule | Precondition | Input | Output/oracle | Risk | Clarification |
|---|---|---|---|---|---|---|---|---|
| REQ-02 | Cart | Customer | quantity là số nguyên dương; cùng SKU được cộng dồn | Cart có catalog hợp lệ | SKU và quantity của từng lần add | CartLine và subtotal hoặc INVALID_QUANTITY | Số lượng sai vẫn thay giỏ; trùng SKU thành nhiều dòng | Có cần chặn bool? Python coi True là int; cần BA/PO xác nhận nếu mở rộng. |
| REQ-07 | Promotion | Customer | Voucher không hợp lệ/used phải bị từ chối; chỉ đánh dấu used sau khi tạo order thành công | Mã voucher, customer và giỏ hợp lệ | voucher, customer.used_codes, kết quả payment | Voucher exception, used_codes, số order | Mã bị consume khi declined; tái dùng mã đã used | Phạm vi REQ-07 không mặc định bao gồm chính sách ngưỡng SAVE10 của REQ-06. |
| REQ-09 | Shipping | Customer | inner miễn phí từ subtotal 500000; dưới đó 30000; outer 50000 | Có subtotal Decimal và area | subtotal và area | shipping fee Decimal | Sai dấu biên hoặc phân loại vùng | Quy tắc area khác inner/outer không định nghĩa cho nhóm REQ này; không tự khẳng định. |
| REQ-10 | Payments | Customer | COD=PENDING_COD; ONLINE approved mới PAID; declined không tạo order | Customer authenticated và cart có hàng | method, approved, key | order status, số order, số charge hoặc PAYMENT_DECLINED | Tạo order khi declined; ghi charge sai | Rollback stock sau declined thuộc REQ-08 worked example, không gán nhầm cho REQ-10. |
| REQ-15 | Inventory | Customer | Nếu bất kỳ SKU thiếu stock phải từ chối toàn đơn, SKU khác không bị trừ | Giỏ có nhiều SKU và stock xác định | SKU, quantity, tồn kho ban đầu | OUT_OF_STOCK/Order; tồn kho của toàn bộ SKU | Trừ SKU đủ trước khi phát hiện SKU thiếu | Atomicity ở đây là mô hình in-memory tuần tự, không chứng minh concurrency. |

## B. Condition → Scenario structure

Conditions are axes of behavior. Scenarios state WHAT to test; concrete inputs and expected values appear in `test_cases.csv`.

| Requirement | Condition | Scenario | Test cases |
|---|---|---|---|
| REQ-02 | COND-CART-02 | TS-CART-VALID | TC-CART-001 |
| REQ-02 | COND-CART-02 | TS-CART-AGGREGATE | TC-CART-002, TC-CART-003 |
| REQ-02 | COND-CART-01 | TS-CART-INVALID | TC-CART-004, TC-CART-005, TC-CART-006, TC-CART-007 |
| REQ-07 | COND-PROMO7-01 | TS-PROMO7-INVALID | TC-PROMO7-001, TC-PROMO7-006 |
| REQ-07 | COND-PROMO7-01 | TS-PROMO7-USED | TC-PROMO7-002, TC-PROMO7-005 |
| REQ-07 | COND-PROMO7-02 | TS-PROMO7-SUCCESS | TC-PROMO7-003, TC-PROMO7-007 |
| REQ-07 | COND-PROMO7-02 | TS-PROMO7-DECLINED | TC-PROMO7-004 |
| REQ-09 | COND-SHIP-01 | TS-SHIP-INNER-THRESHOLD | TC-SHIP-001, TC-SHIP-002, TC-SHIP-003, TC-SHIP-006 |
| REQ-09 | COND-SHIP-02 | TS-SHIP-OUTER | TC-SHIP-004, TC-SHIP-005 |
| REQ-10 | COND-PAY-01 | TS-PAY-COD | TC-PAY-001, TC-PAY-002 |
| REQ-10 | COND-PAY-02 | TS-PAY-ONLINE-APPROVED | TC-PAY-003, TC-PAY-004 |
| REQ-10 | COND-PAY-02 | TS-PAY-ONLINE-DECLINED | TC-PAY-005, TC-PAY-006 |
| REQ-15 | COND-INV15-01 | TS-INV15-REJECT | TC-INV15-001, TC-INV15-002, TC-INV15-003, TC-INV15-006 |
| REQ-15 | COND-INV15-02 | TS-INV15-SUCCESS | TC-INV15-004, TC-INV15-005, TC-INV15-007 |

## C. Detailed cases and traceability

The CSV is the canonical executable detailed test-case artifact. It contains: test_case_id, REQ/COND/TS, title, priority, precondition, fixture_key, test_steps, input_json, expected_type, expected_json, execution fields.
Execution fields in the input file stay empty; the runner writes separate files under `reports/`. `traceability_design.csv` lists REQ→COND→TS→TC; `reports/traceability_execution.csv` adds RUN→status after execution.

| TC | REQ | Condition | Scenario | Kind | Input | Expected |
|---|---|---|---|---|---|---|
| TC-CART-001 | REQ-02 | COND-CART-02 | TS-CART-VALID | positive | `{"actions":[["A",1]]}` | `{"exception":null,"lines":[{"sku":"A","quantity":1}],"subtotal":"200000"}` |
| TC-CART-002 | REQ-02 | COND-CART-02 | TS-CART-AGGREGATE | positive | `{"actions":[["A",2],["A",3]]}` | `{"exception":null,"lines":[{"sku":"A","quantity":5}],"subtotal":"1000000"}` |
| TC-CART-003 | REQ-02 | COND-CART-02 | TS-CART-AGGREGATE | positive | `{"actions":[["A",1],["B",2]]}` | `{"exception":null,"lines":[{"sku":"A","quantity":1},{"sku":"B","quantity":2}],"subtotal":"800000"}` |
| TC-CART-004 | REQ-02 | COND-CART-01 | TS-CART-INVALID | boundary | `{"actions":[["A",0]]}` | `{"exception":"ValueError:INVALID_QUANTITY","lines":[],"subtotal":"0"}` |
| TC-CART-005 | REQ-02 | COND-CART-01 | TS-CART-INVALID | negative | `{"actions":[["A",-1]]}` | `{"exception":"ValueError:INVALID_QUANTITY","lines":[],"subtotal":"0"}` |
| TC-CART-006 | REQ-02 | COND-CART-01 | TS-CART-INVALID | negative | `{"actions":[["A",1.5]]}` | `{"exception":"ValueError:INVALID_QUANTITY","lines":[],"subtotal":"0"}` |
| TC-CART-007 | REQ-02 | COND-CART-01 | TS-CART-INVALID | negative | `{"actions":[["A","2"]]}` | `{"exception":"ValueError:INVALID_QUANTITY","lines":[],"subtotal":"0"}` |
| TC-PROMO7-001 | REQ-07 | COND-PROMO7-01 | TS-PROMO7-INVALID | negative | `{"mode":"discount","voucher":"FAKE"}` | `{"exception":"ValueError:INVALID_VOUCHER","used_codes":[],"order_count":0}` |
| TC-PROMO7-002 | REQ-07 | COND-PROMO7-01 | TS-PROMO7-USED | negative | `{"mode":"discount","voucher":"SAVE10","setup_used":true}` | `{"exception":"ValueError:VOUCHER_USED","used_codes":["SAVE10"],"order_count":0}` |
| TC-PROMO7-003 | REQ-07 | COND-PROMO7-02 | TS-PROMO7-SUCCESS | positive | `{"mode":"checkout","voucher":"SAVE10","method":"COD","approved":true}` | `{"exception":null,"used_codes":["SAVE10"],"order_count":1,"payment_status":"PENDING_COD"}` |
| TC-PROMO7-004 | REQ-07 | COND-PROMO7-02 | TS-PROMO7-DECLINED | negative | `{"mode":"checkout","voucher":"SAVE10","method":"ONLINE","approved":false}` | `{"exception":"ValueError:PAYMENT_DECLINED","used_codes":[],"order_count":0,"payment_status":null}` |
| TC-PROMO7-005 | REQ-07 | COND-PROMO7-01 | TS-PROMO7-USED | negative | `{"mode":"reuse_after_success","voucher":"SAVE10"}` | `{"exception":"ValueError:VOUCHER_USED","used_codes":["SAVE10"],"order_count":1,"payment_status":null}` |
| TC-PROMO7-006 | REQ-07 | COND-PROMO7-01 | TS-PROMO7-INVALID | negative | `{"mode":"discount","voucher":"SAVE10","make_inactive":true}` | `{"exception":"ValueError:INVALID_VOUCHER","used_codes":[],"order_count":0}` |
| TC-PROMO7-007 | REQ-07 | COND-PROMO7-02 | TS-PROMO7-SUCCESS | positive | `{"mode":"checkout","voucher":"SAVE10","method":"ONLINE","approved":true}` | `{"exception":null,"used_codes":["SAVE10"],"order_count":1,"payment_status":"PAID"}` |
| TC-SHIP-001 | REQ-09 | COND-SHIP-01 | TS-SHIP-INNER-THRESHOLD | boundary | `{"subtotal":499999,"area":"inner"}` | `{"exception":null,"fee":"30000"}` |
| TC-SHIP-002 | REQ-09 | COND-SHIP-01 | TS-SHIP-INNER-THRESHOLD | boundary | `{"subtotal":500000,"area":"inner"}` | `{"exception":null,"fee":"0"}` |
| TC-SHIP-003 | REQ-09 | COND-SHIP-01 | TS-SHIP-INNER-THRESHOLD | boundary | `{"subtotal":500001,"area":"inner"}` | `{"exception":null,"fee":"0"}` |
| TC-SHIP-004 | REQ-09 | COND-SHIP-02 | TS-SHIP-OUTER | boundary | `{"subtotal":499999,"area":"outer"}` | `{"exception":null,"fee":"50000"}` |
| TC-SHIP-005 | REQ-09 | COND-SHIP-02 | TS-SHIP-OUTER | boundary | `{"subtotal":500000,"area":"outer"}` | `{"exception":null,"fee":"50000"}` |
| TC-SHIP-006 | REQ-09 | COND-SHIP-01 | TS-SHIP-INNER-THRESHOLD | positive | `{"subtotal":300000,"area":"inner"}` | `{"exception":null,"fee":"30000"}` |
| TC-PAY-001 | REQ-10 | COND-PAY-01 | TS-PAY-COD | positive | `{"method":"COD","approved":true}` | `{"exception":null,"status":"PENDING_COD","order_count":1,"charge_count":0}` |
| TC-PAY-002 | REQ-10 | COND-PAY-01 | TS-PAY-COD | positive | `{"method":"COD","approved":true}` | `{"exception":null,"status":"PENDING_COD","order_count":1,"charge_count":0}` |
| TC-PAY-003 | REQ-10 | COND-PAY-02 | TS-PAY-ONLINE-APPROVED | positive | `{"method":"ONLINE","approved":true}` | `{"exception":null,"status":"PAID","order_count":1,"charge_count":1}` |
| TC-PAY-004 | REQ-10 | COND-PAY-02 | TS-PAY-ONLINE-APPROVED | positive | `{"method":"ONLINE","approved":true}` | `{"exception":null,"status":"PAID","order_count":1,"charge_count":1}` |
| TC-PAY-005 | REQ-10 | COND-PAY-02 | TS-PAY-ONLINE-DECLINED | negative | `{"method":"ONLINE","approved":false}` | `{"exception":"ValueError:PAYMENT_DECLINED","status":null,"order_count":0,"charge_count":0}` |
| TC-PAY-006 | REQ-10 | COND-PAY-02 | TS-PAY-ONLINE-DECLINED | negative | `{"method":"ONLINE","approved":false}` | `{"exception":"ValueError:PAYMENT_DECLINED","status":null,"order_count":0,"charge_count":0}` |
| TC-INV15-001 | REQ-15 | COND-INV15-01 | TS-INV15-REJECT | negative | `{"actions":[["A",2],["B",100]],"method":"COD","approved":true}` | `{"exception":"ValueError:OUT_OF_STOCK","stock_after":{"A":20,"B":15,"C":12},"order_count":0,"charge_count":0}` |
| TC-INV15-002 | REQ-15 | COND-INV15-01 | TS-INV15-REJECT | negative | `{"actions":[["A",21],["B",2]],"method":"COD","approved":true}` | `{"exception":"ValueError:OUT_OF_STOCK","stock_after":{"A":20,"B":15,"C":12},"order_count":0,"charge_count":0}` |
| TC-INV15-003 | REQ-15 | COND-INV15-01 | TS-INV15-REJECT | negative | `{"actions":[["A",1],["C",13]],"method":"COD","approved":true}` | `{"exception":"ValueError:OUT_OF_STOCK","stock_after":{"A":20,"B":15,"C":12},"order_count":0,"charge_count":0}` |
| TC-INV15-004 | REQ-15 | COND-INV15-02 | TS-INV15-SUCCESS | boundary | `{"actions":[["A",20],["B",15]],"method":"COD","approved":true}` | `{"exception":null,"stock_after":{"A":0,"B":0,"C":12},"order_count":1,"charge_count":0}` |
| TC-INV15-005 | REQ-15 | COND-INV15-02 | TS-INV15-SUCCESS | positive | `{"actions":[["A",1],["B",2]],"method":"COD","approved":true}` | `{"exception":null,"stock_after":{"A":19,"B":13,"C":12},"order_count":1,"charge_count":0}` |
| TC-INV15-006 | REQ-15 | COND-INV15-01 | TS-INV15-REJECT | boundary | `{"actions":[["B",16],["C",1]],"method":"COD","approved":true}` | `{"exception":"ValueError:OUT_OF_STOCK","stock_after":{"A":20,"B":15,"C":12},"order_count":0,"charge_count":0}` |
| TC-INV15-007 | REQ-15 | COND-INV15-02 | TS-INV15-SUCCESS | positive | `{"actions":[["C",2],["A",1]],"method":"COD","approved":true}` | `{"exception":null,"stock_after":{"A":19,"B":15,"C":10},"order_count":1,"charge_count":0}` |

## D. Design counts

- Selected REQs: REQ-02, REQ-07, REQ-09, REQ-10, REQ-15
- Cases per requirement: REQ-02: 7, REQ-07: 7, REQ-09: 6, REQ-10: 6, REQ-15: 7
- Total: 33 cases
- Case kinds: positive=12, boundary=8, negative=13
- Each REQ has >=2 conditions, >=2 scenarios and >=3 cases. Negative/boundary >=5.

## E. Gaps and risks, not assumed acceptance criteria

- [ ] Ask BA/PO whether boolean quantity True is acceptable; source code `isinstance(True, int)` yields True in Python, but current tests do not impose an unconfirmed interpretation.
- [ ] Price freeze at add vs checkout is **not specified** (Part 3.4); do not silently choose an oracle.
- [ ] Network failure, concurrency and persistence are outside the in-memory model; risk noted but not asserted as covered.
- [ ] The chosen cases do not replace standalone validation of worked example REQ-06/08/11.

## F. Two untested risks if current selected suite has zero FAIL

1. **Concurrent inventory reservations:** in-memory sequential reserve checks are not proof against two requests racing on the same SKU; the model has no database lock/concurrency simulation.
2. **Changing product prices between add-to-cart and checkout:** acceptance rules do not determine which price to lock; the resulting order amount cannot be objectively judged before a BA/PO decision.

These are disclosures for the assignment’s conditional no-FAIL branch, **not claims of existing defects**.
