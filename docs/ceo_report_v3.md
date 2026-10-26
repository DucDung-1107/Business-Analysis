# CEO decision report V3

## Quyết định hôm nay

Không phê duyệt A/B test ở mức thay đổi 2–3 điểm phần trăm. Với quy mô hiện có, pilot đó thiếu lực thống kê. Phê duyệt giai đoạn chuẩn bị dữ liệu, consent và service routing; sau đó chọn một trong ba phương án: nhận diện một hiệu ứng lớn hơn, kéo dài quan sát, hoặc mở rộng cohort.

## Hai phân khúc vận hành

**Khách dùng số thường xuyên:** 5.243 khách. Họ có 67,2 app-active days trong sáu tháng, 4,9 tháng có dòng tiền vào và 41,8 giao dịch. Tỷ lệ churn tĩnh lịch sử là 14,3% (752/5.243). Đây là nhóm bảo vệ trải nghiệm, không phải nhóm cần incentive.

**Khách dùng số thấp:** 4.757 khách. Họ có 24,5 app-active days, 1,4 tháng có dòng tiền vào và 26,4 giao dịch. Tỷ lệ churn tĩnh là 27,0% (1.285/4.757). Đây là nhóm đáng báo động. Họ cũng có failed payment cao hơn (0,64 so với 0,24) và unresolved-case share cao hơn (30,6% so với 10,5%) trong simulation.

Các khác biệt trên là output của synthetic V3; effect sizes lớn nhất là app-active days (Cohen's d 4,28), inflow months (2,91) và transaction count (2,57). Chúng chứng minh hai nhóm tách rõ trong simulation, không chứng minh nguyên nhân churn thật.

## Hai chiến lược cần so sánh

### Nhóm dùng số thấp: sửa trải nghiệm hay tạo thói quen quay lại

- **Arm A, Service recovery:** route khách có service issue vào Care, xác nhận lỗi, xử lý theo SLA, thông báo trạng thái và chỉ mời tiếp khi case đóng.
- **Arm B, Reactivation coach:** journey 14 ngày, một mục tiêu sử dụng rõ ràng, hướng dẫn trong app, nhắc đúng thời điểm, không dùng cash incentive ở pilot đầu.

KPI leading: case closure within SLA, repeat contact, app-active days, failed payment. KPI 90 ngày: active-month rate và retention. Hard stop: consent breach hoặc route nhầm khách có unresolved case vào campaign.

### Nhóm dùng số thường xuyên: giữ self-service hay tăng giá trị sử dụng

- **Arm A, Digital concierge:** hỗ trợ theo ngữ cảnh trong app; đo completion và repeat support contact.
- **Arm B, Value review:** giải thích fee/benefit và cho khách quyền chọn tư vấn tiếp; không mặc định cross-sell.

KPI leading: self-service completion, case recurrence, app-active days. KPI 90 ngày: retention và product-fit completion. Hard stop: consent breach hoặc guardrail complaint/opt-out vượt ngưỡng Risk phê duyệt.

## Điều kiện về quy mô pilot

Với alpha 5%, power 80% và giả định MDE 3 điểm phần trăm cho tái kích hoạt, cần **4.360 khách mỗi arm**. Với MDE 2 điểm cho retention, cần **4.920 khách mỗi arm**. Đây là giả định thiết kế, không phải uplift dự báo. Decision cube hiện chỉ cho thấy 1.678 khách dùng số thấp, không có service issue, ở lower cashflow scenario; vì vậy pilot P1 như thiết kế chưa đủ mẫu. CEO cần yêu cầu Analytics lập lại power với MDE/baseline do CRM và Finance phê duyệt trước randomization.

## Điều hành 30/60/90 ngày

- **0–30:** CRM khoá consent/contact cap; Care chuẩn hóa service-case category/SLA; Finance chốt cost và contribution assumptions; Analytics chốt power.
- **31–60:** chạy pilot đủ mẫu, kiểm tra arm balance hằng tuần, không scale.
- **61–90:** đọc uplift với CI 95%, cost/saved customer và fairness exposure. Scale chỉ nếu cận dưới CI > 0, break-even đạt và guardrail không xấu hơn control.

Artifacts: [multi-seed diagnostics](../reports/segmentation/v3/multi_seed_diagnostics.csv), [effect sizes](../reports/segmentation/v3/distinctiveness.csv), [decision cube](../reports/segmentation/v3/decision_cube_v3.csv), [pilot protocol](../reports/segmentation/v3/pilot_protocol_v3.csv), [figures](../reports/segmentation/v3/).
