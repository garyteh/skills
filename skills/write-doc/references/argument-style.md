# Argument document style

The mechanics for a decision or proposal document. Read at Step 5 when the genre is
argument. The rules that hold for both genres are in the skill body, not here.

## The bottom line

The document opens with one sentence naming the call, the recommendation or the outcome,
labelled exactly:

```
**Bottom line:** move the dedup constraint into dispatch before the freeze.
```

**Strict.** The gate script matches that label exactly, because a reader who stops after
one line has to leave knowing the answer. It goes first even though it is derived last.

Then the situation and the complication, in the order a reader needs them rather than the
order the author discovered them.

## Bullets carry the point in their first 2 to 4 words

Every top-level bullet opens with a bold span of `style.bullet_anchor_min_words` to
`style.bullet_anchor_max_words` words. That span is what a skimming reader's eye lands on,
so it carries the point rather than labelling a category.

- **Rollback is free** beats **Rollback:**
- **Finance flagged 14 cases** beats **Impact:**
- **The bug is structural** beats **Root cause:**

A category label makes the reader read the rest of the bullet to find out whether they
care. That is the tax this rule removes.

## Bold is a budget, not a decoration

Only what a skimmer must not miss. `gates.bold_span_budget` in config is the ceiling
outside bullet anchors and structural labels. Bold everything and you have bolded nothing.

Bold is never a heading. Where a bolded line is doing a heading's job, make it a heading.

## Detail goes down or out

Level 4 content sits in an appendix or behind a link. Migration steps, index definitions,
the backfill query, full schemas, exact commands. Not in the body, even when every reader
is technical, because they are reference rather than argument.

The gate script checks this by looking for a fenced code block in a language other than
prose sitting before the appendix heading. A code fence in the body is the usual symptom.

## Alternatives are an obligation

A recommendation with no rejected option beside it reads as the only idea anyone had.
Reviewers then supply the alternatives themselves, in the meeting, badly. State what was
considered and why it lost, in one line each. This is the opposite of the task genre's one
route rule, and the difference is deliberate: an argument document is asking the reader to
agree, and agreement needs the road not taken.

## The close

End with what, so what, now what. The facts, the implication, and the next action with a
named owner and a date. A document that stops at analysis makes the reader do the last and
hardest step alone.

```
## What happens before the freeze

- **The constraint ships first.** Dispatch owns it, done by the end of next week.
- **The backfill runs after.** Platform owns it, and it is reversible.
- **UNASSIGNED:** someone has to confirm the vendor contract allows the retry change.
```

An owner nobody has been named for is written `UNASSIGNED`, not omitted.

## Headings

One level 1 heading, naming the artefact and the subject. No skipped levels. Every heading
named for its content, per the naming table in the obligations reference.

The level 1 heading is the one place a document type acronym is a label rather than
jargon, so `DACI - Checkout dedup` needs no expansion.

## Sentence and paragraph shape

- One idea per sentence.
- No sentence over `style.sentence_hard_max` words, average at or under
  `style.sentence_avg_max`.
- A paragraph makes one point. Where it makes two, it is two paragraphs or a list.
- Tables for anything the reader compares. Scanning a table beats reading 4 paragraphs
  that each describe one option.

## What a strong argument section looks like

```
## What double redemption is costing us now

**Bottom line:** the ledger cannot enforce single-use, so we are paying for it monthly.

- **Finance flagged 14 cases** last quarter, worth about $40k.
- **The bug is structural.** Dispatch checks eligibility, then writes, and 2 requests can
  pass the check before either writes.
- **The freeze is the deadline.** After it, the fix waits a quarter.
```

Short sentences, a number in every bullet, and a bold span that carries the point rather
than naming a category.
