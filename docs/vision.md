# What Peter wants this to be

In Peter's own words, from the conversation that started the project
(2026-10-17). Quoted as written. When a decision here is unclear, ask Peter
rather than reading between the lines, and add the answer below with its
date.

## The ask

> I want to setup a camera that looks at a round about and I want it to
> track crashes and almost near accidents. How can I set this up

> Yeah lookup free apis or ways to track the traffic and accidents, code
> that does it GitHub repos, look to see if someone already does this so we
> can use that as references

> I'm in Cleveland

> Also make sure whatever camera is easiest tos setup and use with our code
> is picked or make sure at least the 2 are compatible. I want a full list
> of parts needed, as well as a framework direction of how the code will
> be. I want this to be in its own repository, with all the basic rules and
> architecture that's needed and what I've used on my other projects in md
> steering files. Lookup what the best code would be for this as well.

## What that means for the work

- **Crashes and near-misses, at one roundabout, in Cleveland.** One camera,
  one place, done well, before anything bigger.
- **The camera and the code are chosen together.** The camera is picked
  for being easy to set up and certain to work with the code (standard
  RTSP and ONVIF, no cloud account), not for features the code won't use.
- **Build on what exists.** Use existing open-source pieces where they are
  good (detection, tracking, the safety maths) and cite them; write our own
  only for the glue and for what nobody has built (`docs/research/`).
- **Run it the way Playthroughd runs.** Same rules, same records, same
  review process (CLAUDE.md).

## Not decided yet

These are open questions for Peter, tracked in `docs/next.md`:

- **What the results are for.** Personal interest, evidence for the city
  (Cleveland's Vision Zero programme), or something to share publicly.
  This decides how much review, privacy work and documentation the results
  need.
- **Which roundabout, and where the camera mounts.** Peter's own building,
  someone else's with permission, or a city pole (which needs the city's
  permission).
- **Who sees the clips.** Peter only, or others.
