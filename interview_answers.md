# STLab02 – Part 4: Interview Questions & Code Review (nội dung trả lời)

**Nguồn câu hỏi:** Requirement, Phần 4, các câu 1–20 và Code Interview A–C. Ví dụ minh họa bám EduCommerce gốc, không thay thế kết quả thực thi Part 1.

## 1. Requirement, Condition, Scenario, Case, Execution khác nhau ra sao?
Requirement (REQ-09) là quy tắc nghiệp vụ: nội thành miễn ship từ 500k. Test Condition là điều kiện phải kiểm tra, ví dụ biên subtotal. Test Scenario nói **cái gì** cần thử: nội thành ngay dưới, bằng và trên 500k. Test Case đưa dữ liệu cụ thể (499999, inner), bước gọi hàm và expected 30000. Test Execution ghi actual, PASS/FAIL/BLOCKED cùng thời điểm chạy.

## 2. Test oracle là gì? Vì sao không lấy actual làm expected?
Test oracle là căn cứ xác định hành vi đúng. Với EduCommerce, oracle là acceptance criteria và các quy tắc đã làm rõ, không phải output hiện tại của `Shipping.calculate()`. Nếu code đang sai dấu `>=` thành `>`, sao chép actual sang expected sẽ che giấu bug. Khi requirement thiếu thông tin, phải ghi câu hỏi làm rõ thay vì tự đoán.

## 3. EP và BVA trong Pricing/Shipping?
Equivalence Partitioning (EP) nhóm dữ liệu kỳ vọng xử lý giống nhau: nội thành dưới 500k, nội thành từ 500k trở lên, ngoại thành. Boundary Value Analysis (BVA) chọn dữ liệu 499999, 500000, 500001 để kiểm điều kiện `>=`. Với số tiền, sử dụng `Decimal` để xác định các giá trị chính xác; test oracle phải bám cách tính và đơn vị tiền mà đề nêu.

## 4. Positive, negative và edge với Cart.add()?
Positive: `add('A',2)` tạo dòng A qty2. Negative: `add('A',-1)` phải bị từ chối `INVALID_QUANTITY`. Edge: `add('A',0)` ở ranh giới nhỏ nhất phải bị từ chối, còn `add('A',1)` hợp lệ. Sau thao tác lỗi, nên kiểm tra giỏ không bị thay đổi.

## 5. Fixture là gì? Vì sao cần riêng cho mỗi case?
Fixture là tập dữ liệu và object được khởi tạo trước test: `Checkout`, `Customer`, `Cart` và sản phẩm/stock mẫu. Tạo fixture mới mỗi case bảo đảm expected chỉ phụ thuộc test data hiện tại, không phụ thuộc thứ tự các case. Ví dụ một test payment trừ stock không thể ảnh hưởng test inventory chạy sau.

## 6. Test isolation khác reset sau test thế nào?
Isolation là yêu cầu rằng các test không ảnh hưởng nhau. Tạo object mới trước mỗi test là cách đạt isolation ngay từ đầu. Reset sau test là chiến lược dọn state nhưng có thể thất bại nếu test crash giữa chừng; do đó cách tạo fixture độc lập dễ tin cậy hơn trong hệ thống in-memory này.

## 7. ValueError expected là PASS hay FAIL?
Runner phải đọc oracle của case. Nếu expected là `ValueError('INVALID_QUANTITY')`, nhận đúng loại lỗi và thông điệp mới là PASS. Nếu không raise, raise lỗi khác, hoặc raise khi expected success thì FAIL. Nếu input CSV không đọc được hoặc fixture_key không hợp lệ, đó là vấn đề test setup nên phân loại BLOCKED thay vì quy cho sản phẩm.

## 8. Vì sao chỉ kiểm return value chưa đủ?
`Checkout.place()` có thể trả về Order hợp lệ nhưng vẫn trừ stock sai hoặc charge thêm. Vì vậy phải kiểm trạng thái sau thao tác phù hợp REQ: inventory stock, số order, `Payments.charges`, `Customer.used_codes` và `by_key`. Trường hợp payment declined cần đảm bảo không tạo order; hoàn tồn kho thuộc REQ-08 và cần test riêng.

