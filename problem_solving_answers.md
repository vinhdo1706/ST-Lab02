# STLab02 – Part 3: Problem Solving (nội dung trả lời tám tình huống)

**Nguồn đề:** `STLab02 - Test Case Execution (Requirement)(1).docx`, Part 3, mục 3.1–3.8.  
**Nguồn hệ thống:** `STLab02 - Test Case Execution (Instruction)(1).docx`, EduCommerce gốc tại mục 2.6.  
Các test case trong phần giải quyết tình huống minh họa các phương án kiểm thử được đề xuất; chúng được phân biệt với 33 test case đã thực thi của Phần 1 trong `test_cases.csv`. Các thay đổi về mã nguồn nêu tại đây là phương án phân tích, chưa được áp dụng vào ứng dụng gốc.

## 3.1. Hai SKU, một SKU thiếu tồn kho

**Nguyên nhân/risk:** Checkout chứa A=2 (stock 20) và B=100 (stock 15). Một SKU thiếu hàng phải làm toàn bộ giao dịch thất bại. Nếu `Inventory.reserve` trừ A trước rồi mới phát hiện B thiếu, A sẽ bị trừ sai mặc dù không có đơn. Với source gốc, `Inventory.reserve()` duyệt kiểm tra tồn kho của **tất cả** SKU rồi mới trừ; đó là cơ chế bảo vệ atomicity trong phạm vi mô phỏng tuần tự, không phải giao dịch DB thật.

**File/function:** `ecommerce_app.py` → `Inventory.reserve(lines)`; đường gọi `Checkout.place()`. **Thay đổi dự kiến nếu lỗi xuất hiện:** kiểm tra khả năng đáp ứng mọi dòng hàng trước khi thay đổi bất kỳ stock nào; khi có failure khác sau khi reserve thì cần xử lý release/rollback tương ứng theo REQ-08 (một yêu cầu mẫu riêng). Không tự sửa khi chưa tái hiện lỗi.

| Case đề xuất | Dữ liệu / các bước | Expected theo REQ-15 | Evidence cần thu |
|---|---|---|---|
| PS31-TC01 | Fixture mới, A=2, B=100; lưu stock A20/B15; checkout COD | `OUT_OF_STOCK`; không có order; A20/B15 không đổi | Test input, exception, stock before/after, code `reserve()` |
| PS31-TC02 | Fixture mới, A=20, B=15; checkout COD | Thành công, một order; A0/B0 | Order và stock before/after; case dữ liệu biên |

**Không suy rộng:** Mô hình này chưa chứng minh tính nguyên tử khi hai request chạy đồng thời.

## 3.2. Voucher chỉ đánh dấu `used` sau thành công

**Nguyên nhân/risk:** Online payment declined thì chưa có đơn thành công. Nếu `Customer.used_codes` đã thêm `SAVE10` trước đó, khách mất quyền dùng voucher dù giao dịch không thành công. `Checkout.place()` phải chỉ cập nhật voucher sau khi tạo đơn hợp lệ. Trong source gốc, dòng `customer.used_codes.add(voucher)` nằm sau tạo `Order`, nhưng hậu quả về tồn kho khi payment failure thuộc REQ-08 và phải kiểm tra riêng.

**File/function:** `ecommerce_app.py` → `Checkout.place()`, `Promotions.discount()` và `Payments.collect()`. **Thay đổi dự kiến khi có lỗi:** chỉ ghi used_codes sau commit thành công; bảo toàn used_codes ở mọi nhánh thất bại; nếu có giao dịch DB thực phải coi đây là cùng một giao dịch logic.

| Case đề xuất | Dữ liệu / các bước | Expected theo REQ-07 | Evidence cần thu |
|---|---|---|---|
| PS32-TC01 | Fixture 600k; `SAVE10`; ONLINE, `approved=False`; so used_codes trước/sau | `PAYMENT_DECLINED`; 0 order; voucher **chưa used** | Input, exception, used_codes, orders |
| PS32-TC02 | Fixture 600k; `SAVE10`; COD thành công; thử voucher lần hai với key khác | Đơn đầu thành công, mã đánh dấu used; lần hai `VOUCHER_USED`, không thêm order | Log hai thao tác, trạng thái mã, danh sách order |

## 3.3. Mã thanh toán lạ `WALLET`

**Nguyên nhân/risk:** Nếu checkout reserve hàng trước khi xác thực phương thức thanh toán, `WALLET` có thể làm stock giảm rồi bị `Payments.collect()` từ chối, tạo side effect sai. Source gốc hiện gọi `Inventory.reserve()` trước khi kiểm tra method trong `Payments.collect()`; đó là một rủi ro cần tái hiện độc lập nếu giải quyết/triển khai tình huống.

