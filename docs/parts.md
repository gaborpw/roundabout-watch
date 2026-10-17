# Parts list

Everything to buy, as a checklist, for the camera behind Peter's
second-floor window (ADR 0005) and the Jetson next to it (ADR 0003).
Prices and stock were read on **2026-10-17** from each store's own product
data. Re-check before ordering.

Several big stores (Amazon, B&H, Newegg, Micro Center, Best Buy, Walmart)
blocked the automated check, so these are the stores that could be read,
not necessarily the cheapest. Buy elsewhere only if it's the **exact model
number**.

## How it connects

```
 [Reolink CX410, lens against the glass]
        │ Cat6, 10 ft
 [UniFi PoE Adapter]  ── plugs into the wall; powers the camera over the cable
        │ Cat6, 3 ft
 [Jetson Orin Nano Super] ── Wi-Fi to the home network
```

The camera's only connection is the cable to the Jetson, so it can't reach
the internet (CLAUDE.md 22).

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

- [ ] **NVIDIA Jetson Orin Nano Super Developer Kit**: runs the detector
  beside the camera, so footage never leaves the house (ADR 0003).
  - Quantity: 1.
  - Two places to buy:
    - [SparkFun](https://www.sparkfun.com/nvidia-jetson-orin-nano-developer-kit.html):
      **$399.00**, **back-ordered**.
    - [Seeed Studio bundle](https://www.seeedstudio.com/NVIDIAr-Jetson-Orintm-Nano-Super-Developer-Kit-Bundle.html):
      **$450.30**, in stock per its page data, limit 1; which warehouse
      ships it is unknown.
  - It comes with no storage.
  - The power supply is included (general knowledge; check the box
    contents).

- [ ] **1 TB NVMe SSD (M.2 2280)**: for the system, 72 hours of recording
  and the clips (ADR 0006).
  - Quantity: 1.
  - Link: [SanDisk SSD Plus M.2 NVMe 1TB, SDSSDA3N-1T00-G26](https://www.sandisk.com/products/ssd/internal-ssd/sandisk-ssd-plus-m2-nvme)
  - Price: **$287.99**, in stock per SanDisk's store data.
  - The Samsung 990 EVO Plus 1TB ($289.99) and WD Blue SN5000 1TB were out
    of stock. A 500 GB drive should fit 72 hours by the storage estimate, but
    none was confirmed in stock.

- [ ] **trueCABLE Cat6, 10 ft**: camera to PoE adapter.
  - Measure first; 14 ft is $12.25 if 10 ft is short.
  - Quantity: 1.
  - Link: [trueCABLE Cat6 patch cable](https://www.truecable.com/products/cat6-unshielded-28awg-component-rated-patch-cord-cm-jacket)
  - Price: **$10.49**. In stock in blue or yellow.

- [ ] **trueCABLE Cat6, 3 ft**: PoE adapter to Jetson.
  - Quantity: 1.
  - Link: [trueCABLE Cat6 patch cable](https://www.truecable.com/products/cat6-unshielded-28awg-component-rated-patch-cord-cm-jacket)
  - Price: **$7.51**. In stock in blue, white, black or green.

- [ ] *(Optional)* **CyberPower ST425 UPS** (260 W): rides out short power
  cuts so recording doesn't stop and the drive isn't corrupted.
  - Link: [ST425](https://www.cyberpowersystems.com/product/ups/standby/st425/)
  - Price: **$64.95** list price; stock can't be checked on the
    manufacturer's page.

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
| Jetson Orin Nano Super (SparkFun, back-ordered) | $399.00 |
| 1 TB NVMe SSD (SanDisk) | $287.99 |
| trueCABLE Cat6, 10 ft + 3 ft | $18.00 |
| **Total** | **$797.98** |
| UPS, optional (ST425) | +$64.95 |
| Jetson from Seeed instead (in stock) | +$51.30 |

Before tax, shipping and hardware-store items. The first, outdoor version
of this list came to $1,118.51; the window removes:

- the outdoor camera;
- its junction box;
- the outdoor cable;
- the surge protector;
- the PoE switch.

## Probably already owned (check before buying)

For the Jetson's first setup only:

- a DisplayPort monitor, or a DisplayPort-to-HDMI adapter;
- a USB keyboard and mouse;
- a USB stick of 16 GB or more.

For the camera's one-time setup: a phone or computer with Reolink's app or
desktop client (ADR 0005).

## Sources (read 2026-10-17)

- Every product: its own page, linked above (price and stock from the page's
  built-in offer data where the page draws them by script).
- Jetson price rise from $249 to $399: CNX Software, 2026-07-22 (via the
  research notes).
