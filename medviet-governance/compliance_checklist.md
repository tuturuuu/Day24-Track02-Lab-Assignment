# NĐ13/2023 Compliance Checklist — MedViet AI Platform

## A. Data Localization
- [ ] Tất cả patient data lưu trên servers đặt tại Việt Nam
- [ ] Backup cũng phải ở trong lãnh thổ VN
- [ ] Log việc transfer data ra ngoài nếu có

## B. Explicit Consent
- [ ] Thu thập consent trước khi dùng data cho AI training
- [ ] Có mechanism để user rút consent (Right to Erasure)
- [ ] Lưu consent record với timestamp

## C. Breach Notification (72h)
- [ ] Có incident response plan
- [ ] Alert tự động khi phát hiện breach
- [ ] Quy trình báo cáo đến cơ quan có thẩm quyền trong 72h

## D. DPO Appointment
- [ ] Đã bổ nhiệm Data Protection Officer
- [ ] DPO có thể liên hệ tại: dpo@medviet.vn

## E. Technical Controls (mapping từ requirements)
| NĐ13 Requirement | Technical Control | Status | Owner |
|-----------------|-------------------|--------|-------|
| Data minimization | PII anonymization pipeline (Presidio) | ✅ Done | AI Team |
| Access control | RBAC (Casbin) + ABAC (OPA) | ✅ Done | Platform Team |
| Encryption | AES-256 at rest, TLS 1.3 in transit | 🚧 In Progress | Infra Team |
| Audit logging | CloudTrail + API access logs | ⬜ Todo | Platform Team |
| Breach detection | Anomaly monitoring (Prometheus) | ⬜ Todo | Security Team |

## F. TODO: Điền vào phần còn thiếu
Với mỗi row còn "⬜ Todo", mô tả technical solution cụ thể bạn sẽ implement.

- Audit logging:
	- Thu thập access log tại FastAPI middleware (request_id, user, role, endpoint, status, latency).
	- Đẩy log sang Loki/CloudWatch theo chuẩn JSON và đặt retention >= 180 ngày.
	- Tạo dashboard theo dõi truy cập dữ liệu nhạy cảm và alert khi có spike bất thường.
- Breach detection:
	- Dùng Prometheus thu thập metrics lỗi auth (401/403), số lần truy cập PII endpoint và tốc độ xuất dữ liệu.
	- Thiết lập Alertmanager rule: nhiều 403 liên tiếp, tăng đột biến băng thông outbound, hoặc truy cập trái giờ.
	- Kết nối alert với PagerDuty/Slack để kích hoạt quy trình incident response trong 72h.
