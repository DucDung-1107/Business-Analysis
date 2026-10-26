# Kế hoạch giữ chân khách hàng: quyết định cần CEO phê duyệt

## Quyết định trong một trang

Ngân hàng không nên gửi khuyến mãi hàng loạt. Hai nhóm khách hàng cần hai cách chăm sóc khác nhau:

1. **Nhóm cần tái kích hoạt:** 2.303 khách hàng, tương đương 23% danh mục. Tỷ lệ rời bỏ trong nhãn lịch sử là **25,1%**, cao hơn mức chung 20,4%. Đây là nhóm cần được thử nghiệm trước, với hành trình quay lại dịch vụ và xử lý vướng mắc.
2. **Nhóm đang gắn bó nhưng có quy mô lớn:** 7.697 khách hàng, chiếm 77% danh mục. Tỷ lệ rời bỏ là **18,9%**, thấp hơn mức chung, nhưng nhóm này có 1.458 khách đã rời bỏ trong dữ liệu lịch sử. Mục tiêu ở đây là giữ trải nghiệm tốt và phát hiện sớm khách cần hỗ trợ, không phải giảm giá đại trà.

Các tỷ lệ trên là số liệu từ nhãn churn lịch sử của Kaggle, với khoảng tin cậy 95%: nhóm tái kích hoạt 23,4–27,0%; nhóm gắn bó 18,1–19,8%. Chúng không phải dự báo quý sau và cũng không chứng minh nguyên nhân rời bỏ.

## Hai cách chia khách hàng, dùng cho hai quyết định khác nhau

### Cách 1: chia theo cách khách hàng sử dụng dịch vụ

Mục tiêu là trả lời: **khách đang dùng ngân hàng theo nhịp nào và cần trải nghiệm nào?**

Nhóm dự án tạo sáu tháng hành vi mô phỏng gồm giao dịch, đăng nhập, tỷ lệ dùng kênh số và liên hệ dịch vụ. Sau đó so sánh ba cách gom nhóm:

| Cách thử | Điểm mạnh | Điều còn yếu | Kết quả kiểm tra |
| --- | --- | --- | --- |
| K-Means | Dễ giải thích, nhóm lặp lại rất ổn định | Các nhóm chưa tách rõ bằng cách mô hình hoá hình dạng dữ liệu | Độ ổn định 0,957; điểm tách nhóm 0,185 |
| Phân cấp Ward | Cho góc nhìn cấu trúc tổng thể | Độ ổn định thấp hơn và không thắng theo tiêu chí đã chốt | Độ ổn định 0,811; điểm tách nhóm 0,211 |
| Gaussian Mixture | Cho phép mỗi nhóm có mức dao động khác nhau, phù hợp khi hành vi không đồng đều | Khó giải thích hơn K-Means, nên chỉ dùng hai nhóm dễ vận hành | **Được chọn**; độ ổn định 0,875; điểm tổng hợp 0,700 |

Nói đơn giản, Gaussian Mixture được chọn không phải vì “AI tốt hơn”, mà vì nó cân bằng tốt nhất giữa việc tách được hai kiểu sử dụng và việc lặp lại kết quả khi lấy lại mẫu dữ liệu. K-Means vẫn được giữ làm đối chứng: nếu hai cách cho kết quả khác nhau nhiều, không nên đưa ra quyết định lớn.

### Cách 2: chia theo trạng thái quan hệ với ngân hàng

Mục tiêu là trả lời: **nên ưu tiên ai trong vận hành, ngay cả khi chưa biết lý do rời bỏ?**

Đây không phải là thuật toán phân cụm. Đây là các nhóm vận hành đơn giản từ dữ liệu gốc:

| Góc nhìn | Nhóm | Quy mô | Tỷ lệ rời bỏ lịch sử | Ý nghĩa thực tế |
| --- | --- | ---: | ---: | --- |
| Hoạt động | Không active | 4.849 | 26,9% | Danh sách cần xem xét tái kích hoạt, sau khi kiểm tra consent |
| Hoạt động | Active | 5.151 | 14,3% | Nhóm đối chiếu; ưu tiên duy trì trải nghiệm |
| Độ sâu sản phẩm | 1 sản phẩm | 5.084 | 27,7% | Có thể thiếu gắn kết sản phẩm; cần kiểm chứng bằng thử nghiệm |
| Độ sâu sản phẩm | 2 sản phẩm | 4.590 | 7,6% | Mốc tham chiếu tốt, không có nghĩa là phải bán thêm sản phẩm |
| Độ sâu sản phẩm | 3 sản phẩm | 266 | 82,7% | Nhóm nhỏ, rủi ro cao bất thường; cần service review trước mọi ưu đãi |

