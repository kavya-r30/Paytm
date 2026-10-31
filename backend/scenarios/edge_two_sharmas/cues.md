# Edge - two Sharmas on the khata

Scenario `edge_two_sharmas` · pack kirana

## Scene 1: Two khata customers share a surname
- **1.1** (P1) · 37 ms: Ramesh Sharma and Sunil Sharma both run a khata
- **1.2** (P1) · 22 ms: Sunil Sharma joins
- **1.3** (P1) · 152 ms: Both get a ₹5,000 khata

## Scene 2: Arth asks which Sharma instead of guessing
- **2.1** (P1) · 124 ms: "Sharma ji ne 200 jama kiye" → "Kaun se Sharma ji?" (nothing posted)
- **2.2** (P1) · 44 ms: "Ramesh Sharma ne 200 jama kiye" → read-back for Ramesh only (R2)
- **2.3** (P1) · 194 ms: "Haan" posts it; books and audit hold
