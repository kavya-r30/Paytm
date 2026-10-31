# Edge - the device bills offline and replays its queue

Scenario `edge_offline_billing` · pack kirana

## Scene 1: Billing while the network is down
- **1.1** (P1) · 27 ms: Wi-Fi drops; the device keeps billing and queues each command with its own key
- **1.2** (P1) · 172 ms: A kilo of sugar, paid in cash, all queued

## Scene 2: Back online, the queue replays and nothing doubles
- **2.1** (P1) · 6 ms: The flaky reconnect sends the whole queue again
- **2.2** (P1) · 148 ms: Add and checkout replay; the bill stays ₹45 and closed
