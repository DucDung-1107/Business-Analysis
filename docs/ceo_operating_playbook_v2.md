# Playbook CEO: hai chiến lược giữ chân, hai phân khúc, hai lựa chọn hành động

## Điều CEO cần quyết định

Phê duyệt hai pilot khác nhau. Mỗi pilot so sánh **hai cách chăm sóc**, không phải “gửi campaign” với “không làm gì”. Khách không có consent, đã vượt contact cap, hoặc còn case khiếu nại mở sẽ bị loại khỏi randomization. Case khiếu nại mở luôn được xử lý theo quy trình dịch vụ bắt buộc.

## Vì sao có hai phân khúc này?

Hệ thống tạo sáu tháng dữ liệu hành vi mô phỏng: số giao dịch, app sessions, tiền vào, chi tiêu thẻ, thanh toán hóa đơn/khoản vay, rút tiền, failed payment và service case. Ba cách gom nhóm được thử trên cùng bộ chỉ số hành vi:

| Phương pháp | Điều nó làm tốt | Kết quả | Quyết định |
| --- | --- | ---: | --- |
| K-Means | Nhóm lặp lại rất ổn định, dễ vận hành | stability 0,979; composite 0,883 | **Dùng làm phân khúc chính** |
| Gaussian Mixture | Cho phép nhóm có độ phân tán khác nhau | composite 0,650 | Đối chứng, không chọn |
| Ward hierarchical | Cho góc nhìn cây nhóm | composite 0,483 | Không chọn |

Chúng tôi chọn K-Means vì phân khúc phải dùng được trong CRM hằng tuần: hai nhóm gần bằng nhau, kết quả gần như giữ nguyên khi lấy lại mẫu. Các điểm số này chỉ kiểm tra độ ổn định của hành vi **mô phỏng**; chúng không xác nhận đây là hành vi ngân hàng thực.

## Phân khúc 1: khách đang gắn bó, cần giữ trải nghiệm tốt

**Quy mô:** 5.019 khách, bằng 50,2% danh mục.  
**Rủi ro lịch sử:** 713/5.019 đã rời bỏ, tương đương **14,2%**; khoảng tin cậy 95% là 13,3–15,2%. Mức chung là 20,4%.

**Chân dung:** tuổi trung bình 37,8; 45,0% nữ, 55,0% nam. France 50,3%, Germany 24,7%, Spain 25,0%. Có 89,8% cờ active-member, trung bình 1,6 sản phẩm. Median salary estimate 106.656 và median balance 94.631, đơn vị tiền tệ không được dataset xác định. Country là nơi được ghi nhận, không phải quê quán; gender/country không quyết định offer.

**Hành vi trong kịch bản sáu tháng:** mỗi tháng khoảng 4,4 giao dịch, 5,8 lần đăng nhập và 7,5 ngày dùng app. Tiền vào bình quân 7.431/tháng, xuất hiện trong 85,7% tháng; chi tiêu/rút tiền ổn định hơn nhóm còn lại. Failed payment là 0,04/tháng. Tỷ lệ case chưa giải quyết ở mức 6,7% trong simulation.

**Diễn giải cho business:** nhóm này chưa phải báo động về tỷ lệ rời bỏ, nhưng quy mô lớn. Nếu trải nghiệm xấu đi, tác động tuyệt đối sẽ lớn. Trong simulation, 1.205 khách có service-contact signal và 1.591 có tín hiệu ưu tiên tự phục vụ số. Đây là các tình huống cần kiểm tra, không phải lý do rời bỏ đã được chứng minh.

### Pilot A/B: “Giữ mượt” hay “Tăng giá trị sử dụng”

| Arm | Action cụ thể | Chủ sở hữu | Mục tiêu |
| --- | --- | --- | --- |
| A: Digital concierge | In-app checklist theo ngữ cảnh, hướng dẫn hoàn thành tác vụ và đường tắt hỗ trợ; không ưu đãi tiền | Product + CRM | Giảm nhu cầu liên hệ support, tăng self-service completion |
| B: Value review | Tin nhắn/nhân viên tư vấn ngắn về sản phẩm khách đang có, fee/benefit rõ ràng, khách tự chọn có nhận tư vấn tiếp không | CRM + Product | Tăng mức sử dụng phù hợp, không ép cross-sell |

Chia ngẫu nhiên 50/50 trong khách đủ điều kiện, giữ một holdout nhỏ nếu Finance/CRM yêu cầu baseline. Không đưa khách có case mở vào Arm B.

**KPI:** trong 30 ngày: completion rate, app-active days, repeated support contact. Trong 90 ngày: chênh lệch retention và active-month rate giữa A/B. **Thành công:** arm thắng có cận dưới CI 95% của hiệu quả retention lớn hơn 0, complaint/opt-out không xấu hơn arm còn lại, và Finance xác nhận chi phí/khách giữ lại dưới break-even. **Dừng:** mọi consent breach; hoặc complaint/opt-out vượt guardrail đã ký trước pilot.

## Phân khúc 2: khách suy giảm hoạt động, nhóm đáng báo động

