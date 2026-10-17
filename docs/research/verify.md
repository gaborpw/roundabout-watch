# To verify

Facts the project relies on that came from memory, a secondary source, or a
page that couldn't be read (CLAUDE.md 44). Each gets checked against a
primary source; then the source and date go in the "Checked" column and the
code comment is fixed. Nothing here may still be unverified when the system
runs live or anything is shared with anyone.

| Fact | Used in | Why it's unverified | Checked |
|---|---|---|---|
| DRAC conflict threshold 3.35 m/s² (Archer 2005) | `docs/architecture.md`, thresholds | Secondary sources only | |
| PET threshold: SSAM default 5.0 s vs tighter values in intersection research | thresholds | SSAM's default is confirmed (FHWA 10-038); the right value for a roundabout isn't | |
| NVIDIA's Jetson AI Lab index has PyTorch and ONNX Runtime wheels for JetPack 7.2.1 (Python 3.12) | ADR 0003 | Only the JetPack 6 index was listed | |
| Buying and using a Dahua-made camera in the US is lawful (FCC Covered List) | ADR 0005 | News and industry reports only; FCC page returned 403 | |
| The Jetson dev kit includes its power supply | `docs/parts.md` | General knowledge | |
| The surge protector must be grounded, and how | `docs/parts.md` | General knowledge | |
| PyAV's bundled libx264/libx265 are GPL, and what that means for a device image | ADR 0007 | General knowledge | |
| A 4 MP H.264 stream is about 45–65 GB a day | `docs/architecture.md`, retention | General-knowledge estimate; measure on the real camera | |
| ROCO dataset licence (CC BY-SA vs BY-NC-SA vs separate dataset terms) | build step 5 | The repo contradicts itself | |
| US patent 10,522,040 B2: scope and whether it matters for this use | `docs/architecture.md` | Google Patents status is "not a legal conclusion"; needs a patent attorney before any commercial use | |
| Ohio Revised Code 2933.52 text | ADR 0006 | Read through secondary sources only | |
| Which City of Cleveland office permits mounting on a city pole | `docs/next.md` | General knowledge | |
| RF-DETR Small/Medium speed on an Orin Nano Super | ADR 0004 | Only measured by Roboflow on an Orin NX | |
| OHGO API rate limits | `enrich.py` (later) | Not stated in what was read | |
| OpenCodeReview's tool loop works with Claude's thinking left on (`llm_extra_body` `{}`) | ADR 0009 | Not run yet; the first reviewed pull request shows it | |
| Tokens and cost per OpenCodeReview run, and whether 400,000 is a sensible ceiling | ADR 0009 | Not measured | |
| Anthropic Console steps for a workspace spend limit | `docs/next.md` | Third-party guide only; Anthropic's API docs say workspace limits via the API are early access | |
