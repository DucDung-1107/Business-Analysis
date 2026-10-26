# Operating Playbook V3 — pilot giữ chân khách hàng

## 1. Phạm vi và nguyên tắc

Playbook áp dụng cho hai persona V3 trong [Persona Atlas](persona_atlas_v3.md). Đây là pilot mô phỏng; không tự động gửi liên hệ đến khách hàng thật. Không dùng giới tính, quốc gia, salary estimate hoặc balance để quyết định treatment.

Một khách chỉ được vào pilot khi: đã consent đúng kênh, chưa opt-out, không vượt contact cap, không có fraud/suitability hold và không có service case mở. Case mở luôn được route vào Service Recovery, không vào marketing.

## 2. Hai pilot và eligibility

| Pilot | Population | Arm A | Arm B | Không được đưa vào |
| --- | --- | --- | --- | --- |
| P1: phục hồi quan hệ | Persona dùng số thấp | Service Recovery chủ động | Reactivation Coach 14 ngày | case mở, không consent, contact cap vượt mức |
| P2: bảo vệ trải nghiệm số | Persona dùng số thường xuyên | Digital Concierge | Value Review tự chọn | case mở, không consent, contact cap vượt mức |

CRM đóng băng danh sách eligibility trước randomization. Analytics randomize 50/50 trong từng persona, phân tầng theo active-member và product count. Mỗi customer ID chỉ có một arm. CRM lưu `pilot_id`, `arm`, `seed`, `assignment_time`, `suppression_reason` và `contact_status`; không được thay arm thủ công.

## 3. Journey chi tiết

### P1 Arm A — Service Recovery chủ động

| Mốc | Việc làm | Owner | SLA / log bắt buộc |
| --- | --- | --- | --- |
| Ngày 0 | Kiểm tra case, lịch sử liên hệ, consent | Care Ops | xác nhận routing trong 4 giờ làm việc |
| Ngày 1 | Liên hệ bằng kênh khách đã consent; nêu vấn đề và owner xử lý | Care agent | attempt/result/time/channel |
| Ngày 1–3 | Xử lý hoặc escalation theo category/severity | Operations | severity high: escalation ngay; mọi case có status hằng ngày |
| Ngày 3–7 | Xác nhận closure; hỏi một câu “vấn đề đã được giải quyết chưa?” | Care agent | closure/reopen/satisfaction prompt |
| Ngày 14 | Chỉ khi khách xác nhận closure, CRM mới được kiểm tra eligibility cho journey khác | CRM | cooling-period result |

### P1 Arm B — Reactivation Coach

| Mốc | Việc làm | Owner | Policy |
| --- | --- | --- | --- |
| Ngày 0 | Chọn một tác vụ đơn giản phù hợp: xem giao dịch, chuyển tiền hoặc thanh toán hóa đơn | Digital Product | không suy đoán nhu cầu; không offer tiền |
| Ngày 1 | Gửi hướng dẫn trong app hoặc email đã consent | CRM | một message duy nhất |
| Ngày 4 | Hiển thị trợ giúp theo ngữ cảnh nếu khách quay lại app | Product | không follow khách ngoài consent |
| Ngày 8 | Nhắc một lần nếu chưa hoàn thành | CRM | không gửi nếu opt-out/case mở |
| Ngày 14 | Kết thúc journey, ghi completion/drop-off | Analytics | không contact thêm nếu không có consent mới |

## 4. Playbook riêng cho Persona dùng số thường xuyên

### Mục tiêu của phân khúc này

Không cố “kích hoạt lại” khách đã hoạt động. Mục tiêu là giữ các giao dịch thường ngày không bị gián đoạn và tìm cách hỗ trợ nào làm khách tiếp tục tự phục vụ. Đây là cohort 5.285 khách, nhưng chỉ khách có consent, không có case mở và chưa vượt contact cap mới vào pilot.

### P2 Arm A — Digital Concierge

