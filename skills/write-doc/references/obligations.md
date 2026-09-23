# Obligations

What each intent owes its reader, and how a section list comes out of that. Read at
Step 2, before naming any section.

## Contents

1. Why obligations rather than templates
2. The 6 intents and what each one owes
3. High-risk obligations
4. The altitude map
5. Naming sections
6. Worked derivations
7. When the intent is wrong

## 1. Why obligations rather than templates

**An obligation is a question, not a heading.** Several obligations can share one section,
and one obligation can need three. Naming comes later, in section 5.

**An unfillable obligation is a gap, not a cut.** Carry it into the gap ledger. Do not drop
the obligation because the material was not in the author's notes.

## 2. The 6 intents and what each one owes

### Decide

A DACI, an ADR, a decision memo, an options paper.

1. The call, in one sentence, at the top.
2. Who decides, who drives, who contributes, who is informed. One approver.
3. The options genuinely considered. At least 2.
4. The delta between options, not a full description of each. Usually cost, effort, risk,
   time or capacity.
5. Why the rejected options were rejected. A reader who cannot see this supplies their own
   alternatives, in the meeting.
6. The recommendation, with its author named.
7. What is reversible and what is not, plus the cost of being wrong.
8. When the decision is needed, and what happens if it slips.

### Propose

An RFC, a proposal, a pitch, a business case.

1. The problem, stated as a cost being paid today.
2. What forced this now.
3. The proposed direction, in one sentence.
4. Success, as a measure with a number.
5. Rough size, in effort, cost or elapsed time. A range is fine; silence is not.
6. What this displaces.
7. The alternatives, including doing nothing.
8. The main risk, and the response to it.

### Specify

A PRD, a design document, a technical specification.

1. Who the user is, and what they want.
2. Scope, plus an explicit out-of-scope list. The out-of-scope list prevents more rework
   than the scope list does.
3. Requirements, each one testable. A requirement nobody can verify is a wish.
4. The mechanism. Components, contracts, data flow.
5. Failure modes, and what happens in each.
6. Dependencies and prerequisites, stated before any step that needs them.
7. How the reader self-verifies that a piece works.
8. Open questions, ranked by how much each would change the design.

### Align ownership

An on-call model, an operating model, a team charter.

1. Activities, named concretely enough to be assignable.
2. Exactly one accountable person per activity. Two is the defect this document exists to
   remove.
3. Who is consulted before, and who is informed after.
4. The escalation path when the accountable person is unavailable.
5. What is deliberately nobody's job, and why.
6. A review date, because ownership decays faster than anything else in a document.

### Record

An ADR, a post-incident review, a decision log.

1. What was decided or happened, with a date.
2. The context at the time, written so it does not depend on today's knowledge.
3. What was rejected, and why it was rejected then.
4. The consequences, including the ones already visible.
5. What would trigger revisiting it.

### Enable a task

A how-to, a runbook for non-engineers, an onboarding walkthrough. This intent is the task
genre, and its obligations are shaped by one fact: the reader arrives from search, alone,
and does not follow links.

1. The outcome, in the first sentence, as something the reader gets rather than something
   the system does.
2. When someone needs this page.
3. Every prerequisite, stated before step 1, and specific enough to check. "Edit access to
   the portal, and if you cannot see the New rule button you do not have it" beats
   "appropriate permissions".
4. One route. Where several ways exist, document the one that works for the most readers
   and say nothing about the others.
5. The location that orients every step, before the action.
6. What the reader should see after anything consequential, so they can self-verify
   instead of asking for help.
7. Recovery beside the step that can fail, not in an appendix.
8. Who to ask when the page runs out.
9. An owner and a review date. Incorrect documentation is worse than missing
   documentation.
10. Self-containment. No step depends on a fact stated only on another page.

**Sections a task document never adds**, because each one exists to make the author feel
the page is complete and costs the reader their first 20 seconds: an introduction or
background section; an architecture or how-it-works section, which is a different genre
and a different page; alternatives or other ways to do this; a glossary at the bottom,
where the reader at step 4 will not scroll; and a troubleshooting appendix covering every
possible failure, which becomes a dumping ground nobody maintains.

## 3. High-risk obligations

