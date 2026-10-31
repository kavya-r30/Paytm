# Edge - every AI provider is down

Scenario `edge_provider_outage` · pack kirana

## Scene 1: The counter and grounded answers keep working
- **1.1** (P1) · 76 ms: Providers down; "Aaj kitna aaya?" still answers (fast path + templates)
- **1.2** (P1) · 57 ms: A free-form question degrades politely instead of failing
