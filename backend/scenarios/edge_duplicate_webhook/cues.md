# Edge - the rails deliver the same webhook twice

Scenario `edge_duplicate_webhook` · pack kirana

## Scene 1: Duplicate delivery is idempotent; a second real payment is flagged
- **1.1** (P1) · 28 ms: Fault injected, then a QR payment
- **1.2** (P1) · 237 ms: Add and pay; the webhook arrives twice
- **1.3** (P1) · 165 ms: Priya pays again by static QR - a duplicate payment, flagged with an R4 refund suggestion
