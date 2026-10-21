# To verify

Facts the project relies on that came from memory, a secondary source, or a
page that couldn't be read (CLAUDE.md 44). Each gets checked against a
primary source; then the source and date go in the "Checked" column and the
code comment is fixed. Nothing here may still be unverified when the system
runs live or anything is shared with anyone.

| Fact | Used in | Why it's unverified | Checked |
|---|---|---|---|
| The UniFi PoE Adapter (15W) is 802.3af and powers the CX410 | `docs/parts.md` | Ubiquiti's page doesn't name the standard; resellers do | |
| Reolink's app or client setup needs no Reolink account | ADR 0005 | Reolink says RTSP and ONVIF are turned on "in the Reolink App or Client"; account need not stated | |
| The CX410's RTSP stream holds up through go2rtc, or RTMP/HTTP-FLV is needed | ADR 0005, 0007 | Frigate and go2rtc warn Reolink RTSP varies by model | |
| Detection quality at night behind glass with street light only | ADR 0005 | Not measured | |
| DRAC conflict threshold 3.35 m/s² (Archer 2005) | `docs/architecture.md`, thresholds | Secondary sources only | |
| PET threshold: SSAM default 5.0 s vs tighter values in intersection research | thresholds | SSAM's default is confirmed (FHWA 10-038); the right value for a roundabout isn't | |
| Buying and using a Dahua-made camera in the US is lawful (FCC Covered List) | ADR 0005 | News and industry reports only; FCC page returned 403 | 2026-10-17, FCC DA 21-309 and DA 26-635: limits are for public-safety, government and national-security uses, not home use. Moot now: the camera is a Reolink (ADR 0005). |
| PyAV's bundled libx264/libx265 are GPL, and what that means if the program is given to anyone | ADR 0007 | General knowledge | |
| A 4 MP H.264 stream is about 45–65 GB a day | `docs/architecture.md`, retention | General-knowledge estimate; measure on the real camera | |
| ROCO dataset licence (CC BY-SA vs BY-NC-SA vs separate dataset terms) | build step 5 | The repo contradicts itself | |
| US patent 10,522,040 B2: scope and whether it matters for this use | `docs/architecture.md` | Google Patents status is "not a legal conclusion"; needs a patent attorney before any commercial use | |
| Ohio Revised Code 2933.52 text | ADR 0006 | Read through secondary sources only | |
| Which City of Cleveland office permits mounting on a city pole | `docs/next.md` | General knowledge | |
| OHGO API rate limits | `enrich.py` (later) | Not stated in what was read | |
| OpenCodeReview's `ocr delegate` commands run cleanly in CI under claude-code-action | ADR 0010 | Its docs describe a local agent; not run yet | |
| How much of the Claude subscription's quota a review uses | ADR 0010 | Not measured | |
| Anthropic Console steps for a workspace spend limit | `docs/next.md` | Third-party guide only; Anthropic's API docs say workspace limits via the API are early access | |
| A camera cabled straight to the desktop, with no gateway on either end and Internet Connection Sharing off, can't reach the internet | ADR 0011 | General knowledge of Windows routing; check at setup that the camera reaches nothing outside | |
| How to give the CX410 its first address and password without plugging it into the home router | ADR 0005, 0011 | Not read yet; the router route would put it online before cloud and P2P are off | |
| The desktop draws 100–200 W on average with the detector running (about $15–30 a month) | ADR 0011 | Estimate; measure with a plug-in meter or the GPU's own reading | |
| The M4 MacBook Air has no fan, so it slows under hours of load | ADR 0011 | General knowledge | |
| Cat5e and Cat6 both carry 802.3af PoE to the camera | `docs/parts.md` | General knowledge | |
| The CX810 has the CX410's 1/1.8" sensor and F1.0 lens, and no infrared | `docs/parts.md` | Reolink's CX810 spec page only (2026-10-21); a second source, or the camera itself, confirms it | |
