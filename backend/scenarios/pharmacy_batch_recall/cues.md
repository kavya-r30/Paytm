# A distributor recall at the pharmacy

Scenario `pharmacy_batch_recall` · pack pharmacy

## Scene 1: Recall a batch, list buyers, block sales
- **1.1** (P1) · 53 ms: The distributor recalls the Amoxicillin batch
- **1.2** (P1) · screen rx · 149 ms: Mark the batch recalled → buyers listed, the Curator opens a recall work item
- **1.3** (P2) · 50 ms: Billing the recalled batch is impossible; "Rx dekha" is recorded for the rest
- **1.4** (P2) · 135 ms: Add the recalled medicine and try to check out
