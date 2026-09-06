<!-- Reference file for the `summarise` skill: the full gate rubric.
     A reviewer grading a draft should read part B only.
     Named thresholds live in config.yaml. -->

# Rubric

Every check is PASS or FAIL, never partial. Nothing here tests fidelity to the
source, because neither the script nor the reviewer can see it. The agent that
wrote the draft checks fidelity separately, against the source.

#### Part A — mechanical, decided by the script

Not scored. All 9 must be clean before the reviewer runs.

- **A1** The brief opens with a `## Summary: <title>` line, and the lead line
  runs 2 sentences or fewer with nothing above it but that title.
- **A2** No heading is drawn from the banned generic list ("Details",
  "Background", "Risks", "Notes", "Summary", "Overview", "Rollout" and similar).
  The script holds the full list.
- **A3** Bold appears no more than `gates.bold_span_budget` times, counting
  emphasis only. The mandated diagram label and the mandated `**Your move:**`
  label are structural and don't count against the budget.
- **A4** The reader's own variant of English where the run named one, numerals
  not spelled-out words, and no em dashes or colons inside a sentence. Bold
  lead-in labels, headings, bullet labels and the mandated diagram label are
  exempt. Where no variant was named, the script says so and checks the rest.
- **A5** Every mermaid block parses.
- **A6** No type listed under `diagrams.on_request_only` appears unless the reader
  named it.
- **A7** Every date in the brief that has already passed is marked as passed on the
  same line. Repeating a source's due date as if it is still ahead is a real
  failure mode, and it is invisible to a reader who trusts the brief.
- **A8** No 2 statements in the brief say the same thing. The script compares
  content-word overlap between every pair of bullets, sentences and captions, and
  reports any pair above `gates.restatement_threshold`. The usual hit is a caption
  repeating the bullet that sent the reader to the diagram.
- **A9** A single `**Your move:**` line exists, sits below the title and above
  every section heading so a layer 2 reader reaches it, and carries enough words
  to name a move. An explicit "none, informed only" passes.

#### Part B — judgement, decided by the reviewer

14 gates: B1 to B14, every one of them. They are grouped below by theme rather
than by number, so check your verdict against that list before returning it and
report them in numeric order.

Report each as PASS or FAIL and give the failure count. Where a gate's wording
asks you to name, quote or count something, do it on a PASS as much as on a FAIL.
A bare PASS on a countable gate cannot be told apart from not having looked.

Part B grades the brief's judgement and shape only. It says nothing about
coverage, verbatim specs or the ledger, so a clean part B verdict is not evidence
that any of those held.

The ship bar is `gates.max_gate_failures` in config, a maximum failure count
rather than a score, so it keeps its meaning when a gate is added. Gates marked ⛔
block however few the failures. Return the full set of blocking gates every round,
not only the blocking ones that failed.

**Lead and layering**

- **B1** ⛔ The lead line carries the spine, not merely a description of the
  source, and the spine is the reader's stake rather than the shape the document
  presents. A decision spine fails this where the reader is unnamed, holds no
  vote, or the call already closed. The clearest tell is a brief that
  contradicts itself, a spine asserting something lands on the reader above a
  bullet saying nothing does.
- **B12** ⛔ The lead states what forced this now, not only where things stand.
  Where the source names a forcing event, a deadline, an incident, a blocked
  launch, a limit hit, an approval closing, the lead carries it. Where the source
  names none, the brief says so rather than manufacturing urgency.
- **B14** The move line names a position the reader could take, not a chore they
  already knew about. "Argue for a USER principal type before the backfill runs"
  passes. "Review this doc" and "go and ask the team" fail, because neither tells
  them what to say when they get there. It also fails where the line names a
  meeting, forum or channel that appears nowhere in the brief, since the reader
  cannot act on a venue that may not exist. Quote the move line in your verdict,
  pass or fail.
- **B2** ⛔ Every heading names what is actually in that section of this source.
  Passing A2 is not enough; a heading can dodge the banned list and still tell the
  reader nothing.
- **B3** The layers run in order. Nothing that changes the reader's read sits below
  something that doesn't.
- **B4** Each layer stands alone. No point in an earlier layer needs a later layer
  to make sense.

**Readability and compression**

- **B5** Every paragraph carries 1 idea and lands in a single pass. Nothing makes
  the reader re-read to work out where the point was.
- **B6** No sentence can be deleted without losing something that changes the
  reader's read or decision. Fail this the moment a sentence exists to introduce,
  frame or round off another sentence rather than to carry a fact of its own.
- **B7** Nothing is said twice in different words. A8 catches near-identical
  wording, so this gate is for the paraphrase A8 misses: a bullet and a caption
  making the same point with different vocabulary, or a layer 3 paragraph
  re-explaining a layer 2 bullet at greater length. Name the pair when it fails.
- **B8** No claim is left vague where the brief itself shows it could be concrete.
  No "there are scaling considerations" sitting next to a number the brief already
  quotes elsewhere.
- **B13** Facts are stated, not attributed to the document holding them. "The doc
  lists 3 open questions" fails where "3 questions are open, and the expiry one
  blocks M2" was available. 3 uses are legitimate and never fail this gate:
  attributing a claim the brief is separating from its own read, reporting that 2
  artefacts disagree, and saying a source leaves something unanswered. Judge only
  the remainder. Give the count of sentences using the source as subject and quote
  the ones you judged illegitimate, on a PASS as much as on a FAIL, because this
  gate is cheap to wave through and expensive to get wrong.

**Nuance and honesty**

- **B9** ⛔ Trade-offs, consequences and assumptions are legible where the brief
  raises them, not flattened into a bare verdict the reader has to take on trust.
- **B10** ⛔ Fact, interpretation and recommendation are visibly separated. Every
  claim that is the brief's own read rather than the source's is marked
  "(inferred)". Where the brief recommends, it reads as a recommendation and
  states the assumption it rests on, rather than asserting a call as settled fact.

**Diagram fitness**

- **B11** Every section the context card labels structural has its own diagram or
  numbered list, and no diagram carries 2 structures at once. The type fits what
  the section is, C4 altitude sits within `diagrams.preferred_c4_levels` (Context
  only across system boundaries), any sequence diagram's lifelines are deployed
  services rather than code objects, and the diagram carries the structure while
  the prose beside it adds only what the diagram cannot carry. A numbered list in
  place of a diagram passes. A diagram whose boxes restate their own labels, or
  whose caption is the only part carrying weight, fails, because that is a
  diagram kept for having been drawn rather than for helping.