Hai cách chia này đi cùng nhau. Cách 1 cho biết nên thiết kế trải nghiệm nào. Cách 2 giúp xếp hàng ưu tiên, giới hạn công suất và kiểm tra kết quả theo từng nhóm.

## Chân dung và chiến lược cho từng nhóm

### 1. Nhóm cần tái kích hoạt

Đây là nhóm có hoạt động mô phỏng thấp hơn: trung bình 2,6 giao dịch và 3,8 lần đăng nhập mỗi tháng; 80,2% số tháng có hoạt động. Họ dùng kênh số cho 57,3% giao dịch. Trong dữ liệu gốc, 33,3% có cờ active-member, thấp hơn đáng kể so với nhóm còn lại.

Về chân dung, nhóm có tuổi trung bình 40; 46,5% là nữ và 53,5% là nam. Trường `country` ghi France 50,2%, Germany 24,8%, Spain 25,0%. Đây là quốc gia được ghi nhận trong dataset, không phải quê quán. Median estimated salary là 92.916 và median balance là 98.650, nhưng dataset không ghi đơn vị tiền tệ; hai số này không phải thu nhập thực hay giá trị mang lại cho ngân hàng.

Trong kịch bản mô phỏng, 698 khách (30,3%) được gắn tín hiệu đã liên hệ dịch vụ; 565 khách (24,5%) có tín hiệu hoạt động thấp. Đây là **đầu vào để thiết kế thử nghiệm**, không phải lời giải thích đã được khách hàng xác nhận.

**Chiến lược ngắn hạn, 0–90 ngày**

- Với tín hiệu liên hệ dịch vụ: Customer Care gọi lại hoặc nhắn trong ứng dụng để xác nhận vấn đề, theo dõi đến khi đóng case. Không gửi ưu đãi khi case còn mở.
- Với tín hiệu hoạt động thấp: CRM gửi một hành trình ngắn, tối đa theo contact policy, hướng dẫn một việc hữu ích cụ thể thay vì giảm giá đại trà.
- Owner: CRM Lifecycle chịu trách nhiệm hành trình; Customer Care chịu trách nhiệm case; Product chịu trách nhiệm sửa điểm gây khó dùng được phát hiện.

**Chiến lược dài hạn, 3–12 tháng**

- Ghi nhận reason-for-contact, loại lỗi, thời gian giải quyết, consent, kênh ưa thích và hoạt động thật sau can thiệp.
- Xây dựng luồng “phát hiện sớm suy giảm sử dụng”, chỉ sau khi có dữ liệu giao dịch thật theo thời gian.

**KPI và điều kiện quyết định**

- Leading KPI tuần: tỷ lệ nhận liên hệ, hoàn thành journey, case được xử lý đúng SLA, active days và logins.
- KPI 90 ngày: chênh lệch tỷ lệ active month và retention giữa treatment/control.
- Thành công: ước lượng incremental retention dương, cận dưới CI 95% lớn hơn 0, không vi phạm guardrail và Finance xác nhận đạt break-even.
- Dừng ngay: breach consent, gửi sai suppression list, hoặc sự cố service nghiêm trọng. Tạm dừng chiến dịch nếu opt-out, complaint hoặc contact fatigue vượt ngưỡng đã được CRM/Risk phê duyệt trước khi chạy.

### 2. Nhóm đang gắn bó nhưng quy mô lớn

Nhóm này có trung bình 3,9 giao dịch, 4,9 lần đăng nhập mỗi tháng và hoạt động trong toàn bộ sáu tháng mô phỏng. Tỷ lệ giao dịch trên kênh số là 62,2%. Đây không phải là lời khẳng định họ hài lòng; chỉ nói rằng trong kịch bản, nhịp dùng dịch vụ cao hơn nhóm tái kích hoạt.

