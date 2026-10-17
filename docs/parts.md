# Parts list

Everything to buy, as a checklist. Prices and stock were read on
**2026-10-17**, from each store's own page unless it says otherwise.
Re-check before ordering: stock below says "only 3 left" in places.
Why each part was chosen is in ADR 0005 (camera) and ADR 0003 (computer).

Several big stores (Amazon, B&H, Newegg, Micro Center, Best Buy, Walmart,
amcrest.com) blocked the automated check, so the links below are the stores
that could be read, not necessarily the cheapest. If you find a part
cheaper elsewhere, make sure it's the **exact model number**.

## How it connects

```
 [Camera] ──outdoor Cat6── [surge protector, grounded] ── wall ── [PoE switch] ── [Jetson]
                                                                     ▲                │
                                                              camera gets power      Wi-Fi to the home network
                                                              and data here          (the camera never reaches it)
```

The switch holds only the camera and the Jetson, so the camera has no route
to the internet (CLAUDE.md 22). The Jetson reaches the internet over its
own Wi-Fi.

## To buy

### The camera

- [ ] **EmpireTech IPC-T54IR-ZE-S3** (a Dahua camera sold under EmpireTech's
  name). 4 MP, 1/1.8" sensor, motorised 2.7–12 mm zoom, RTSP, ONVIF, H.264,
  PoE (8.2 W max), IP67, infrared to 40 m.
  - Why: Frigate's own docs rank Dahua first for reliable RTSP streams, and
    the large sensor matters most at night.
  - Quantity: 1.
  - Store: EmpireTech, which ships from US and Canadian warehouses in 4–8
    working days.
  - Link: [IPC-T54IR-ZE-S3](https://empiretech01.com/products/empiretech-ipc-t54ir-ze-s3-1-1-8-cmos-4mp-ir-starlight-vari-focal-turret-security-camera)
  - Price: **$261.24**, "Only 14 left" (2026-10-17).
  - **Before buying, read ADR 0005, "The FCC question".** Dahua is on the
    FCC Covered List.
  - Alternatives:
    - **Amcrest IP5M-VT1289EW-AI**: [IP Security Depot](https://www.ipsecuritydepot.com/amcrest-5mp-ai-ip-poe-camera-turret-5x-optical-zoom-ip5m-vt1289ew-ai/ip5m-vt1289ew-ai/),
      $151.99. **Back-ordered, 2–3 weeks.** Cheaper, but the smaller sensor
      gives worse night images. Amcrest cameras are made by Dahua, so the
      same FCC question applies.
    - **Hanwha Vision XNO-6083R**: [IP Security Depot](https://ipsecuritydepot.com/hanwha-xno-6083r-2mp-outdoor-ai-ir-bullet-network-ip-camera/xno-6083r),
      $1,039.99. **Back-ordered, 2–3 weeks.** Hanwha is Korean and isn't on
      the Covered List. It's 2 MP with a 2.8–12 mm motorised zoom, RTSP,
      ONVIF, H.264, PoE+ (802.3at Class 4), IP66/67. It costs four times as
      much, and its junction box is a different part (not checked).

- [ ] **EmpireTech PFA130-E junction box.** The mount made for this camera;
  it keeps the cable joint dry.
  - Quantity: 1.
  - Link: [PFA130-E](https://empiretech01.com/products/empiretech-water-proof-junction-box-bracket-pfa130-e)
  - Price: **$20.99** in white, "Only 3 left". Black is sold out.

### The computer

- [ ] **NVIDIA Jetson Orin Nano Super Developer Kit.** Runs the detector on
  its GPU beside the camera, so footage never leaves the house (ADR 0003).
  - Quantity: 1.
  - Price: NVIDIA raised it from $249 to $399 in July 2026 (CNX Software,
    2026-07-22).
  - Two places to buy:
    - [SparkFun](https://www.sparkfun.com/nvidia-jetson-orin-nano-developer-kit.html),
      **$399.00**, **back-ordered**.
    - [Seeed Studio bundle](https://www.seeedstudio.com/NVIDIAr-Jetson-Orintm-Nano-Super-Developer-Kit-Bundle.html),
      **$450.30**, in stock according to its page data, limit 1. I couldn't
      tell whether it ships from the US.
  - It comes with no storage, so it needs the drive below.
  - The power supply is included (general knowledge, check the box
    contents on the store page).
  - Alternative: a desktop or mini PC with an NVIDIA RTX 4060/5060-class
    card. It's faster and easier to install software on, but draws about
    150–300 W all day. No link checked.

- [ ] **1 TB NVMe SSD (M.2 2280).** Holds the system, 72 hours of recording
  (about 150–200 GB by an estimate still to be measured) and the clips.
  - Quantity: 1.
  - Link: [SanDisk SSD Plus M.2 NVMe 1TB, SDSSDA3N-1T00-G26](https://www.sandisk.com/products/ssd/internal-ssd/sandisk-ssd-plus-m2-nvme)
  - Price: **$287.99**, in stock according to SanDisk's store data (the
    price loads by script, so check it on the page).
  - Alternatives: the Samsung 990 EVO Plus 1TB was $289.99 and **out of
    stock**; the WD Blue SN5000 1TB was out of stock. A 500 GB drive should
    also fit 72 hours, but I didn't find one confirmed in stock.

### Network and power

- [ ] **EmpireTech POE4CH-110W PoE switch** (4 PoE ports plus 2 uplinks,
  802.3af/at, 30 W per port). Powers the camera over its network cable.
  - Quantity: 1.
  - Link: [POE4CH-110W](https://empiretech01.com/products/empiretech-poe4ch-110w-gigabit-6-port-poe-switch)
  - Price: **$59.99**, "Only 4 left".

- [ ] **Outdoor Cat6 cable, 100 ft** (wet- and UV-rated). Runs from the
  camera into the house. Measure the run first and buy the next length up.
  - Quantity: 1.
  - Link: [Primus Cable shielded outdoor Cat6](https://www.primuscable.com/products/cat6-ethernet-patch-cable-shielded-outdoor-industrial-26-awg-black)
  - Price: **$69.29** for 100 ft, with "various lead times may apply". It
    isn't sold as direct-burial cable.
  - If the cable goes underground, use [CableWholesale 10X8-722HD gel-filled](https://www.cablewholesale.com/products/network-phone/cat-6-cable/product-10x8-722hd.php)
    instead: $92.26, "contact us about availability".

- [ ] **Ubiquiti ETH-SP-G2 Ethernet surge protector.** Stops lightning on
  the outdoor cable from reaching the switch and the Jetson. It must be
  connected to ground (general knowledge).
  - Quantity: 1.
  - Link: [ETH-SP-G2](https://store.ui.com/us/en/category/accessories-poe-power/collections/pro-store-poe-and-power-surge-protection-outdoor/products/ethernet-surge-protector)
  - Price: **$12.50**, add to cart available.

- [ ] **trueCABLE Cat6 patch cable, 3 ft.** Connects the switch to the
  Jetson.
  - Quantity: 1.
  - Link: [trueCABLE Cat6 patch cord](https://www.truecable.com/products/cat6-unshielded-28awg-component-rated-patch-cord-cm-jacket)
  - Price: **$7.51**, blue and black in stock.

- [ ] *(Optional)* **CyberPower ST425 UPS** (260 W). Rides out short power
  cuts, so recording doesn't stop and the drive isn't corrupted.
  - Link: [ST425](https://www.cyberpowersystems.com/product/ups/standby/st425/)
  - Price: **$64.95** list price. Stock can't be checked on the
    manufacturer's page.

### From a hardware store (no links)

- A long 3/4"–1" drill bit to pass the cable's plug through the wall, plus
  pilot bits.
- Masonry anchors or Tapcons, and stainless screws.
- Exterior silicone or duct-seal putty, and a wall bushing.
- UV-rated cable clips and ties. Leave a drip loop where the cable enters
  the wall.
- 10 AWG ground wire and a ground clamp for the surge protector.

## Total

| Part | Price |
|---|---|
| Camera (EmpireTech IPC-T54IR-ZE-S3) | $261.24 |
| Junction box (PFA130-E) | $20.99 |
| Jetson Orin Nano Super (SparkFun, back-ordered) | $399.00 |
| 1 TB NVMe SSD (SanDisk) | $287.99 |
| PoE switch (POE4CH-110W) | $59.99 |
| Outdoor Cat6, 100 ft (Primus) | $69.29 |
| Surge protector (ETH-SP-G2) | $12.50 |
| Patch cable, 3 ft (trueCABLE) | $7.51 |
| **Total** | **$1,118.51** |
| UPS, optional (ST425) | +$64.95 |
| Jetson from Seeed instead (in stock) | +$51.30 |
| Hanwha XNO-6083R instead of the EmpireTech camera | +$778.75 |

Before tax, shipping, and hardware-store items.

## Probably already owned (check before buying)

For the Jetson's first setup only:

- a DisplayPort monitor, or a DisplayPort-to-HDMI adapter;
- a USB keyboard and mouse;
- a USB stick of 16 GB or more;
- a ladder.

## Sources (read 2026-10-17)

- Frigate on camera brands and RTSP: https://docs.frigate.video/frigate/hardware
  and https://docs.frigate.video/configuration/camera_specific
- Jetson price rise: CNX Software, 2026-07-22 (via the research notes).
- Every product: its own page, linked above.
