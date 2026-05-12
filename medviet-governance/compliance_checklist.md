# NĐ13/2023 Compliance Checklist — MedViet AI Platform

## A. Data Localization

* [ ] Tất cả patient data được lưu trữ trên hệ thống máy chủ đặt tại lãnh thổ Việt Nam.
* [ ] Toàn bộ dữ liệu backup được lưu trữ trong phạm vi lãnh thổ Việt Nam.
* [ ] Có cơ chế logging và audit toàn bộ hoạt động truyền tải dữ liệu ra khỏi hệ thống nội bộ (nếu phát sinh).

---

## B. Explicit Consent

* [ ] Thu thập và lưu trữ explicit consent trước khi sử dụng dữ liệu cho mục đích AI training.
* [ ] Cung cấp cơ chế cho phép người dùng rút lại consent (Right to Erasure / Right to Withdraw Consent).
* [ ] Lưu trữ consent records kèm theo metadata: timestamp, user_id, purpose, version of consent policy.

---

## C. Breach Notification (72h)

* [ ] Xây dựng incident response plan theo quy trình chuẩn hóa.
* [ ] Triển khai hệ thống cảnh báo tự động khi phát hiện dấu hiệu data breach hoặc hành vi truy cập bất thường.
* [ ] Thiết lập quy trình báo cáo vi phạm dữ liệu đến cơ quan có thẩm quyền trong vòng tối đa 72 giờ theo NĐ13/2023.

---

## D. DPO Appointment

* [ ] Đã bổ nhiệm Data Protection Officer (DPO) chịu trách nhiệm giám sát tuân thủ dữ liệu cá nhân.
* [ ] Thiết lập kênh liên hệ chính thức với DPO: [dpo@medviet.vn](mailto:dpo@medviet.vn)
* [ ] DPO có quyền truy cập hệ thống audit logs và báo cáo compliance định kỳ.

---

## E. Technical Controls (mapping từ requirements)

| NĐ13 Requirement  | Technical Control                                               | Status      | Owner         |
| ----------------- | --------------------------------------------------------------- | ----------- | ------------- |
| Data minimization | PII anonymization pipeline (Presidio-based processing)          | Done        | AI Team       |
| Access control    | RBAC (Casbin) + ABAC (OPA policy engine)                        | Done        | Platform Team |
| Encryption        | AES-256 encryption at rest, TLS 1.3 for data in transit         | In Progress | Infra Team    |
| Audit logging     | Centralized logging system (FastAPI middleware + Cloud logging) | Todo        | Platform Team |
| Breach detection  | Metrics monitoring and anomaly detection (Prometheus + rules)   | Todo        | Security Team |

---

## F. Chi tiết triển khai cho các hạng mục còn thiếu

### Audit logging

* Triển khai lớp logging tập trung trong middleware của FastAPI để ghi nhận toàn bộ hoạt động API, bao gồm:

  * request_id, user_id, vai trò người dùng (role)
  * endpoint, phương thức HTTP (GET, POST,...)
  * mã trạng thái phản hồi (status code)
  * thời gian xử lý request (latency)
  * địa chỉ IP truy cập
* Chuẩn hóa log theo định dạng JSON để phục vụ giám sát và truy vết dữ liệu.
* Gửi log về hệ thống logging tập trung (ví dụ: Loki, ELK Stack hoặc CloudWatch).
* Thiết lập chính sách lưu trữ log tối thiểu 180 ngày theo yêu cầu tuân thủ.
* Xây dựng dashboard để theo dõi:

  * Lượt truy cập vào các API chứa dữ liệu nhạy cảm (PII)
  * Hành vi truy cập theo người dùng
  * Phát hiện bất thường về lưu lượng truy cập
* Thiết lập cảnh báo khi:

  * Có tăng đột biến truy cập vào dữ liệu nhạy cảm
  * Có nhiều request không hợp lệ hoặc bị từ chối (403/401)
  * Truy cập bất thường ngoài khung giờ hoạt động

---

### Phát hiện vi phạm (Breach detection)

* Thu thập metrics giám sát bằng Prometheus, bao gồm:

  * Số lượng lỗi xác thực (401/403)
  * Tần suất truy cập vào các endpoint chứa dữ liệu nhạy cảm
  * Lưu lượng dữ liệu đầu ra (data egress)
* Thiết lập luật cảnh báo trong Alertmanager:

  * Nhiều lần đăng nhập thất bại liên tiếp từ cùng một IP
  * Tăng đột biến truy cập dữ liệu PII
  * Lưu lượng dữ liệu xuất ra ngoài tăng bất thường
  * Hành vi truy cập khác so với baseline bình thường
* Tích hợp hệ thống cảnh báo với kênh phản ứng sự cố:

  * Slack / PagerDuty để thông báo cho đội trực
  * Tự động tạo ticket xử lý sự cố (Jira hoặc ServiceNow)
* Đảm bảo quy trình xử lý sự cố đáp ứng yêu cầu báo cáo vi phạm dữ liệu trong vòng tối đa 72 giờ theo NĐ13/2023.