## 9. Tại sao dùng Decimal thay float?
`float` lưu số nhị phân xấp xỉ nên các phép tính tiền có thể xuất hiện sai số; `Decimal('0.1')` lưu số thập phân chính xác theo dữ liệu đầu vào. EduCommerce dùng `money()` với `ROUND_HALF_UP` để làm tròn khi tính discount. Cần thống nhất mức làm tròn (ở đây đến VND nguyên) theo rule, không dùng `float` rồi so sánh trực tiếp.

## 10. Data-driven testing là gì?
Một hàm runner đọc nhiều dòng CSV, mỗi dòng quy định một TC gồm input và expected khác nhau. `test_case_id` dùng nhận dạng, `requirement_id` xác định logic dispatch, `fixture_key` tạo môi trường mới, `input_json` chứa tham số, `expected_json` là oracle. Runner xuất một `RUN-...` cho mỗi TC, giữ liên kết REQ→COND→TS→TC→RUN.

## 11. Traceability Matrix phục vụ gì?
Ma trận liên kết từ acceptance rule đến các condition, scenario, testcase và run. Nó giúp chứng minh coverage và phát hiện requirement chưa có test. Khi ngưỡng shipping đổi, có thể truy ngược các TC gắn REQ-09 để biết dữ liệu, expected và hồi quy cần cập nhật. Coverage chỉ có ý nghĩa nếu link đúng, không chỉ đếm số dòng.

## 12. Priority test case khác Severity defect?
Priority là mức ưu tiên chạy/sửa theo thời gian hoặc rủi ro. Severity là mức tác động của lỗi khi xảy ra. Một lỗi làm lệch tiền có thể severity cao; việc sửa trước hay sau còn phụ thuộc xác suất, phạm vi ảnh hưởng và release. Một lỗi hiển thị nhỏ nhưng xảy ra liên tục có thể được ưu tiên xử lý sớm dù severity thấp.

## 13. Unit, Integration, System và Checkout.place()?
Unit test nhắm vào một đơn vị nhỏ như `Shipping.calculate()`; integration test kiểm tương tác giữa nhiều module. `Checkout.place()` sử dụng Cart, Promotions, Shipping, Inventory và Payments, nên trong EduCommerce in-memory nó gần với kiểm thử tích hợp ở cấp service. Không gọi là system test end-to-end với UI/database thật vì mẫu ứng dụng không có những thành phần đó.

## 14. COD/ONLINE có state transition nào?
COD đặt thành công trả `PENDING_COD`, nghĩa là chưa thu tiền trực tuyến. ONLINE chỉ thành `PAID` khi `approved=True`; declined phải raise `PAYMENT_DECLINED` và không tạo order. Test cần quan sát `order.status`, số order và `Payments.charges`. Không suy diễn rằng `PENDING_COD` tương đương đã thu tiền.

## 15. Idempotency trong checkout là gì?
Idempotency nghĩa là xử lý lại cùng request/key không tạo thêm tác động mới sau lần thực hiện đầu. Không chỉ tránh duplicate order: còn phải tránh trừ stock và ghi charge hai lần. Vì vậy cần so order count, stock và payment charges trước/sau retry. REQ-11 là worked example trong Instruction, không nằm trong năm REQ tự chọn của Part 1.

## 16. Phân biệt FAIL sản phẩm và FAIL test script/fixture?
Đầu tiên xác minh acceptance rule và dữ liệu expected. Sau đó tái chạy trong fixture mới với input tối giản, kiểm lại cách dispatch/compare. Nếu runner parse nhầm CSV hoặc dùng fixture sai thì đây là lỗi test, không nên mở defect sản phẩm. Chỉ kết luận bug khi hành vi thực tế vi phạm oracle hợp lệ và có chứng cứ từ source/trạng thái.

## 17. Gradio dashboard có thay raw log không?
Không. Dashboard tổng hợp tốt nhưng có thể che mất dòng lỗi, thông tin exception hoặc số case bị bỏ qua. Evidence cần gồm raw execution CSV/log, thời điểm chạy, các case ID và dữ liệu liên quan. Lab 02 đã chốt HTML thay Gradio, nhưng nguyên tắc không thay raw log là như nhau.