**File/function:** `ecommerce_app.py` → `Checkout.place()`, `Payments.collect()`, `Inventory.reserve()`. **Thay đổi dự kiến:** validate `method in ('COD','ONLINE')` trước mọi biến đổi stock/payment; hoặc bảo đảm rollback toàn bộ nếu validation xảy ra sau reserve. Không tự bật hỗ trợ WALLET vì đề yêu cầu từ chối phương thức lạ (REQ-16).

| Case đề xuất | Dữ liệu / các bước | Expected | Evidence cần thu |
|---|---|---|---|
| PS33-TC01 | Fixture 600k, `method='WALLET'`; lưu stock và orders trước khi đặt | `INVALID_PAYMENT_METHOD`; 0 order; 0 charges; stock giữ nguyên | Exception, state before/after, code trình tự |
| PS33-TC02 | Cùng dữ liệu nhưng `method='COD'` trên fixture mới | `PENDING_COD`; tạo một order; stock trừ đúng số lượng | Log order, payments, stock; đối chứng phương thức hợp lệ |

## 3.4. Giá sản phẩm thay đổi giữa add-to-cart và checkout

**Nguyên nhân/risk:** `Cart` chỉ giữ `(sku, quantity)`; `Cart.subtotal()` tra `Catalog.get(sku).price` tại thời điểm được gọi. Giá B tăng sau khi add thì subtotal lúc checkout có thể khác lúc khách bỏ hàng vào giỏ. **REQ hiện tại chưa xác định thời điểm cố định giá**; không được tự đưa ra expected mới như một business rule đã được phê duyệt.

**File/function chịu ảnh hưởng:** `Cart.add()`, `Cart.subtotal()`, `Catalog.get()`, `Checkout.place()`, và dữ liệu order. **Câu hỏi BA/PO:** Giá được cố định khi thêm vào giỏ, khi checkout hay khi xác nhận đặt hàng? Nếu giá đổi, người mua có cần được thông báo/đồng ý lại không? Có TTL hoặc price version không?

**Thay đổi dự kiến theo câu trả lời:** Nếu chốt tại add-to-cart thì lưu snapshot giá ở cart line; nếu chốt tại checkout thì dùng giá hiện hành, thông báo trước xác nhận. Chưa sửa code vì chưa có căn cứ chọn phương án.

| Case đề xuất | Dữ liệu / các bước | Expected có điều kiện | Evidence cần thu |
|---|---|---|---|
| PS34-TC01 | Add B qty=1 khi 300k, đổi B thành 350k rồi checkout | **Chờ BA/PO**: 300k nếu giá chốt ở add; 350k nếu giá chốt tại checkout, trước shipping | Price trước/sau, subtotal, order total, quyết định BA/PO |
| PS34-TC02 | Add A+B, đổi giá B tại đúng ngưỡng miễn ship (subtotal từ 500k thành 450k) | **Chờ BA/PO** về giá chốt; shipping áp ngưỡng cho subtotal chính thức được chọn | Cart, giá, subtotal, shipping, acceptance clarification |

**Không kết luận PASS/FAIL** trước khi làm rõ oracle.

## 3.5. Cùng SKU nhập hai lần

**Nguyên nhân/risk:** Nếu `Cart.add()` tạo hai dòng riêng cho A thay vì cộng dồn, điều kiện stock và subtotal có thể bị đánh giá sai. Source gốc tìm dòng theo SKU và tăng `quantity` nếu đã tồn tại. Lưu ý kiểm tra ranh giới số lượng: REQ-02 yêu cầu số nguyên dương; số tồn kho là điều kiện ở bước reserve chứ không tự động là giới hạn trên khi thêm vào giỏ.

**File/function:** `Cart.add()`, `Cart.subtotal()`, `Inventory.reserve()`. **Thay đổi dự kiến nếu lỗi:** gộp theo SKU duy nhất; validate quantity trước khi thay đổi giỏ; không âm thầm biến quantity sai thành quantity hợp lệ.

| Case đề xuất | Dữ liệu / các bước | Expected | Evidence cần thu |
|---|---|---|---|
| PS35-TC01 | Add A=2, add A=3 | Một dòng A qty=5; subtotal 1.000.000 | `cart.lines`, subtotal, code `Cart.add()` |
| PS35-TC02 | Add A=2 rồi add A=0 | `INVALID_QUANTITY`; giỏ vẫn có một dòng A qty=2 | Exception, cart before/after |
| PS35-TC03 | Add A=20 rồi add A=1; sau đó checkout | Cart có một dòng A qty=21; checkout `OUT_OF_STOCK`, không trừ stock | Cart, lỗi checkout và stock before/after |

## 3.6. Data-driven tests bị phụ thuộc nhau

**Nguyên nhân/risk:** Nếu nhiều case dùng chung `Checkout`, `Catalog`, `Customer` hay `Cart`, case trước có thể thay stock, price, `used_codes`, `charges` hoặc `by_key`. Case sau phụ thuộc thứ tự chạy, gây false FAIL hoặc false PASS. Đây là lỗi thiết kế test fixture chứ chưa phải bug ứng dụng.

