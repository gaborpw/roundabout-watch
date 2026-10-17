# 5. The camera: standard RTSP and ONVIF, chosen for the code

- **Status:** proposed (waiting on Peter's choice, `docs/next.md`)
- **Date:** 2026-10-17

## Context

Peter's ask: the camera should be the easiest to set up and certain to
work with the code. The code reads the camera only through **RTSP** (the
video stream), with **H.264** video, through go2rtc (ADR 0007). It never
uses a maker's app, cloud or software. So any camera that serves RTSP
reliably, in H.264, without a cloud account, is compatible. The rest of the
choice is about reliability and picture quality at a roundabout, day and
night.

What the code needs from the camera:

- RTSP main stream in H.264, 25–30 fps, 4 MP or so.
- A settable keyframe interval (1 s), so clips can start close to the event.
- ONVIF, so go2rtc and other tools can find and configure it.
- PoE, so one cable carries power and data.
- A motorised zoom lens, to frame the roundabout from wherever it can be
  mounted.
- A large sensor for night (Frigate's docs: "Larger sensors are better than
  higher resolutions; especially at night").
- Works fully offline (CLAUDE.md 22).

Frigate's docs rank brands for reliable RTSP: "I recommend Dahua, Hikvision,
and Amcrest in that order", and they warn that Reolink's RTSP "isn't always
reliable on all hardware versions".

## Decision (proposed)

**EmpireTech IPC-T54IR-ZE-S3**, a Dahua camera: 4 MP, 1/1.8" sensor,
2.7–12 mm motorised zoom (115° to 47° across), H.264/H.265, RTSP, ONVIF
Profile S/G/T, PoE 802.3af, IP67, $261.24 (`docs/parts.md`).

The code is written so the camera can be swapped: its only link to the
camera is the RTSP address in `.env`. Any of the alternatives below works
with no code change.

## The FCC question

Dahua (and so Amcrest, which sells Dahua-made cameras) is on the FCC's
Covered List. Since 2022 the FCC has refused new equipment authorisations
for these makers. Buying and using a camera already sold in the US doesn't
appear to be banned, but the FCC has asked for comment on restricting
previously authorised equipment. This was read in news and industry
reports, not in FCC guidance; the FCC's own page refused the automated read
(403). **Peter decides**, knowing that:

- Our design already treats the camera as untrusted: it never reaches the
  internet (CLAUDE.md 22), which removes most of the security concern
  behind the listing.
- The alternative that avoids the question is **Hanwha Vision XNO-6083R**
  (Korean): 2 MP, 2.8–12 mm motorised zoom, RTSP, ONVIF, H.264, $1,039.99 and
  back-ordered. **Trade-off:** about four times the price for a lower
  resolution, in exchange for a maker that isn't on the list.

## Consequences

- At its narrowest (47°) the lens frames a roundabout from about 30–60 m
  away. Further away needs an 8–32 mm model, and EmpireTech's infrared
  version of that was sold out. Measure the distance before ordering.
- The camera's own "smart" features (its AI, its app, P2P) are switched off;
  the Jetson does the analysis.
- The RTSP address for Dahua and Amcrest is
  `rtsp://USER:PASSWORD@CAMERA-IP/cam/realmonitor?channel=1&subtype=0`, and
  it goes only in `.env` (CLAUDE.md 15, 16).

## Sources (read 2026-10-17)

- Frigate hardware recommendations: https://docs.frigate.video/frigate/hardware
- Frigate camera-specific notes (Reolink, Dahua URL):
  https://docs.frigate.video/configuration/camera_specific
- Camera page and specs: https://empiretech01.com/products/empiretech-ipc-t54ir-ze-s3-1-1-8-cmos-4mp-ir-starlight-vari-focal-turret-security-camera
- Hanwha XNO-6083R page and specs: https://ipsecuritydepot.com/hanwha-xno-6083r-2mp-outdoor-ai-ir-bullet-network-ip-camera/xno-6083r
- FCC Covered List: https://www.fcc.gov/supplychain/coveredlist (returned 403);
  reports: https://www.campussafetymagazine.com/news/fcc-bans-new-equipment-sales-of-hikvision-dahua-hytera/
  and https://www.securityinfowatch.com/video-surveillance/article/21227289/fcc-moves-one-step-closer-to-banning-hikvision-dahua-products
  (via search result)