## 18. Sanity và Regression sau sửa bug?
Sanity kiểm nhanh xem phần vừa sửa hoạt động ở đường đi chủ đạo, ví dụ shipping tại 500k. Regression chạy những test có nguy cơ chịu tác động: 499999/500000/500001, các case outer và checkout total. So sánh trước/sau, không điều chỉnh expected cho theo chương trình nếu requirement không đổi.

## 19. Repository cần gì để tái hiện Colab?
Tối thiểu có `ecommerce_app.py`, `test_runner.py`, `test_cases.csv`, notebook và README chỉ cách upload/chạy. Kết quả CSV và dashboard nên lưu kèm thông tin phiên chạy, phiên bản Python và dependency. Không commit token, mật khẩu hoặc dữ liệu cá nhân nhạy cảm. Người đọc cần biết đâu là source gốc, đâu là code test do sinh viên viết.

## 20. Chỉ có thời gian chạy 5 case, chọn theo risk?
Ưu tiên những nơi có tác động nghiệp vụ lớn và khả năng lỗi cao: inventory atomicity với A đủ/B thiếu; online declined không tạo order; voucher không bị dùng khi thanh toán thất bại; phí ship tại đúng 500k; cart gộp SKU hai lần. Đây chỉ là thứ tự ưu tiên khi bị giới hạn thời gian; không thay thế định mức tối thiểu 15 case của bài nộp.

---

# 4.1. Code Interview – Phân tích/sửa lỗi

## A — Exception oracle

**Vấn đề:** Runner coi mọi `ValueError` là FAIL nên tạo false negative khi lỗi là hành vi dự kiến.

**Điều chỉnh:** Phân biệt expected là success hoặc expected exception. Nếu exception đã được dự kiến, kiểm cả loại và message; nếu khớp, PASS. Nếu không có exception như kỳ vọng hoặc nhận exception khác thì FAIL.

```python
try:
    cart.add('A', 0)
    actual_error = None
except ValueError as error:
    actual_error = str(error)

assert actual_error == 'INVALID_QUANTITY'
```

Trường `expected_json` phải chứa oracle lỗi, chẳng hạn `{"exception":"ValueError:INVALID_QUANTITY"}`. Dữ liệu CSV parse lỗi hoặc fixture_key sai cần phân loại BLOCKED; đó không phải exception nghiệp vụ được mong đợi.

## B — False positive vì chỉ kiểm order_id

**Vấn đề:** `assert order.order_id is not None` chỉ kiểm có ID, không kiểm các điều kiện cốt lõi; có thể PASS dù trừ stock sai hoặc tính tổng tiền sai.

**Các assertion bổ sung (trên một fixture mới, theo acceptance criteria):**

```python
app, customer, cart = fixture('600k')  # A: 3 x 200000
before = app.catalog.get('A').stock
order = app.place(customer, cart, method='COD', key='CHECK-ONE')
assert order.order_id is not None
assert order.total == Decimal('600000')  # no voucher, free inner shipping
assert order.status == 'PENDING_COD'
assert app.catalog.get('A').stock == before - 3
assert len(app.orders) == 1
assert len(app.payments.charges) == 0
```

`fixture` và `Decimal` cần import từ `ecommerce_app`/`decimal` tương ứng trong code thực tế. Nếu có voucher, expected total phải được tính từ rule discount/shipping đúng và dữ liệu của case, không copy giá trị actual.

## C — Shared fixture

**Vấn đề:** Một instance `Checkout()` dùng chung cho các case làm lẫn `catalog.products`, `customer.used_codes`, `orders`, `payments.charges`. Kết quả có thể phụ thuộc thứ tự chạy.

**Cách kiểm:** cho TC đầu trừ stock hoặc đổi giá, chạy TC sau; đảo thứ tự và so sánh. Nếu expected thay đổi vì lịch sử các TC, fixture chưa độc lập.

**Cách sửa:** gọi `fixture()`/`fresh_state()` **bên trong vòng lặp thực thi từng case**. Không đặt một `Checkout()` toàn cục cho cả suite. Khi cần cùng một sequence trong một test, giữ state trong chính test đó, không dùng chung xuyên test. Runner P6 khởi tạo fixture cho từng dòng CSV.
