# STLab02 – Requirement Analysis & Test Design

**Nguồn yêu cầu:** STLab02 Requirement (Phần 1) và STLab02 Instruction (mục 1.2, 2.6).
**Phạm vi đã chốt:** REQ-02, REQ-07, REQ-09, REQ-10, REQ-15. REQ-06/08/11 là ví dụ có sẵn trong Instruction, không thuộc bộ yêu cầu được lựa chọn.

## A. Phân tích yêu cầu

| REQ | Module | Tác nhân | Quy tắc chấp nhận | Điều kiện trước | Đầu vào | Kết quả/oracle | Rủi ro | Điểm cần làm rõ |
|---|---|---|---|---|---|---|---|---|
| REQ-02 | Cart | Customer | quantity là số nguyên dương; cùng SKU được cộng dồn | Cart có catalog hợp lệ | SKU và quantity của từng lần add | CartLine và subtotal hoặc INVALID_QUANTITY | Số lượng sai vẫn thay giỏ; trùng SKU thành nhiều dòng | Có cần chặn bool? Python coi True là int; cần BA/PO xác nhận nếu mở rộng. |
| REQ-07 | Promotion | Customer | Voucher không hợp lệ/used phải bị từ chối; chỉ đánh dấu used sau khi tạo order thành công | Mã voucher, customer và giỏ hợp lệ | voucher, customer.used_codes, kết quả payment | Voucher exception, used_codes, số order | Mã bị consume khi declined; tái dùng mã đã used | Phạm vi REQ-07 không mặc định bao gồm chính sách ngưỡng SAVE10 của REQ-06. |
| REQ-09 | Shipping | Customer | inner miễn phí từ subtotal 500000; dưới đó 30000; outer 50000 | Có subtotal Decimal và area | subtotal và area | shipping fee Decimal | Sai dấu biên hoặc phân loại vùng | Quy tắc area khác inner/outer không định nghĩa cho nhóm REQ này; không tự khẳng định. |
| REQ-10 | Payments | Customer | COD=PENDING_COD; ONLINE approved mới PAID; declined không tạo order | Customer authenticated và cart có hàng | method, approved, key | order status, số order, số charge hoặc PAYMENT_DECLINED | Tạo order khi declined; ghi charge sai | Rollback stock sau declined thuộc REQ-08 worked example, không gán nhầm cho REQ-10. |
| REQ-15 | Inventory | Customer | Nếu bất kỳ SKU thiếu stock phải từ chối toàn đơn, SKU khác không bị trừ | Giỏ có nhiều SKU và stock xác định | SKU, quantity, tồn kho ban đầu | OUT_OF_STOCK/Order; tồn kho của toàn bộ SKU | Trừ SKU đủ trước khi phát hiện SKU thiếu | Atomicity ở đây là mô hình in-memory tuần tự, không chứng minh concurrency. |

## B. Cấu trúc Test Condition → Test Scenario

Test Condition xác định khía cạnh hoặc trạng thái cần kiểm tra. Test Scenario diễn đạt **điều gì cần kiểm thử**; dữ liệu cụ thể và expected tương ứng được ghi trong `test_cases.csv`.

| Yêu cầu | Điều kiện | Tình huống | Test case |
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

## C. Test case chi tiết và truy vết

CSV là nguồn dữ liệu chi tiết của bộ test có thể thực thi. Các trường gồm `test_case_id`, REQ/COND/TS, `title`, `priority`, `precondition`, `fixture_key`, `test_steps`, `input_json`, `expected_type`, `expected_json` và các trường kết quả chạy.
Các trường kết quả trong CSV đầu vào được để trống; runner ghi dữ liệu vào các file riêng thuộc `reports/`. `traceability_design.csv` thể hiện REQ → COND → TS → TC; `reports/traceability_execution.csv` bổ sung RUN và trạng thái sau khi chạy.

| TC | REQ | Điều kiện | Tình huống | Loại | Đầu vào | Expected |
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

## D. Thống kê thiết kế

- Các REQ được chọn: REQ-02, REQ-07, REQ-09, REQ-10, REQ-15
- Số test case theo từng REQ: REQ-02: 7, REQ-07: 7, REQ-09: 6, REQ-10: 6, REQ-15: 7
- Tổng cộng: 33 test case
- Phân loại case: positive=12, boundary=8, negative=13
- Mỗi REQ có tối thiểu 2 conditions, 2 scenarios và 3 test cases; số case negative/boundary ít nhất 5.

## E. Điểm chưa rõ và rủi ro (không tự xem là quy tắc chấp nhận)

- [ ] Hỏi BA/PO liệu `True` có được chấp nhận làm số lượng hay không. Trong Python, `isinstance(True, int)` trả về `True`; bộ test hiện chưa tự áp đặt cách hiểu chưa được xác nhận.
- [ ] Chưa xác định thời điểm cố định giá: khi thêm vào giỏ hay khi checkout (Phần 3.4). Không tự chọn oracle nếu thiếu quy tắc.
- [ ] Lỗi mạng, xử lý đồng thời và lưu trữ lâu dài nằm ngoài mô hình in-memory; ghi nhận rủi ro nhưng không tuyên bố đã kiểm thử.
- [ ] Bộ test mới không thay thế việc kiểm chứng riêng những REQ mẫu 06/08/11.

## F. Hai rủi ro chưa kiểm thử khi bộ test không có FAIL

1. **Hai yêu cầu giữ hàng đồng thời:** kiểm tra tồn kho tuần tự trong bộ nhớ không chứng minh được tính đúng khi hai yêu cầu cạnh tranh cùng SKU; mô hình không có cơ chế khóa cơ sở dữ liệu hoặc mô phỏng concurrency.
2. **Giá sản phẩm thay đổi giữa khi thêm giỏ và checkout:** acceptance criteria chưa xác định phải giữ giá ở thời điểm nào; chưa thể đánh giá khách quan tổng tiền đơn hàng nếu BA/PO chưa làm rõ.

Đây là hai rủi ro được trình bày theo nhánh yêu cầu khi không có FAIL; **không phải kết luận rằng ứng dụng đã có hai bug này**.
