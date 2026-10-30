# Edge - a pending UPI payment resolves

Scenario `edge_pending_upi` · pack kirana

## Scene 1: Pending then success
- **1.1** (P1) · 28 ms: Bill and a pending payment
- **1.2** (P1) · screen pay · 256 ms: The customer's bank says pending
- **1.3** (P1) · 203 ms: The bank confirms; the bill closes
