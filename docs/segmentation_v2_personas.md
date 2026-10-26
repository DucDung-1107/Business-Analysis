# Persona khach hang va chien luoc thu nghiem - Segmentation V2

> **Canh bao pham vi:** Ho so co hai lop du lieu. Gioi tinh, quoc gia theo truong `country`, tuoi, so du, luong uoc tinh, san pham va trang thai thanh vien la truong tinh cua Kaggle. Giao dich, dang nhap, khieu nai va tin hieu pain-point/nhu cau duoc sinh bang Python cho bai tap. Khong co truong nao cho phep ket luan ly do roi bo that, nhu cau da phat bieu, hay hieu qua uu dai.

## Du lieu da duoc kiem tra

- Phien ban goc: `v1-90f6625c31bd-baeb8804`, 10,000 khach hang; nhan churn tinh duoc tach khoi dau vao clustering.
- Ba cach clustering da duoc so sanh trong tai lieu quyet dinh: K-Means, Gaussian Mixture va Ward hierarchical. Cac metric do do tach/stability cua du lieu hanh vi mo phong, khong do gia tri thuong mai.
- Cac ty le churn ben duoi la cross-tab cua nhan Kaggle sau khi gan segment, co khoang tin cay Wilson 95%. Day la mo ta lich su/tinh, khong phai du bao quy tiep theo.
- Scenario pain/need duoc sinh khong dung nhan churn. Kiem tra ky thuat gom: seed co the tai lap, mot dong/khach hang, khong null, chi nam trong tap scenario da khai bao, va label tach biet.

## Quy tac su dung an toan

- `country` chi la quoc gia trong source, khong phai que quan, quoc tich hay dan toc.
- `estimated_salary` dung don vi tien te khong ro; khong goi la thu nhap thuc te va khong dung lam gia tri khach hang.
- Gioi tinh va quoc gia chi dung de mo ta/tinh cong bang sau thi nghiem; khong dung de quyet dinh uu dai, kenh, gia hay dieu kien tham gia.

## Persona chi tiet

### segment_02 - Low-activity customers

**Quy mo va churn da quan sat:** 4,981 khach hang (49.8% mau). Churn tinh: 1,324/4,981 = 26.6%; Wilson 95%: 25.4%-27.8%; toan mau: 20.4%.

**Chan dung tinh (du lieu Kaggle):** France 49.9%, Germany 25.5%, Spain 24.6%; female 45.8%, male 54.2%. Tuoi trung binh 40.1, tuoi trung vi 38.0. Luong uoc tinh trung vi 92982.6, so du trung vi 99340.8 (don vi source khong ro). Trung binh 1.5 san pham; 12.9% co co active_member=1.

**Hanh vi V2 mo phong:** Observed in the synthetic behavioural extension: mean monthly transactions 2.8, mean monthly spend 81.5, mean logins 3.5, monthly inflow 3093.2, failed payments 0.06, and unresolved-case share 9.7%. Ty le giao dich digital trung binh 53.4%; ty le thang co hoat dong 92.3%; recency 0.09 ky mo phong. Day la dau ra simulation, khong phai lich su giao dich that.

**Pain-point va mong cau trong kich ban mo phong:** No simulated friction signal: 43.6%; can test: Test value or product-fit review, if consented; Simulated service-contact signal: 33.4%; can test: Test issue resolution before any retention incentive; Simulated low-activity signal: 19.6%; can test: Test whether feature discovery or a simpler return journey improves active use Khong duoc doc nhu phan hoi hay ly do roi bo cua khach hang that.

**Chien luoc de kiem chung:** Test a low-cost reactivation journey focused on relevant digital-bank features, not blanket discounts. Kenh: Consent-aware in-app/email journey. Chu so huu: CRM Lifecycle Team.

**A/B test:** random hoa khach hang du dieu kien va da dong y trong chinh segment nay: treatment la journey o tren; control la trai nghiem trung lap/khong gui journey. KPI chinh: Incremental 90-day active-month rate and retention versus randomized control. Guardrail: Opt-outs, contact frequency and complaint rate. Stop if guardrails worsen beyond a pre-specified tolerance; scale only if confidence intervals support positive incremental retention and unit economics pass break-even.

### segment_01 - High-engagement, higher-spend customers

