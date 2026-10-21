# 5. The camera: a Reolink CX410 behind Peter's window

- **Status:** accepted (Peter's yes to the camera change, 2026-10-17)
- **Date:** 2026-10-17. Supersedes this ADR's first version, which chose an
  outdoor EmpireTech (Dahua) camera before the window and the budget were
  known.

## Context

Peter's asks: the camera should be easy to set up and certain to work with
the code, cost around $100, and look out through one of Peter's windows. The
window is on the second floor, 30–40 feet (about 9–12 m) from the
mini-roundabout at West 45th and Bridge Avenue (`docs/vision.md`).

What the code needs from the camera (ADR 0007): an **H.264** stream it can
read through go2rtc, normally **RTSP**. go2rtc can also read RTMP and
HTTP-FLV and pass them on as RTSP, so a camera whose RTSP is unreliable still
works. The camera's maker app and cloud are never used by the code.

What a window needs:

- **No infrared.** Infrared night vision reflects straight back off the glass
  and whites out the picture.
- **The lens pressed against the glass**, and the room darker than the
  street, so the glass doesn't mirror the room.
- **A large sensor**, because at night there is only street light to work
  with.

Reolink's own guide to cameras behind glass and How-To Geek's say the same
three things.

At 9–12 m no zoom is needed. A lens about 89° wide covers 17.6–23.6 m of
ground across, enough for the circle and its approaches. At 2560 pixels
across that is about 108–145 pixels a metre (my arithmetic).

## Decision

**Reolink CX410**, $84.99 at Reolink's US store. ("In stock" was recorded
here on 2026-10-17 and was wrong: the store showed Notify Me. On
2026-10-21 the in-stock match is the CX810; see `docs/parts.md` and
`docs/lessons.md`.)
Its specs, from Reolink's product page:

- **Picture:** 1/1.8" sensor, f=4 mm F1.0 lens, 89° across by 46° up and
  down; 2560×1440 at up to 30 fps (25 by default).
- **Video:** H.264 only. RTSP, RTMP and ONVIF.
- **No infrared at all.** Night colour comes from the large sensor and a
  warm spotlight, which stays **off** here: it would reflect off the glass
  too.
- **Power:** PoE (IEEE 802.3af), or 12 V DC with an adapter sold
  separately.

It connects by one cable through a PoE adapter straight to the desktop's
Ethernet port, so it has no route to anything else (CLAUDE.md 22, ADR 0011).

Settings to make once, in Reolink's app or desktop client (Reolink says RTSP
and ONVIF are turned on there):

- main stream H.264, 25–30 fps, keyframe interval 1 s;
- spotlight off, microphone off (CLAUDE.md 20);
- cloud and P2P off;
- a fixed IP address;
- a new password.

## Alternatives

- **Reolink E1 Outdoor**, $113.99. Its 3× zoom (90° to 50°) would be the pick
  from further away. Here it is worse: 20 fps and a small 1/2.7" sensor, and
  it's powered by a 12 V adapter, not over the network cable.
- **EmpireTech IPC-T54IR-ZE-S3 (Dahua)**, $261.24, this ADR's first choice
  for an outdoor mount. It is over budget, its infrared is wasted behind
  glass, and Dahua is on the FCC Covered List (FCC DA 21-309). The FCC's June
  2026 order (DA 26-635) bars importing and marketing their approved gear
  for public-safety, government and national-security uses, not home use.
  Reolink and TP-Link aren't named in any FCC notice we read.
- **Tapo C325WB** ($74.99). Its view is too wide, and Tapo says it is "not
  recommended to be used indoors".

## Consequences

- **Reolink's RTSP is the known weak point.** Frigate's docs say it "isn't
  always reliable" and recommend Reolink's HTTP streams; go2rtc lists Reolink
  RTMP as tested. If the RTSP stream drops frames, go2rtc reads RTMP or
  HTTP-FLV instead, and the code doesn't change.
- **Setup needs Reolink's app or client once.** Whether that needs a Reolink
  account isn't confirmed (`docs/research/verify.md`).
- **Night images will be grainy** with only street light. Detections at night
  will be worse than by day; measure it before trusting night events.
- **If the City rebuilds the circle in concrete** (2027), or the camera moves,
  the calibration has to be redone (CLAUDE.md: measurements are in metres,
  never pixels).
- **Trade-off:** the cheapest camera that fits, at the cost of Reolink's
  weaker RTSP and a fixed lens that wouldn't suit a window further away.

## Sources (read 2026-10-17)

- Reolink CX410 page and offer data (price, stock, specs; the 12 V adapter
  "purchased separately"): https://reolink.com/us/product/cx410/
- Reolink E1 Outdoor: https://reolink.com/us/product/e1-outdoor/
- Behind glass: https://reolink.com/blog/security-cameras-through-behind-window-glass/
  and https://www.howtogeek.com/407363/how-to-make-a-security-cameras-night-vision-work-through-a-window/
- Frigate on camera brands and Reolink RTSP: https://docs.frigate.video/frigate/hardware
  and https://docs.frigate.video/configuration/camera_specific
- go2rtc sources (RTMP, HTTP-FLV; Reolink notes): https://github.com/AlexxIT/go2rtc
- FCC: https://docs.fcc.gov/public/attachments/DA-21-309A1.pdf and
  https://docs.fcc.gov/public/attachments/DA-26-635A1.pdf
- Tapo C325WB specs: https://www.tapo.com/us/product/tapo-c325wb-security-camera/v1/1-pack/specs/