**File/function:** `test_runner.py` → khởi tạo fixture trước mỗi dòng; trong source mẫu `ecommerce_app.py` → `fixture()`. **Thay đổi dự kiến:** tạo `Checkout`, `Customer`, `Cart` độc lập cho từng TC; không dùng service global hoặc giữ object từ lần chạy trước. Kiểm tra khi đảo thứ tự case.

| Case đề xuất | Dữ liệu / các bước | Expected | Evidence cần thu |
|---|---|---|---|
| PS36-TC01 | TC-A đổi giá B thành 450k; TC-B mới dùng fixture 300k | TC-B vẫn thấy giá B=300k; không kế thừa giá của TC-A | ID fixture, before/after state, runner log |
| PS36-TC02 | TC-A checkout A qty=3; TC-B mới kiểm stock A ban đầu | TC-B nhìn thấy A stock=20, không bị trừ xuống 17 từ TC-A | Stock ở từng fixture, chạy đảo thứ tự |

## 3.7. Dashboard báo PASS dù thiếu test

**Nguyên nhân/risk:** CSV có 20 dòng, 3 dòng lỗi JSON và bị bỏ qua. Report chỉ còn 17 PASS. Dù `17/17 = 100%` cho **các case đã chạy**, không được báo `20/20 PASS` hoặc che giấu 3 case chưa chạy. Coverage theo dữ liệu gốc mới là 17/20; ba dòng còn lại phải được ghi BLOCKED (hoặc phân loại invalid data rõ ràng) thay vì biến mất.

**File/function:** `test_runner.py` → CSV reader, validation, evaluator, reporter; HTML dashboard. **Thay đổi dự kiến:** bắt lỗi parse ở cấp từng dòng, bảo toàn số dòng đã nạp, ghi trạng thái BLOCKED và lý do; tính `loaded = pass + fail + blocked`, báo riêng tỷ lệ thực thi và tỷ lệ đạt trong số case thực thi.

| Case đề xuất | Dữ liệu / các bước | Expected | Evidence cần thu |
|---|---|---|---|
| PS37-TC01 | CSV 20 dòng, 17 hợp lệ, 3 `input_json` lỗi | loaded=20, PASS=17, BLOCKED=3, FAIL=0; không xóa ba dòng | Input CSV, report từng case, tổng theo status |
| PS37-TC02 | CSV 20 dòng đều hợp lệ và chạy PASS | loaded=20, PASS=20, FAIL=0, BLOCKED=0 | CSV, execution log, HTML chart và bảng |

**Phân biệt công thức:** `pass_rate_executed = PASS/(PASS+FAIL)` nếu mẫu số dương; `execution_coverage = (PASS+FAIL)/loaded`. Trường hợp thứ nhất lần lượt là 100% và 85%, không đồng nghĩa hoàn tất bài.

## 3.8. Đổi ngưỡng miễn phí vận chuyển 500k → 700k

**Nguyên nhân/risk:** REQ-09 hiện miễn phí nội thành nếu subtotal >=500k. Đổi lên 700k ảnh hưởng trực tiếp acceptance rule, boundary tests, fixture subtotals, `Shipping.calculate()` và cả order total ở các flow checkout. Đây là một **giả định thay đổi yêu cầu trong bài Problem Solving**, không phải lệnh thay đổi source hay bộ kiểm thử hiện tại.

**File/function:** `ecommerce_app.py` → `Shipping.calculate()`; các REQ/COND/TS/TC liên quan shipping; `test_cases.csv`; logic tổng tiền ở `Checkout.place()`. **Thay đổi dự kiến nếu được phê duyệt:** thay ngưỡng chính thức thành 700k (ưu tiên cấu hình/hằng số phù hợp mức bài), cập nhật test data và expected; chạy regression cả shipping và checkout total.

| Case đề xuất | Dữ liệu / các bước | Expected *nếu REQ mới được thông qua* | Evidence cần thu |
|---|---|---|---|
| PS38-TC01 | `Shipping.calculate(699999,'inner')` | 30000 | Yêu cầu thay đổi, test, output, source |
| PS38-TC02 | `Shipping.calculate(700000,'inner')` | 0 | Dữ liệu boundary, test, code |
| PS38-TC03 | `Shipping.calculate(700001,'inner')` | 0 | Regression boundary |

**Regression impact:** mức 500k/600k trước đây được miễn phí nay chịu 30k; ngoại thành vẫn 50k. Phải cập nhật REQ-09, COND-SHIP-01, TS-SHIP-INNER-THRESHOLD, các TC-SHIP liên quan, fixture và kiểm tra order total. Không cập nhật expected của baseline 500k khi thay đổi chưa được phê duyệt.
