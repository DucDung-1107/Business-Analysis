# V2 data architecture and ERD

## Design basis

The design separates an account/customer profile from dated behavioural facts. This follows the common account-to-transaction pattern illustrated by the [FDX open-finance overview](https://fdx1dev.financialdataexchange.org/wp-content/uploads/2026/02/ABCs_of_APIs_FINAL_1.pdf), and keeps merchant/channel fields separate from the customer. Merchant/category examples are informed by Visa's documented transaction-enrichment fields, including merchant category, merchant location and payment-acceptance method ([Visa Merchant Search](https://developer.visa.com/api-reference/merchant_search)). These references guide the schema only; they do not supply project data or validate the synthetic values.

```mermaid
erDiagram
    CUSTOMER_BASE ||--o{ CUSTOMER_SNAPSHOT : has
    CUSTOMER_BASE ||--o{ TRANSACTION_MONTH : generates
    CUSTOMER_BASE ||--o{ DIGITAL_MONTH : uses
    CUSTOMER_BASE ||--o{ SERVICE_CASE : raises
    CUSTOMER_BASE ||--o{ FEATURE_SNAPSHOT : receives
    FEATURE_SNAPSHOT ||--o{ SEGMENT_ASSIGNMENT : assigned
    CUSTOMER_BASE ||--o{ CHURN_LABEL : has_static_label

    CUSTOMER_BASE {
        string customer_id PK
        string country
        string gender
        int age_years
        int tenure_years
        float balance_snapshot
        int products_number
        int active_member_flag
        float estimated_salary
        string source_type
    }
    CUSTOMER_SNAPSHOT {
        string customer_id FK
        int simulated_month_index
        string cutoff_type
        string source_type
    }
    TRANSACTION_MONTH {
        string customer_id FK
        int simulated_month_index
        string channel
        string transaction_type
        int transaction_count
        float transaction_amount
        string source_type
    }
    DIGITAL_MONTH {
        string customer_id FK
        int simulated_month_index
        int app_sessions
        int active_days
        int digital_transactions
        string source_type
    }
    SERVICE_CASE {
        string service_case_id PK
        string customer_id FK
        int opened_month_index
        int resolved_month_index
        string severity
        string status
        string source_type
    }
    FEATURE_SNAPSHOT {
        string customer_id FK
        int cutoff_month_index
        float rfm_features
        float trend_features
        float service_features
        string source_type
    }
    SEGMENT_ASSIGNMENT {
        string customer_id FK
        string segment_id
        string segmentation_version
    }
    CHURN_LABEL {
        string customer_id FK
        int churn
        string source_type
    }
```

## Grains and non-negotiable joins

| Table | Grain | Join / integrity rule | Source class |
| --- | --- | --- | --- |
| `customer_base` | one customer | unique `customer_id` | `OBSERVED_STATIC_DATA` |
| `customer_snapshot` | customer x simulated month | exactly six rows/customer; no churn field | `SYNTHETIC_BEHAVIOR` |
| `transaction_month` | customer x simulated month x channel x transaction type | non-negative counts/amounts; sum reconciles to monthly total | `SYNTHETIC_BEHAVIOR` |
| `digital_month` | customer x simulated month | active days 0-31; sessions >= active days | `SYNTHETIC_BEHAVIOR` |
| `service_case` | simulated case | resolved month >= opened month when resolved | `SYNTHETIC_BEHAVIOR` |
| `feature_snapshot` | customer x cutoff | features use periods at/before cutoff only | `SYNTHETIC_BEHAVIOR` |
| `churn_label` | one customer | held separate until post-cluster cross-tab | `OBSERVED_STATIC_DATA` |

## Demographic boundary

The Kaggle base only supports country, binary gender field, age, tenure, estimated salary, balance, product count, card flag and active-member flag. It does not support household composition, education, occupation, hometown, ethnicity, disability, stated needs or consent. Those fields are neither fabricated as observed facts nor used to target customers.
