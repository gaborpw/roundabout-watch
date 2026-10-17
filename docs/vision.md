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

## Peter's answers

2026-10-17, quoted as written:

> its the new roundabout on west 45th and bridge ave, cleveland ohio 44113.
> can we use that one gods view github repo for tracking maybe?

> 2. yes 3. camera mount is through my windowi can see ity rhough one of my
> windows. and is there a camera for around 100? 5. yes 6. personal interest

What they settle:

- **The roundabout:** the new mini-roundabout at West 45th Street and Bridge
  Avenue, Ohio City, 44113. It is one of the City's quick-build traffic
  circles (paint and flexible posts), installed in late August 2026
  (`docs/research/data-sources.md`).
- **The camera looks out through one of Peter's windows.** Nothing is
  mounted outside, and the camera sits indoors behind glass (ADR 0005 is
  being revised for it).
- **Budget:** a camera around $100.
- **What the results are for: personal interest.** Nothing is published or
  shared; the City's own evaluation of the circles is in 2027, and sharing
  anything with them later would be a new decision (CLAUDE.md 46).
- **God's Eye View is not a tracker** (`docs/research/references.md`).
- **ADRs 0003, 0004, 0006, 0007 and 0008: yes.**

## Not decided yet

Tracked in `docs/next.md`:

- **How far the window is from the circle**, and which floor, which decide
  the lens.
- **Which camera**, around $100.