Where the document touches any area listed in `high_risk_domains` in the skill's config,
3 obligations apply regardless of intent, including for a how-to:

1. **Release plan.** How this reaches production, in stages, each stage independently
   deployable.
2. **Test plan.** Edge cases, failure paths, and how correctness is proven before
   exposure.
3. **Rollback.** What undoes this, how long that takes, and what data damage is
   irreversible.

These are not optional and are not negotiable down.

## 4. The altitude map

Argument genre only. The task genre is single-altitude by construction: one page, one
goal, one reader.

| Level | Question it answers | Reader | Typical content |
|---|---|---|---|
| 1 | Should we care, and what is the call? | Approvers, cross-functional leads | Outcome, the call, constraints, success measure, cost of inaction |
| 2 | What is in and out, and who owns it? | Product managers, designers, team leads | Scope and out-of-scope, options compared, ownership, journeys, integrations |
| 3 | How does it work? | Engineers, architects, QA | Components, contracts, data flow, failure modes, sequencing |
| 4 | What exactly do I type? | Implementers, operators | Schemas, configs, code, commands, migration steps, test parameters |

Three rules:

- **Reading order is levels descending**, and every level stands alone. A level 2 section
  that only makes sense after reading level 3 is misfiled.
- **Level 4 never sits in the body.** An appendix or a link.
- **Match the entry point to the primary reader.** An approver opens at level 1, with 3
  and 4 as support. An engineering reader shrinks level 1 to a few lines and lets level 3
  carry the argument.

## 5. Naming sections

Name every section for what is in it, in this document.

| Generic | Named |
|---|---|
| Background | What the current checkout flow costs us |
| Risks | Why the sync call is the risk |
| Trade-offs | What the extra fortnight buys |
| Next steps | What happens before the freeze |
| Options | Buy the vendor or extend the Golden Ticket service |

Two constraints. The heading covers every bullet beneath it, and never widens into
vagueness to make a stray bullet fit. And it does not cover things that are not there: an
overwide heading promises content the section does not deliver, which reads as an
omission.

## 6. Worked derivations

### A checkout decision with a deadline

Intent decide, reader the approver, trigger a booked launch that locks in a fortnight.
Eight decide obligations, plus 3 high-risk ones because checkout moves money. Eleven
obligations land as 7 sections, and the mapping is many to one, which is normal.

1. The call, and the cost of being wrong (L1)
2. What forced this now (L1)
3. The 2 options and the deciding difference (L2)
4. Who approves, who is informed (L2)
5. How the recommended option works (L3)
6. Release, test and rollback (L3)
7. Appendix: the eligibility rules (L4)

### A design document for another team's engineers

Intent specify, reader an engineer who does not share the author's context. Level 1
shrinks to 3 lines, because nobody here is deciding whether to fund it. Level 3 carries
the document. The out-of-scope list matters more than usual, because the reader will
otherwise assume the parts they care about are included. Schemas go to an appendix even
though every reader is technical, because they are reference rather than argument.

### A proposal with no forcing event

Intent propose, and the trigger obligation has no honest answer. Say so: "nothing
external, this is a choice about where to spend the next quarter". Manufacturing urgency
here is the failure, not leaving the field empty.

## 7. When the intent is wrong

Three patterns, all catchable before any prose exists.

**A specify document that is really a decide document.** There is an unresolved fork
inside it. Split the fork out, resolve it, then specify. Left in, the design stalls in
review while reviewers relitigate the fork.

**A decide document with no decision left.** That is the record intent. Writing it as a
decision invites a reopened debate nobody wanted.

**A propose document doing 2 jobs.** The funding reader stops halfway; the building reader
starts halfway. Split into a proposal and a spec, and link them.

Two more patterns appear once both genres are in scope.

**An argument document that is really a how-to.** A "process design document" that is a
runbook. The tell is that every section describes what someone should do next Tuesday
rather than what anyone should conclude.

**A how-to that is really a decision.** A runbook carrying a branch the reader cannot
resolve is a decision nobody made, pushed onto the least-equipped person in the chain.
Resolve the branch, or document how the reader tells which side they are on.

Say which one you see, name the split, and let the author decide. This is the
highest-value observation available here, and only before the prose exists.
