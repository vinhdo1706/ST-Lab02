# STLab02 – Phần 2: Giải thích mã kiểm thử

Tài liệu này giải thích cách hoạt động của những thành phần kiểm thử đã xây dựng. Các minh chứng E01–E10 sẽ được kiểm tra và hoàn thiện riêng; phần giải thích này không thay thế ảnh chụp hoặc nhật ký thực thi.

## 1. Mã nguồn ứng dụng ban đầu

`ecommerce_app.py` được lấy từ khối `%%writefile ecommerce_app.py` trong Instruction, mục 2.6, **không chỉnh sửa quy tắc nghiệp vụ**. Ứng dụng gồm các lớp Catalog, Cart, Inventory, Promotions, Shipping, Payments, Checkout và hàm `fixture()`. Bộ kiểm thử xác định expected từ tiêu chí chấp nhận, không sao chép hành vi hiện tại của chương trình làm chuẩn.

## 2. Fixture và dữ liệu chuẩn bị

`test_runner.fresh_state(fixture_key)` tạo `Checkout`, `Customer` và `Cart` mới cho **mỗi dòng test case**. Các fixture key được hỗ trợ là `empty`, `300k`, `499999`, `500k`, `600k`, `1000k`, `1500k`.

- Với `empty`, giỏ hàng rỗng; tồn kho khởi tạo là A=20, B=15, C=12.
- Với `300k`, giỏ có B=1; với `600k`, giỏ có A=3.
- Fixture độc lập tránh việc tồn kho, trạng thái voucher, đơn hàng hoặc giao dịch của case trước ảnh hưởng case sau.

## 3. Đọc CSV và kiểm tra dữ liệu

Runner sử dụng `pandas.read_csv(..., dtype=str, keep_default_na=False, encoding='utf-8-sig')` để đọc CSV và giữ nguyên ID cũng như các trường rỗng. `read_cases()` kiểm tra các cột bắt buộc. Với mỗi dòng, `evaluate()` kiểm tra TC ID trùng, sự phù hợp giữa REQ và `expected_type`, thông tin truy vết, rồi dùng `json.loads()` để đọc `input_json` và `expected_json`.

- Dòng dữ liệu sai được ghi là **BLOCKED**, vẫn có một dòng kết quả tương ứng.
- Nếu CSV thiếu các cột bắt buộc, toàn bộ lần chạy dừng với thông báo cụ thể và mã thoát 2; không báo PASS sai lệch.

## 4. Điều phối test case đến hàm nghiệp vụ

Hàm `run_business_case()` sử dụng `requirement_id` để chọn thao tác trên ứng dụng thật:

| REQ | Hàm được gọi | Kết quả và trạng thái cần kiểm |
|---|---|---|
| REQ-02 | `Cart.add()`, `Cart.subtotal()` | Ngoại lệ, SKU/số lượng từng dòng giỏ, subtotal. |
| REQ-07 | `Promotions.discount()` hoặc `Checkout.place()` | Lỗi voucher kỳ vọng, `customer.used_codes`, số đơn, trạng thái thanh toán. |
| REQ-09 | `Shipping.calculate(Decimal(subtotal), area)` | Phí vận chuyển chính xác. |
| REQ-10 | `Checkout.place()` | Trạng thái thanh toán, số đơn, số lần ghi nhận charge; declined không được tạo đơn. |
| REQ-15 | `Checkout.place()` / `Inventory.reserve()` | Tồn kho sau thao tác của các SKU, số đơn, số charge và ngoại lệ. |

Mỗi dòng CSV chỉ rõ `input_json` và `expected_json`. **Có Order ID không phải điều kiện PASS duy nhất**: các tác động phụ liên quan đến REQ cũng được kiểm tra.

## 5. Oracle, assertion và ngoại lệ mong đợi

`check_expected()` so sánh đệ quy các trường mà `expected_json` quy định với kết quả thực tế. Kết quả thực tế có thể chứa thêm dữ liệu chẩn đoán, nhưng không được thiếu hoặc làm sai các trường expected đã nêu.

Khi nghiệp vụ phát sinh `ValueError` được dự kiến, `run_business_case()` ghi dưới dạng `ValueError:MESSAGE` để đối chiếu. Vì vậy, nhận **đúng ngoại lệ mong đợi có thể là PASS**; không nhận ngoại lệ hoặc nhận ngoại lệ khác là FAIL.

## 6. Xử lý ngoại lệ và phân loại trạng thái

- **PASS:** Actual khớp mọi trường expected.
- **FAIL:** Hành vi nghiệp vụ không khớp oracle hợp lệ, hoặc ứng dụng phát sinh lỗi ngoài dự kiến khi dữ liệu test hợp lệ.
- **BLOCKED:** Không thể thực thi hoặc đánh giá công bằng do lỗi dữ liệu, ID, schema, fixture hoặc dispatcher. Dòng lỗi dữ liệu không được âm thầm biến mất.

Với dòng CSV lỗi, runner giữ `test_case_id` và `requirement_id` nếu có thể xác định được. **FAIL chưa đủ để khẳng định bug của sản phẩm**; cần đối chiếu lại oracle, fixture và cách tái hiện.

## 7. Xuất báo cáo và truy vết

Runner tạo ra:

- `reports/test_execution.csv`: kết quả từng case gồm expected, actual, status, error, `execution_time_ms`, thời điểm UTC và evidence reference.
- `reports/traceability_execution.csv`: liên kết REQ → COND → TS → TC → RUN và trạng thái.
- `reports/test_summary.csv`: tổng hợp số lượng theo từng requirement.
- `reports/run_metadata.json`: số case, thời gian chạy và danh sách REQ được chọn.
- `reports/test_dashboard.html`: trang HTML tự chứa gồm biểu đồ cột SVG theo REQ và bảng chi tiết case.

`loaded = PASS + FAIL + BLOCKED`. Khi mẫu số dương, `pass_rate_executed = PASS/(PASS+FAIL)`; số BLOCKED được báo riêng. Runner **không ghi đè** dữ liệu expected trong `test_cases.csv`.

## 8. Phân biệt lần chạy cục bộ và Google Colab

Chạy bằng Python tại máy cục bộ chỉ là kiểm tra kỹ thuật bổ trợ. Đầu ra trong repository hiện được đồng bộ từ lần chạy **Google Colab ngày 27/10/2026, 21:42:26 (giờ Việt Nam)**, với 33 PASS, 0 FAIL và 0 BLOCKED. Notebook lưu output của lần chạy này.

Việc xác minh độc lập oracle, kiểm tra sâu kết quả và phân tích nguyên nhân lỗi nếu xuất hiện được thực hiện ở bước kiểm chứng sau; các minh chứng ảnh chụp E01–E10 được hoàn thiện riêng. Không xem tỷ lệ PASS của một lần chạy là bằng chứng đầy đủ về chất lượng toàn bộ ứng dụng.
