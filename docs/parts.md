# Parts list

Everything to buy, as a checklist, for the camera behind Peter's
second-floor window (ADR 0005). Peter's own desktop runs the analysis
(ADR 0011), so the camera and its power are all there is to buy. Prices and
stock were read on **2026-10-17** from each store's own product data.
Re-check before ordering.

Several big stores (Amazon, B&H, Newegg, Micro Center, Best Buy, Walmart)
blocked the automated check, so these are the stores that could be read,
not necessarily the cheapest. Buy elsewhere only if it's the **exact model
number**.

## How it connects

```
 [Reolink CX410, lens against the glass]
        │ network cable into the adapter's PoE port
 [UniFi PoE Adapter]  ── plugs into the wall; powers the camera over the cable
        │ network cable from the adapter's LAN port
 [Peter's desktop, Ethernet port] ── its own internet is over Wi-Fi
```

The camera's only connection is the cable to the desktop, with no gateway
set on either end, so it can't reach the internet (CLAUDE.md 22, ADR 0011).

## To buy

- [ ] **Reolink CX410**: the camera (ADR 0005).
  - 4 MP, 1/1.8" sensor, F1.0, 89° view.
  - No infrared, which would reflect off the glass.
  - H.264, RTSP and ONVIF; powered over the network cable (PoE 802.3af).
  - Quantity: 1.
  - Link: [Reolink CX410](https://reolink.com/us/product/cx410/)
  - Price: **$84.99**, in stock.
  - Alternative: [Reolink E1 Outdoor](https://reolink.com/us/product/e1-outdoor/),
    $113.99. It has a 3× zoom, but at 9–12 m it's worse (20 fps, smaller
    sensor, 12 V adapter).

- [ ] **UniFi PoE Adapter (15W)**: powers the camera through its network
  cable (48 V, 0.32 A, gigabit). The camera's own 12 V adapter is sold
  separately, so this replaces it.
  - Quantity: 1.
  - Link: [UniFi PoE Adapter (15W)](https://store.ui.com/us/en/category/accessories-poe-power/collections/pro-store-poe-and-power-adapters/products/u-poe-af)
  - Price: **$8.00**, in stock.
  - Ubiquiti's page doesn't name the 802.3af standard; resellers list this
    adapter (U-POE-af) as 802.3af. Check that the camera powers up when it
    arrives.

Peter already has network cables (Probably already owned, below). Buy these
only if his are too short:

- [ ] *(If needed)* **trueCABLE Cat6, 10 ft**: camera to PoE adapter.
  - Measure first; 14 ft is $12.25 if 10 ft is short.
  - Quantity: 1.
  - Link: [trueCABLE Cat6 patch cable](https://www.truecable.com/products/cat6-unshielded-28awg-component-rated-patch-cord-cm-jacket)
  - Price: **$10.49**. In stock in blue or yellow.

- [ ] *(If needed)* **trueCABLE Cat6, 3 ft**: PoE adapter to the desktop.
  - Quantity: 1.
  - Link: [trueCABLE Cat6 patch cable](https://www.truecable.com/products/cat6-unshielded-28awg-component-rated-patch-cord-cm-jacket)
  - Price: **$7.51**. In stock in blue, white, black or green.

### From a hardware store (no links)

- Something to hold the camera with its lens against the glass, using its
  own bracket: screws into the window frame or a sill shelf, or strong
  double-sided mounting tape.
- Black foam or dark cloth around the lens, so the room doesn't reflect in
  the glass at night.

## Total

| Part | Price |
|---|---|
| Reolink CX410 | $84.99 |
| UniFi PoE Adapter (15W) | $8.00 |
| **Total** | **$92.99** |
| Cables, only if Peter's are too short (10 ft + 3 ft) | +$18.00 |

Before tax, shipping and hardware-store items. Earlier versions of this list:

- $1,118.51 for an outdoor camera, with its junction box, outdoor cable,
  surge protector and PoE switch;
- $797.98 for the window, with a Jetson ($399.00), a 1 TB SSD ($287.99) and
  an optional UPS. Peter's desktop replaced them (ADR 0011).

## Probably already owned (check before buying)

- **The desktop with the RTX 3080 Ti**, near the window (ADR 0011), with two
  12 TB hard drives: far more than a day of recording needs (ADR 0006).
- **Two network cables** (Peter, 2026-10-17: "i have oing ethernet cords"):
  camera to PoE adapter, and adapter to desktop. Cat5e or Cat6 both carry
  the camera's power (general knowledge).
- **The M4 MacBook Air**, for testing on recorded video.
- For the camera's one-time setup: Reolink's app or desktop client
  (ADR 0005).

## Sources (read 2026-10-17)

- Every product: its own page, linked above (price and stock from the page's
  built-in offer data where the page draws them by script).