**Quy mô:** 4.981 khách, 49,8% danh mục.  
**Rủi ro lịch sử:** 1.324/4.981 đã rời bỏ, tương đương **26,6%**; khoảng tin cậy 95% là 25,4–27,8%. Cao hơn mức chung 6,2 điểm phần trăm. Đây là nhóm ưu tiên một.

**Chân dung:** tuổi trung bình 40,1; 45,8% nữ, 54,2% nam. France 49,9%, Germany 25,5%, Spain 24,6%. Chỉ 12,9% có cờ active-member; trung bình 1,5 sản phẩm. Median salary estimate 92.983; median balance 99.341, cùng giới hạn đơn vị tiền tệ.

**Hành vi trong kịch bản sáu tháng:** khoảng 2,8 giao dịch, 3,5 lần đăng nhập và 4,5 ngày app/tháng. Tiền vào bình quân 3.093/tháng và chỉ xuất hiện trong 40,9% tháng. Tỷ lệ rút tiền trong tổng giá trị giao dịch là 18,2%, cao hơn nhóm gắn bó (15,0%). Failed payment 0,06/tháng; case chưa giải quyết 9,7%, cao hơn nhóm gắn bó 3,0 điểm phần trăm.

**Diễn giải cho business:** đây là chân dung “quan hệ đang yếu” trong mô phỏng: dùng ít hơn, tiền vào thưa hơn, app dùng ít hơn và service case chưa khép lại nhiều hơn. Điều này không chứng minh nguyên nhân churn. Nó đủ để ưu tiên một pilot có thiết kế chặt chẽ.

Trong simulation, 1.662 khách (33,4%) có service-contact signal và 976 khách (19,6%) có low-activity signal. Những tín hiệu này dùng để route journey, không được mô tả với khách như một “điểm rủi ro”.

### Pilot A/B: “Sửa trải nghiệm” hay “Tạo thói quen quay lại”

| Arm | Action cụ thể | Chủ sở hữu | Mục tiêu |
| --- | --- | --- | --- |
| A: Service recovery | Rà soát case, gọi lại trong SLA đã cam kết, cập nhật tiến độ, xác nhận khách đã giải quyết xong; không chào bán khi issue chưa đóng | Customer Care + Operations | Giảm unresolved case, giảm repeat contact, bảo vệ niềm tin |
| B: Reactivation coach | Một journey 14 ngày qua in-app/email: chọn một mục tiêu giao dịch, hướng dẫn thực hiện, nhắc đúng lúc; không cash incentive ở pilot đầu | CRM Lifecycle + Digital Product | Tăng active days, tiền vào đều hơn và số tháng có giao dịch |

Để công bằng, khách có case đang mở phải nhận Service recovery theo policy, không randomize. Phần còn lại của segment_02 được chia ngẫu nhiên 50/50 giữa A và B; randomization phân tầng theo active-member và product count để hai arm cân bằng.

**KPI:** mỗi tuần: tỷ lệ contact thành công, case closure within SLA, app-active days, failed-payment count, opt-out, complaint. Sau 90 ngày: incremental active-month rate và retention của A/B; thêm chi phí service/campaign trên mỗi khách giữ lại. **Scale:** chỉ scale arm thắng khi lower bound CI 95% > 0, break-even được Finance duyệt, không có lệch exposure bất lợi theo gender/country. **Stop:** bất kỳ consent breach; tăng complaint hoặc opt-out theo ngưỡng Risk/CRM phê duyệt; hoặc investigation cho thấy data quality sai.

## Phân vai điều hành

| Bộ phận | Việc phải làm tuần đầu | Việc phải báo cáo hàng tuần |
| --- | --- | --- |
| CRM | Chốt eligibility, consent, frequency cap, randomization list | contacted, delivered, opt-out, arm balance |
| Customer Care / Operations | Định nghĩa SLA và escalation cho case | opened/resolved/reopened cases, SLA breach |
| Product | Viết journey, đo completion và drop-off | funnel, active days, support contact |
| Finance | Xác định contribution, unit cost, break-even | spend, cost/contact, cost/saved customer |
| Risk / Compliance | Duyệt suppression, fairness monitoring | consent breach, exposure and outcome by aggregate demographic |
| Analytics | Khoá protocol, đo CI và kiểm tra bias | treatment effect, uncertainty, data-quality alerts |

## CEO dashboard mỗi tuần

1. Khách đủ điều kiện, đã randomize và đã contact, theo arm.  
2. SLA xử lý case, repeat contact, opt-out và complaint.  
3. App-active days, active-month rate, inbound-flow regularity và failed payments, chỉ như leading indicators.  
4. Sau 90 ngày: retention effect, CI, cost/saved customer và quyết định stop/iterate/scale.

## Ranh giới bằng chứng

Tỷ lệ churn, demographics và trạng thái active là dữ liệu tĩnh Kaggle. Dòng tiền, ngày nhận tiền, app usage, loan/bill payment, service case và pain scenario là synthetic data được sinh bằng seed cố định và không điều kiện theo churn. Các chi tiết này giúp thiết kế và kiểm thử chiến lược; chúng không phải bằng chứng về hành vi hay lý do rời bỏ của một ngân hàng thật.

Số liệu và figure truy vết tại [artifacts V2](../reports/segmentation/v2/) và [methodology](segmentation_v2_methodology.md).
