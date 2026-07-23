# Document contract

Select sections based on the task. Do not include an empty section merely to satisfy a template.

## Required

1. **Title and purpose** — Name the subject and why the artifact exists.
2. **Status legend** — Define observed, reported, inferred, proposed, and unknown.
3. **Executive summary** — State the situation, impact, and current confidence.
4. **Primary journey** — Show at least one flow, state transition, or timeline.
5. **Evidence** — Attribute the sources supporting material claims.
6. **Open questions** — List unresolved items or explicitly state that none remain.
7. **Verification** — Give concrete checks for confirming the behavior.

## Bug

Add:

- expected versus actual behavior;
- reproduction context and affected states;
- impact and scope;
- confirmed cause or labeled root-cause candidates;
- proposed repair only when requested or supported.

## Feature

Add:

- current versus proposed journey;
- user and system outcomes;
- requirements and unknowns;
- alternative approaches when decision support is useful;
- rollout, risks, analytics, and accessibility when relevant.

## Incident

Add:

- timeline with time zone;
- detection, impact, mitigation, and current status;
- confirmed facts versus hypotheses;
- follow-up actions with owners only when known.

## Investigation

Add:

- question being investigated;
- evidence reviewed and methods used;
- findings with confidence;
- eliminated and remaining hypotheses;
- recommended next evidence or experiment.

## Section selection

- Prefer one strong primary journey to many repetitive flows.
- Add UI states only when the interface matters.
- Add technical architecture only when it explains the journey or failure.
- Add code excerpts sparingly and keep them subordinate to the explanation.
- Put dense supporting material in compact evidence cards or an appendix.
