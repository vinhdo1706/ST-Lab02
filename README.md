# STLab02 — EduCommerce Test Case Execution

**Môn học:** Kiểm thử phần mềm (Software Testing)  
**Bài thực hành:** STLab02 – Test Case Execution  
**MSSV:** 20110112  
**Sinh viên:** Đỗ Thành Vinh  
**Yêu cầu được chọn:** REQ-02, REQ-07, REQ-09, REQ-10, REQ-15  
**Phạm vi:** 5 yêu cầu nghiệp vụ; kiểm thử từ CSV bằng Python; báo cáo kết quả và dashboard HTML. Mã nguồn ứng dụng EduCommerce gốc được giữ nguyên.

## 1. Giới thiệu

Dự án thực hiện kiểm thử dựa trên yêu cầu đối với module **EduCommerce** trong tài liệu hướng dẫn STLab02. Bộ kiểm thử sử dụng dữ liệu đầu vào và kết quả mong đợi được xác định từ các tiêu chí chấp nhận (*acceptance criteria*), sau đó chạy tự động trên Google Colab.

Năm yêu cầu được kiểm thử gồm:

| Mã yêu cầu | Nội dung |
|---|---|
| REQ-02 | Số lượng thêm vào giỏ phải là số nguyên dương; cùng SKU được cộng dồn. |
| REQ-07 | Voucher không hợp lệ hoặc đã dùng phải bị từ chối; chỉ ghi nhận đã dùng khi đơn hàng thành công. |
| REQ-09 | Phí vận chuyển phụ thuộc khu vực và ngưỡng tổng tiền hàng. |
| REQ-10 | COD/ONLINE có trạng thái thanh toán riêng; giao dịch bị từ chối không được tạo đơn. |
| REQ-15 | Một SKU thiếu tồn kho phải làm cả đơn bị từ chối, không trừ tồn kho của SKU khác. |

REQ-06, REQ-08 và REQ-11 là ví dụ đã hướng dẫn trong tài liệu Instruction, **không nằm trong năm yêu cầu tự chọn** của bài này.

## 2. Cấu trúc dự án

| Tệp / thư mục | Chức năng |
|---|---|
| `ecommerce_app.py` | Mã nguồn EduCommerce gốc từ tài liệu Instruction, mục 2.6; không sửa logic nghiệp vụ. |
| `test_runner.py` | Chương trình đọc dữ liệu, tạo fixture, chạy các test case, so sánh kết quả và xuất báo cáo. |
| `test_cases.csv` | Bộ 33 test case của năm yêu cầu đã chọn; chứa dữ liệu đầu vào và expected độc lập. |
| `traceability_design.csv` | Ma trận truy vết REQ → COND → TS → TC. |
| `STLab02_EduCommerce.ipynb` | Notebook Google Colab chứa lần chạy kiểm thử và kết quả các cell. |
| `requirement_analysis.md` | Phân tích yêu cầu, điều kiện, tình huống, test case và rủi ro. |
| `code_explanation.md` | Giải thích fixture, CSV reader, dispatcher, assertion, exception handling và reporter. |
| `problem_solving_answers.md` | Câu trả lời tám tình huống ở Phần 3. |
| `interview_answers.md` | Câu trả lời 20 câu hỏi và ba bài Code Interview ở Phần 4. |
| `reports/test_execution.csv` | Kết quả thực thi chi tiết của từng test case trên Colab. |
| `reports/test_summary.csv` | Tổng hợp số test PASS/FAIL/BLOCKED theo từng yêu cầu. |
| `reports/traceability_execution.csv` | Ma trận truy vết đến mã lần chạy (RUN) và trạng thái. |
| `reports/test_dashboard.html` | Dashboard độc lập gồm thống kê, biểu đồ và bảng kết quả. |
| `reports/run_metadata.json` | Thông tin thời gian chạy, số case và các yêu cầu được chọn. |

Tên file, tên hàm, mã yêu cầu, mã test case và các trường dữ liệu giữ nguyên để phục vụ việc thực thi và truy vết.

## 3. Kết quả thực thi trên Google Colab

Lần chạy được lưu trong project diễn ra lúc **21:42:26 ngày 27/10/2026 (giờ Việt Nam)**, tương ứng `2026-10-27T14:42:26+00:00` (UTC).

| Yêu cầu | Số test case | PASS | FAIL | BLOCKED |
|---|---:|---:|---:|---:|
| REQ-02 | 7 | 7 | 0 | 0 |
| REQ-07 | 7 | 7 | 0 | 0 |
| REQ-09 | 6 | 6 | 0 | 0 |
| REQ-10 | 6 | 6 | 0 | 0 |
| REQ-15 | 7 | 7 | 0 | 0 |
| **Tổng** | **33** | **33** | **0** | **0** |

