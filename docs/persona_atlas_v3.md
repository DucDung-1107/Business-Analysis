# Persona Atlas V3 — hồ sơ khách hàng để CEO và các đội vận hành cùng dùng

## Cách đọc atlas

Các số về tuổi, giới tính, quốc gia, credit score, tenure, balance, sản phẩm, active-member và churn là dữ liệu Kaggle tĩnh. Dòng tiền, app feature, failed payment, service case, mục tiêu và pain point là kịch bản mô phỏng sáu tháng. Persona không phải một con người có thật; đó là một mô tả vận hành của một nhóm khách có cùng mẫu hành vi.

## Persona 1 — Linh, khách tự phục vụ số đều đặn

**Quy mô:** 5.285 khách, 52,9% danh mục; 751 nhãn churn lịch sử, 14,2%.

**Chân dung:** tuổi trung bình 39,6; credit score trung bình 653,2; khoảng 44% là nữ. Nhóm phân bố gần một nửa France, phần còn lại Germany/Spain. Họ có khoảng 1,5 sản phẩm và phần lớn mang cờ active-member. Salary estimate median khoảng 100.240, balance median khoảng 95.984, đơn vị tiền tệ không rõ. Những số này không phải thu nhập, tài sản hay CLV thực.

**Một tháng điển hình trong kịch bản mô phỏng:** Linh mở ứng dụng khoảng 11 ngày. Cô thường vào để chuyển tiền hoặc thanh toán hóa đơn; đây là hành vi chính trong 26.472 lượt khách-tháng. Một phần khác, 4.308 lượt khách-tháng, dùng ứng dụng để kiểm tra số dư, xem trạng thái giao dịch thẻ hoặc quản lý thẻ. Dòng tiền vào xuất hiện gần năm trong sáu tháng. Số lần thanh toán không hoàn tất và tỷ lệ yêu cầu hỗ trợ chưa xử lý xong thấp hơn persona còn lại.

**Điều Linh cần từ ngân hàng:** hoàn thành tác vụ nhanh, biết trạng thái giao dịch và được hỗ trợ ngay khi thao tác lỗi. Đây là giả thuyết product từ simulation, không phải khảo sát khách hàng.

**SWOT:** Strength: đã hình thành thói quen số. Weakness: một lỗi trong tác vụ thường dùng có thể phá trải nghiệm. Opportunity: giảm support contact bằng hướng dẫn theo ngữ cảnh. Threat: gửi lời mời bán hàng không liên quan làm tăng contact fatigue.

**Action:** khi Linh mở luồng bill/transfer, thử Digital Concierge với shortcut và trạng thái xử lý; đối chứng là Value Review, giải thích fee/benefit hiện có rồi để khách chọn tiếp. Product chịu completion; CRM chịu consent/contact cap; Care nhận escalation. KPI: completion, repeat contact, opt-out; sau 90 ngày là retention effect với CI 95%.

## Persona 2 — Minh, quan hệ số thưa và cần phục hồi

**Quy mô:** 4.715 khách, 47,2% danh mục; 1.286 nhãn churn lịch sử, 27,3%. Đây là cohort cần ưu tiên.

**Chân dung:** tuổi trung bình 38,2; credit score trung bình 647,5; khoảng 47% là nữ. Balance và salary estimate median gần Persona 1, nhưng active-member rất thấp. Bài học: số dư không nói khách đang gắn bó.

**Một tháng điển hình trong kịch bản mô phỏng:** Minh chỉ dùng ứng dụng khoảng bốn ngày mỗi tháng. Phần lớn lần truy cập chỉ để xem số dư hoặc kiểm tra tình trạng tài khoản; khách thường rời ứng dụng trước khi chuyển tiền hay thanh toán hóa đơn. Dòng tiền vào xuất hiện thưa hơn. Số lần thanh toán không hoàn tất và tỷ lệ yêu cầu hỗ trợ chưa xử lý xong cao hơn. Đây không phải “khách xấu”; đây là khách mà ngân hàng chưa tạo được nhịp sử dụng ổn định.

**Điều Minh có thể cần:** một vấn đề dịch vụ được xử lý đến nơi đến chốn, hoặc một đường quay lại sử dụng dịch vụ đơn giản. Đây là hai giả thuyết phải kiểm chứng.

**SWOT:** Strength: vẫn còn tài khoản và khả năng quay lại. Weakness: thói quen số mỏng. Opportunity: service recovery trước marketing. Threat: gửi promotion khi case chưa xong có thể làm khách rời đi nhanh hơn.

**Action:** khách có case mở đi thẳng vào Service Recovery với owner/SLA/closure confirmation. Khách không có case mở được randomize giữa Service Recovery proactive và Reactivation Coach 14 ngày. KPI: SLA closure, reopen, active days, failed payment, 90-day retention. Consent breach hoặc route sai case mở là hard stop.

## Không được làm

Không dùng gender, country, salary estimate hay balance để quyết định offer. Không gọi “Linh/Minh” là khách thật. Không gọi hành vi mô phỏng là lý do churn đã xác minh.
