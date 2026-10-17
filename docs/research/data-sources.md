# Outside data: Ohio and Cleveland

Free sources to put next to what the camera sees. Checked 2026-10-17.
**None of the crash data is live**: the camera is the only real-time source
of near-misses. These show a roundabout's crash history and let us check
whether a crash we flagged was also reported.

| Source | What it gives | Freshness | Access | Checked how |
|---|---|---|---|---|
| [OHGO API](https://publicapi.ohgo.com/docs/resources) (ODOT) | Live incidents, dangerous slowdowns, travel delays, construction, state camera snapshots (every 5 s) | Live | Free key: [registration](https://publicapi.ohgo.com/docs/registration) (address from a wrapper's docs, not opened). Key in an `Authorization` header or `api-key` parameter. [Terms](https://publicapi.ohgo.com/docs/terms-of-use): "as is", can change. | via search result |
| [OSTATS](https://statepatrol.ohio.gov/ostats.aspx) (Ohio State Highway Patrol) | Every police-reported crash in Ohio (OH-1 reports), filter, map, download views | Weekly; 5 years + current | Free, public | via the [OSTATS user guide](https://dam.assets.ohio.gov/image/upload/statepatrol.ohio.gov/links/OSTATS_PublicUserGuide.pdf), search result |
| [ODPS crash statistics](https://ohtrafficdata.dps.ohio.gov) | Bulk crash records by date range and county (Cuyahoga) or agency | 5 years + current | Free; link emailed within 24 h, opened with a PIN | via the [web guide](https://ohtrafficdata.dps.ohio.gov/Content/CrashStatsWebGuide.pdf), search result |
| [ODOT GCAT](https://gis.dot.state.oh.us/tims/CrashAnalytics/Login) | Crash map (Public Access button); full tool for agencies | — | Public map free; full accounts for public agencies and approved consultants | via search result |
| Cleveland Open Data, "Cleveland Traffic Crashes" ([catalog record](https://geo.btaa.org/catalog/44239d50c4f448dc9789ff4f7739e524_62.oai_dc_xml)) | City crash layer; Vision Zero high-crash segments | Last modified 2025-11-21 | Free; search on [data.clevelandohio.gov](https://data.clevelandohio.gov) | via search result; dataset page not opened |
| [TomTom Traffic](https://docs.tomtom.com/pricing) | Live flow and incidents | Live | Free tier: 2,500 incident details and 20,000 flow-segment requests a month, no card | provider page |
| [NHTSA FARS CrashAPI](https://crashviewer.nhtsa.dot.gov/CrashAPI) | Fatal crashes only | Yearly | Free | page returned 403; via search result |
| OpenStreetMap (Overpass) | The roundabout's exact shape (`junction=roundabout`) | — | Free, ODbL (licence from general knowledge) | OSM wiki |

Not available to us: Waze for Cities (councils and transport agencies only),
and Google Maps has no traffic or incident API.

## Recording law (Ohio)

- Video of a public road from private property: generally lawful in the US
  (general guides, not statute; not Ohio-specific).
- Audio: Ohio is a one-party consent state, Ohio Revised Code 2933.52
  ([RCFP Ohio guide](https://www.rcfp.org/reporters-recording-guide/ohio/),
  [DMLP Ohio recording law](https://www.dmlp.org/legal-guide/ohio/ohio-recording-law);
  secondary sources, statute text not read). We record no audio anyway
  (CLAUDE.md 20).
- Mounting on a city pole or signal needs the City of Cleveland's
  permission (general knowledge; which office is not confirmed).

This is research, not legal advice (CLAUDE.md 46). Before sharing footage
or results with anyone, check with a lawyer.