| Mốc | Việc làm cụ thể | Owner | Điều không được làm |
| --- | --- | --- | --- |
| Ngày 0 | Product chọn một tác vụ đang dùng nhiều: chuyển tiền, thanh toán hóa đơn, xem số dư/thẻ | Product | không suy đoán nhu cầu từ gender/country/balance |
| Ngày 1 | Khi khách mở đúng tác vụ, hiển thị một shortcut và trạng thái giao dịch rõ ràng | Product | không pop-up ngoài bối cảnh tác vụ |
| Ngày 1–7 | Nếu thao tác lỗi, hiển thị cách sửa và nút kết nối Care | Product + Care | không ép khách chat/call |
| Ngày 7 | CRM chỉ gửi một message trợ giúp nếu khách đã consent và chưa hoàn thành | CRM | không gửi offer tiền hoặc cross-sell |
| Ngày 14 | Analytics ghi task completion, failed task, support contact và opt-out | Analytics | không contact thêm nếu không có trigger mới |

**KPI riêng:** task completion, failed-task-to-support rate, repeat support contact trong 7 ngày, app-active days.  
**Rủi ro riêng:** hướng dẫn gây phiền hoặc che lỗi hệ thống. **Pause** nếu complaint/opt-out xấu hơn Value Review theo guardrail; Product phải xem recording/event log trước khi mở lại.

### P2 Arm B — Value Review tự chọn

| Mốc | Việc làm cụ thể | Owner | Điều không được làm |
| --- | --- | --- |
| Ngày 0 | CRM kiểm tra consent và fee/benefit thật sự đang áp dụng cho khách | CRM + Product | không dùng dữ liệu mô phỏng làm lý do liên hệ |
| Ngày 1 | Gửi một bản tóm tắt ngắn: sản phẩm đang có, phí/benefit, đường dẫn xem chi tiết | CRM | không nói “khách đang có nguy cơ rời bỏ” |
| Ngày 4 | Khách tự chọn: xem thêm, yêu cầu tư vấn, hoặc từ chối | Customer | không có lựa chọn mặc định đồng ý |
| Ngày 5–10 | Chỉ khách chọn tư vấn mới nhận lịch hẹn hoặc call | CRM / RM | không bán thêm sản phẩm không phù hợp |
| Ngày 14 | Ghi completion, request, opt-out và complaint | Analytics | không tự suy ra product need |

**KPI riêng:** view-to-choice rate, voluntary advice request, product-fit completion, opt-out, complaint.  
**Scale rule riêng:** chỉ scale khi retention effect tốt hơn Digital Concierge với lower CI 95% > 0, cost/contact nằm trong cap Finance và không làm chênh lệch exposure theo gender/country bất thường.

## 5. Playbook riêng cho Persona dùng số thấp

### Mục tiêu của phân khúc này

Đây là cohort 4.715 khách với churn lịch sử cao hơn. Không được coi đây là danh sách bán hàng. Câu hỏi là: giải quyết trải nghiệm chưa xong hay giúp khách hình thành lại một thói quen đơn giản sẽ có hiệu quả hơn?

### P1 Arm A — Service Recovery chủ động

| Mốc | Việc làm cụ thể | Owner | Escalation |
| --- | --- | --- | --- |
| Ngày 0 | Care đọc case category, severity, contact history và kiểm tra đã có case mở hay chưa | Care Ops | severity high sang Operations ngay |
| Ngày 1 | Agent gọi/nhắn qua kênh consent; nói rõ vấn đề, owner, mốc cập nhật kế tiếp | Care | không có phản hồi: ghi no-contact, không spam |
| Ngày 1–3 | Sửa lỗi hoặc xử lý yêu cầu; cập nhật status cho khách | Operations | quá SLA: team lead nhận escalation |
| Ngày 3–7 | Xác nhận closure bằng câu hỏi đơn giản; nếu chưa xong thì reopen | Care | reopen quay về owner ban đầu |
| Ngày 14 | Cooling period; CRM không gửi marketing | CRM | chỉ release khi closure xác nhận |

**KPI riêng:** closure within SLA, reopen rate, repeat contact, complaint after closure, active days sau closure.  
**Hard stop riêng:** case mở bị gửi promotion, consent breach, hoặc high-severity case không có owner.

### P1 Arm B — Reactivation Coach