**Quy mo va churn da quan sat:** 5,019 khach hang (50.2% mau). Churn tinh: 713/5,019 = 14.2%; Wilson 95%: 13.3%-15.2%; toan mau: 20.4%.

**Chan dung tinh (du lieu Kaggle):** France 50.3%, Germany 24.7%, Spain 25.0%; female 45.0%, male 55.0%. Tuoi trung binh 37.8, tuoi trung vi 36.0. Luong uoc tinh trung vi 106655.9, so du trung vi 94631.3 (don vi source khong ro). Trung binh 1.6 san pham; 89.8% co co active_member=1.

**Hanh vi V2 mo phong:** Observed in the synthetic behavioural extension: mean monthly transactions 4.4, mean monthly spend 131.4, mean logins 5.8, monthly inflow 7430.8, failed payments 0.04, and unresolved-case share 6.7%. Ty le giao dich digital trung binh 69.0%; ty le thang co hoat dong 98.5%; recency 0.01 ky mo phong. Day la dau ra simulation, khong phai lich su giao dich that.

**Pain-point va mong cau trong kich ban mo phong:** No simulated friction signal: 44.0%; can test: Test value or product-fit review, if consented; Simulated digital self-service signal: 31.7%; can test: Test contextual self-service education rather than a blanket incentive; Simulated service-contact signal: 24.0%; can test: Test issue resolution before any retention incentive Khong duoc doc nhu phan hoi hay ly do roi bo cua khach hang that.

**Chien luoc de kiem chung:** Test proactive value review or product-fit support; reserve incentives for experimentally eligible customers. Kenh: In-app prompt or relationship-manager outreach where consented. Chu so huu: Retention + Product.

**A/B test:** random hoa khach hang du dieu kien va da dong y trong chinh segment nay: treatment la journey o tren; control la trai nghiem trung lap/khong gui journey. KPI chinh: Incremental retention and product-fit completion versus randomized control. Guardrail: Incentive cost per retained customer and contact fatigue. Stop if guardrails worsen beyond a pre-specified tolerance; scale only if confidence intervals support positive incremental retention and unit economics pass break-even.

## Nhieu goc nhin bo sung tu du lieu tinh

Bang sau khong phai cluster. Day la cac lens tao truoc khi join churn de bo sung goc nhin relationship, do sau san pham va so du. Dung de lap ke hoach cong suat va phan tich ket qua A/B, khong dung de suy ra ly do roi bo.

| lens | group | customer_count | customer_share | historical_churn_count | historical_churn_rate | churn_rate_ci95_low | churn_rate_ci95_high |
| --- | --- | --- | --- | --- | --- | --- | --- |
| balance_lens | Positive balance: middle third | 2127 | 0.213 | 587 | 0.276 | 0.257 | 0.295 |
| balance_lens | Positive balance: upper third | 2128 | 0.213 | 493 | 0.232 | 0.214 | 0.250 |
| balance_lens | Positive balance: lower third | 2128 | 0.213 | 457 | 0.215 | 0.198 | 0.233 |
| balance_lens | Zero recorded balance | 3617 | 0.362 | 500 | 0.138 | 0.127 | 0.150 |
| product_lens | 4 products | 60 | 0.006 | 60 | 1.000 | 0.940 | 1.000 |
| product_lens | 3 products | 266 | 0.027 | 220 | 0.827 | 0.777 | 0.868 |
| product_lens | 1 product | 5084 | 0.508 | 1409 | 0.277 | 0.265 | 0.290 |
| product_lens | 2 products | 4590 | 0.459 | 348 | 0.076 | 0.069 | 0.084 |
| relationship_lens | Recorded not-active member | 4849 | 0.485 | 1302 | 0.269 | 0.256 | 0.281 |
| relationship_lens | Recorded active member | 5151 | 0.515 | 735 | 0.143 | 0.133 | 0.153 |

## Thong tin con thieu truoc khi goi day la insight khach hang that

Can thu thap co governance: reason-for-close/cancel, noi dung va loai ticket, survey nhu cau va su hai long, preference/consent kenh, campaign assignment, chi phi, CLV/margin, va outcome retention theo mot cua so thoi gian that. Khi co, thay the scenario mo phong bang su kien quan sat va danh gia uplift bang A/B test.
