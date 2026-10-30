# Edge - a pending UPI payment resolves

Scenario `edge_pending_upi` · pack kirana

## Scene 1: Pending then success
- **1.1** (P1) · 37 ms: Bill and a pending payment
- **1.2** (P1) · screen pay · 209 ms: The customer's bank says pending
- **1.3** (P1) · 188 ms: The bank confirms; the bill closes