| Mốc | Việc làm cụ thể | Owner | Policy |
| --- | --- | --- | --- |
| Ngày 0 | Kiểm tra không có case mở; chọn một tác vụ đơn giản từ dữ liệu hành vi thực khi có | CRM + Product | không dùng balance/salary làm trigger |
| Ngày 1 | Một hướng dẫn rõ ràng trong app/email: xem giao dịch, chuyển tiền hoặc thanh toán hóa đơn | CRM | một message |
| Ngày 4 | Nếu khách mở app, hiển thị hỗ trợ theo ngữ cảnh | Product | không gửi push nếu chưa consent |
| Ngày 8 | Một reminder duy nhất khi chưa hoàn thành | CRM | dừng sau reminder |
| Ngày 14 | Đo completion/drop-off; không có incentive ở vòng đầu | Analytics | contact cap bắt buộc |

**KPI riêng:** app-active days, số tháng hoạt động, completion, failed payment, opt-out.  
**Scale rule riêng:** lower CI 95% của active-month/retention effect > 0; failed payment và complaint không xấu hơn Service Recovery; Finance xác nhận cost/saved customer.

## 6. SLA, escalation và policy chung

| Sự kiện | Hành động | Owner | Thời hạn |
| --- | --- | --- | --- |
| Consent breach | dừng arm, suppress khách, điều tra | Compliance | ngay lập tức |
| Case severity high | route Care/Operations, chặn marketing | Care Ops | ngay lập tức |
| Complaint tăng vượt guardrail | pause arm, QA contact content | CRM + Risk | trong 24 giờ |
| Randomization imbalance | dừng enrollment, Analytics kiểm tra | Analytics | trong 1 ngày làm việc |
| Data schema failure | không gửi contact mới | Data Engineering | ngay lập tức |

Contact cap, complaint threshold, opt-out threshold và cost cap phải được CRM/Risk/Finance ký trước launch. Không ghi số giả định vào dashboard như kết quả thật.

## 7. KPI dictionary và cadence

| KPI | Công thức | Chủ sở hữu | Nhịp | Decision use |
| --- | --- | --- | --- | --- |
| Eligibility rate | eligible / candidate persona | CRM | tuần | kiểm tra capacity |
| Contact completion | delivered / assigned | CRM | tuần | channel execution |
| Case closure SLA | closed within SLA / opened cases | Care | tuần | service quality |
| Reopen rate | reopened / closed cases | Care | tuần | closure quality |
| Journey completion | completed task / delivered journey | Product | tuần | leading signal |
| Opt-out rate | opt-outs / delivered | CRM | tuần | pause guardrail |
| Complaint rate | complaints / contacted | Risk | tuần | pause guardrail |
| Incremental active-month rate | treatment rate − comparator rate | Analytics | day 30/60/90 | P1 decision |
| Incremental retention | treatment retention − comparator retention | Analytics | day 90 | scale decision |
| Cost per retained customer | incremental cost / incremental retained customers | Finance | day 90 | break-even |

## 8. Stop, iterate, scale

**Stop ngay:** consent breach, suppressed customer contacted, case mở bị đưa vào marketing, hoặc critical data-quality failure.  
**Pause:** complaint/opt-out/contact-frequency vượt guardrail đã ký; randomization mất cân bằng; Care backlog vượt SLA.  
**Iterate:** journey completion thấp nhưng không có safety issue; Product sửa nội dung rồi randomize phiên bản mới.  
**Scale:** cận dưới CI 95% của retention effect > 0, guardrail không xấu hơn comparator, Finance xác nhận cost/saved customer đạt break-even, Risk ký fairness review.

## 9. RACI và weekly operating meeting

| Việc | CRM | Care | Product | Finance | Risk | Analytics |
| --- | --- | --- | --- | --- | --- | --- |
| eligibility/randomization | A/R | C | C | I | C | R |
| service routing/SLA | I | A/R | C | I | C | I |
| journey/content | R | C | A/R | I | C | C |
| cost/break-even | I | I | C | A/R | I | C |
| guardrail/consent | C | C | I | I | A/R | R |
| experiment readout | I | I | C | C | C | A/R |

Mỗi thứ Hai, nhóm họp 30 phút: Analytics đọc arm balance/data QA; Care đọc SLA/reopen; CRM đọc contact/opt-out; Product đọc completion/drop-off; Finance đọc spend; Risk quyết định pause/continue. CEO nhận dashboard một trang mỗi tuần và quyết định stop/iterate/scale ở ngày 90.