**Tỷ lệ PASS của các case thực thi:** 100% (33/33). Tổng số dòng được nạp bằng tổng PASS + FAIL + BLOCKED. Các tệp trong `reports/` và output của notebook là kết quả chạy thực tế; kết quả PASS không đồng nghĩa ứng dụng không có lỗi ngoài phạm vi đã kiểm thử.

## 4. Hướng dẫn chạy trên Google Colab

1. Truy cập [Google Colab](https://colab.research.google.com/), chọn **File → Upload notebook** và mở `STLab02_EduCommerce.ipynb`.
2. Chạy cell đầu tiên để xem phiên bản Python và thư mục làm việc.
3. Tại cell **Upload source và CSV**, tải lên đồng thời ba file từ cùng phiên bản project: `ecommerce_app.py`, `test_runner.py`, `test_cases.csv`.
4. Chạy cell thực thi bộ test. Kiểm tra danh sách case, trạng thái PASS/FAIL/BLOCKED, thời gian chạy và thông báo lỗi nếu có.
5. Chạy các cell hiển thị bảng tổng hợp và HTML dashboard.
6. Chạy cell cuối để tải `STLab02_Colab_Execution.zip`, chứa các tệp kết quả trong `reports/`.
7. Lưu kết quả tải về và cập nhật đồng bộ các file trong thư mục `reports/` của project nếu thực hiện lần chạy mới.

**Lưu ý:** Môi trường chạy Colab có tính tạm thời. Khi thực thi lại, cần sử dụng notebook, mã nguồn và dữ liệu kiểm thử cùng phiên bản; lưu các tệp kết quả sau khi chạy.

## 5. Chạy cục bộ bằng VS Code (tùy chọn)

Cần Python 3.10 trở lên và thư viện `pandas`. Mở terminal tại thư mục `Labs/ST-Lab02`, sau đó chạy:

```powershell
py -3 -m pip install pandas
py -3 test_runner.py
```

Nếu `pandas` đã được cài, không cần chạy lại lệnh cài thư viện. Việc chạy cục bộ chỉ để hỗ trợ kiểm tra; **không thay thế kết quả Google Colab** theo yêu cầu bài thực hành.

## 6. Nguyên tắc đánh giá kết quả

- **PASS:** Kết quả thực tế khớp tất cả các trường được yêu cầu trong `expected_json`, kể cả ngoại lệ nghiệp vụ được dự kiến.
- **FAIL:** Test case hợp lệ có kết quả không khớp expected, hoặc xuất hiện lỗi ứng dụng ngoài dự kiến.
- **BLOCKED:** Chưa thể đánh giá hành vi ứng dụng do thiếu/sai dữ liệu, mã định danh trùng, fixture không hợp lệ hoặc lỗi thiết lập/đọc dữ liệu.
- **Tính đầy đủ:** `loaded = PASS + FAIL + BLOCKED`; dòng dữ liệu lỗi không được âm thầm bỏ khỏi báo cáo.
- **Tỷ lệ PASS trong số case thực thi:** `PASS / (PASS + FAIL)` khi mẫu số lớn hơn 0. Cần xem riêng số BLOCKED để không nhầm tỷ lệ PASS cao với độ bao phủ đầy đủ.

Các cột dữ liệu bắt buộc của CSV:

```text
test_case_id, requirement_id, condition_id, scenario_id, title, priority, precondition, fixture_key, input_json, expected_type, expected_json, execution_status, actual_result, error_message, evidence_reference
```

Hai cột bổ sung `case_type` và `test_steps` hỗ trợ đọc test case. Các trường đầu ra thực thi trong CSV đầu vào được để trống; runner ghi kết quả vào `reports/`, **không ghi đè expected gốc**.

## 7. Nguồn gốc và giới hạn

- `ecommerce_app.py` được lấy từ khối mã trong `STLab02 - Test Case Execution (Instruction)(1).docx`, mục 2.6, và được bảo toàn về logic nghiệp vụ.
- Runner, test data và các tài liệu phân tích được xây dựng để đáp ứng `STLab02 - Test Case Execution (Requirement)(1).docx`.
- EduCommerce là ứng dụng mô phỏng chạy trong bộ nhớ; không có cơ sở dữ liệu lưu trữ, cổng thanh toán thực tế hoặc mô phỏng tranh chấp đồng thời.
- Các trường hợp chưa được kiểm thử và những điểm requirement cần làm rõ được ghi trong `requirement_analysis.md`.
- Nếu phát hiện FAIL, cần xác minh expected, dữ liệu và fixture trước khi kết luận lỗi sản phẩm. Không chỉnh expected để làm tăng PASS.

**Repository:** https://github.com/vinhdo1706/ST-Lab02

Repository cung cấp mã nguồn, dữ liệu kiểm thử, notebook, hướng dẫn thực thi và kết quả để phục vụ đối chiếu, tái hiện bài thực hành.
