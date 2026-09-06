<!-- Reference file for the `summarise` skill.
     Read once a full brief's intent is settled, before planning the sections.
     Step and layer numbers refer to SKILL.md. -->

# What each intent adds, and the ledger they all share

Read the list for the intent the reader picked, or for both where they picked 2.
Every intent runs layers 1 to 4 as normal and adds its own material to layers 3
and 4, plus the layer 5 ledger below.

Intent selects sections. It never relaxes the waste test: a sentence that would
not change what the reader does next is still cut, whichever intent is running.

## Approve a technical direction

- The specs, verbatim, narrowed to what is new or changed.
- The mechanism at service altitude, as a diagram per Step 3.
- Failure modes the doc does or does not handle: idempotency and retry safety,
  partial and silent failure, recovery after a crash or timeout, and the bounds
  on anything a caller or config can set.
- Every alternative the doc rejected, and the reason it gives.
- Where the doc knowingly defers a design decision, which is different from
  leaving one open by accident.

## Work out what lands on my team

- The ask, per team, quoted from the source rather than paraphrased.
- Every effort estimate and date, and what each is contingent on. An estimate
  sitting behind an unbuilt dependency has no date.
- Work whose owner is unnamed, marked TBC, or split across 2 projects.
- What the reader's team absorbs by default if nobody else resources it.
- What to get committed, and from whom, before signing anything.

## Pressure-test a direction or strategy

- The thesis in 1 sentence, and the bet it is making.
- The assumptions it rests on, and which of those the doc never supports.
- Second-order effects the doc raises and does not follow through.
- What the reader would challenge, ranked by how much it would change the call.
- No specs section, unless the doc turns technical and the reader needs it to
  judge the direction.

## Check a product spec is buildable

- What is actually being asked for, restated as requirements.
- The engineering implications the doc glosses over or assumes away.
- Hidden complexity, and which team it lands on.
- What has to be answered before anyone can estimate it.

## Layer 5 — the ledger

Layers 1 to 4 tell the reader what is true. Layer 5 tells them what to do about
it, in a shape they can act on without retyping anything. Two parts, in this
order, both after every other section.

### The coverage table

The shape the coverage obligation in SKILL.md asks for:

```
| Section of the source | What it carries for you |
```

Every section of the source appears exactly once, including the ones where the
honest answer is "nothing to flag". Where a section is a checklist or a table
with blank rows, give the count of blanks rather than a sample of them.

### The challenge ledger

One row per item the reader could act on, ranked with the highest-consequence
first:

```
| The item | Where it sits | State | Link |
```

- **The item** is the challenge or gap, in 1 line, phrased so it can be pasted
  into the source as a comment.
- **Where it sits** is the section, table row or diagram it attaches to.
- **State** is one of: raised and unanswered, raised and the author disagrees,
  resolved but it changed a decision, or yours and unraised.
- **Link** is the direct comment link the source returned, or the section the
  comment sits on where it returned none. Leave it empty only for a row that is
  the reader's own unraised gap, since there is no comment to point at yet.

Then close with the reader's position in 2 or 3 plain bullets: what would have to
be true for them to sign off, and which ledger rows are currently in the way.
Where the intent is not an approval, say what they are asking for instead.

### Rules for both tables

**Use tables, and keep bold out of them.** Both are tables for a reason: the
Step 5 script exempts table rows from the style and restatement gates, so a table
carries repeated section names and colon-heavy rows that the same content in
prose could not. Bold inside a table still counts against the bold budget, so the
ledger uses plain text and its State column instead of emphasis.

**Name these sections for the source, not for the shape.** The script's banned
heading list rejects "Open questions", "Next steps", "Risks", "Details",
"Trade-offs" and similar, and those are exactly the names a ledger attracts.
"What 7 reviewers are still waiting on" passes and tells the reader something.

**Quick orient has no layer 5.** It never gets an intent, and a ledger is not a
2-minute read.