Tuổi trung bình là 38,6; 45,1% nữ và 54,9% nam. France chiếm 50,1%, Germany 25,2%, Spain 24,7%. Median estimated salary 102.300 và median balance 96.675, cùng giới hạn diễn giải như trên. Có 57,0% khách có cờ active-member.

Kịch bản mô phỏng ghi nhận 2.142 khách (27,8%) có service-contact signal và 1.515 khách (19,7%) có digital self-service signal. Vì đây là dữ liệu sinh, ngân hàng phải coi chúng là các nhánh hành trình cần kiểm nghiệm, không phải nhu cầu đã biết.

**Chiến lược ngắn hạn, 0–90 ngày**

- Với service-contact signal: ưu tiên giải quyết case, minh bạch trạng thái xử lý và chỉ đề xuất bước tiếp theo sau khi khách xác nhận vấn đề đã xong.
- Với digital self-service signal: thử hướng dẫn theo ngữ cảnh trong app, ví dụ cách hoàn thành tác vụ thường gặp. So sánh với nội dung trung lập.
- Với phần còn lại: thử một value/product review mang tính tư vấn, không mặc định bán thêm hay tặng tiền.

**Chiến lược dài hạn, 3–12 tháng**

- Product xây event taxonomy để biết khách bỏ dở bước nào, feature nào gây support contact, và tính năng nào được dùng sau education.
- CRM xây policy giới hạn tần suất liên hệ; Risk/Compliance kiểm tra chênh lệch exposure theo giới tính và country ở mức tổng hợp.

**KPI và điều kiện quyết định**

- Leading KPI: self-service completion, case-resolution time, repeat contact, completion của product review.
- KPI 90 ngày: retention tăng thêm so với control; không dùng tỷ lệ churn hiện tại thay cho uplift.
- Scale: chỉ scale khi cận dưới CI 95% của hiệu quả retention dương, chi phí trên mỗi khách giữ lại nằm dưới ngưỡng Finance phê duyệt, và complaint/opt-out không xấu hơn control.

## Thiết kế A/B test và policy bảo vệ khách hàng

Mỗi treatment phải có control, danh sách eligibility được đóng băng trước randomization, và log đầy đủ treatment, time, channel, cost, outcome. Randomization diễn ra trong từng segment để không so sánh nhầm hai nhóm khách khác nhau.

Không dùng gender, country, salary estimate hay balance để quyết định offer. Chúng chỉ dùng để kiểm tra fairness: tỷ lệ được mời, được liên hệ, opt-out, complaint và hiệu quả treatment có chênh lệch bất thường hay không. Không contact khách không consent, khách đang có complaint chưa xử lý, hoặc khách vượt contact cap.

## Rủi ro CEO cần quản lý

| Rủi ro | Cách giảm thiểu | Owner |
| --- | --- | --- |
| Ưu đãi làm giảm margin nhưng không giữ được khách | Finance duyệt break-even trước scale | CFO / Finance |
| Promotion đến khách đang bức xúc | Tách service recovery khỏi marketing, mở complaint thì suppress | Customer Care / CRM |
| Contact quá nhiều | Frequency cap, consent, opt-out theo thời gian thực | CRM / Compliance |
| Nhầm simulation với hành vi thật | Badge nguồn dữ liệu trên dashboard; thay bằng event thật theo roadmap | Data Product |
| Nhóm 3–4 sản phẩm quá nhỏ hoặc bất thường | Không đưa ra policy rộng; review thủ công và kiểm tra data quality | Risk / Analytics |

## Call to action trong 30 ngày

CEO cần chỉ định ba owner: CRM cho pilot, Product/Care cho hành trình xử lý vấn đề, Finance cho giả định break-even. Trong 30 ngày, đội dự án phải mang lại danh sách eligible đã có consent, contact policy, cost assumptions, definition của retention 90 ngày và kế hoạch randomization. Không đủ năm điều kiện này thì không chạy campaign.

## Phụ lục bằng chứng kỹ thuật

Metric/figure chi tiết: [board evidence document](segmentation_v2_board_document.md), [method comparison](../reports/segmentation/v2/method_summary.csv), [persona profiles](../reports/segmentation/v2/segment_static_personas.csv), [churn cross-tab](../reports/segmentation/v2/segment_churn_cross_tab.csv), [figures](../reports/segmentation/v2/figures/).
