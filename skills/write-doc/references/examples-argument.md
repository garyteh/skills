# Argument examples

Worked pairs calibrating voice and density for the argument genre. **Flexible.** They
calibrate how much to say, not a shape to copy field for field.

## 1. Rough notes become a spine

### What the author gave

> ok so the double redemption thing. dispatch checks eligibility then writes, and 2
> requests can both pass the check. finance flagged some cases last quarter, sounded like
> tens of thousands. we could either put the constraint in dispatch itself or buy the
> vendor thing. the approver wants a call this week. also the launch freeze is in a
> fortnight so if we miss that it waits a quarter

### What comes back

**Intent:** decide. You need someone to pick between 2 options, so this is a decision
document rather than the design document you called it.

**Primary reader:** the approver. You said they want a call this week, so the document
serves them, not the engineers who will build it.

**Trigger:** the launch freeze in a fortnight. Miss it and the fix waits a quarter.

**Bottom line (strawman):** put the constraint in dispatch now, because the vendor
option cannot land before the freeze. Correct me.

**Sections:**

1. The call, and what being wrong costs (L1)
2. What forced this now (L1)
3. The 2 options and the deciding difference (L2)
4. Who approves and who is informed (L2)
5. How the constraint works (L3)
6. Release, test and rollback (L3)
7. Appendix: the eligibility rules (L4)

Checkout moves money, so section 6 is an obligation rather than a choice.

Say it that plainly. Do not narrate how the derivation was done.

## 2. A gap round, strawman-first

Five gaps, one message, strawmen rather than questions.

> **(strawman) The number.** Finance flagged it, so a figure exists. I have written
> "about $40k across 14 cases last quarter". Correct the number: right now that sentence
> has no amount in it and it is the weakest line in the document.
>
> **(strawman) Migration size.** Two to 3 weeks of one backend engineer, online, no write
> downtime. Correct me, especially the downtime part.
>
> **(strawman) The race condition.** Two requests pass the eligibility check before either
> writes, so the window is between check and write rather than anywhere else.
>
> **(strawman) Rollback.** Flag off, the constraint stops being enforced, nothing to
> migrate back. So reverting is minutes and loses nothing.
>
> **(strawman) The freeze.** If the constraint breaks deliberate stacking, that is a
> blocker and it changes the recommendation. I have assumed it does not.

Each one names what it would change. None of them is an open question. Where an answer is
a genuine choice between named options, offer it as a choice so the author picks instead
of typing.

## 3. The same content at 3 altitudes

### Level 1, written for an approver

```
## What double redemption is costing us now

**Bottom line:** dispatch cannot enforce single-use, so we pay for it monthly.

- **Finance flagged 14 cases** last quarter, worth about $40k.
- **The bug is structural.** Eligibility is checked, then written, and 2 requests can
  pass the check before either writes.
- **The freeze is the deadline.** After it, the fix waits a quarter.
```

Short sentences, a number in every bullet, and a bold span carrying the point rather than
labelling a category.

### Level 3, written for the engineers

```
## How the constraint works

A unique index on the redemption pair moves enforcement from application logic into the
write itself. The check disappears, and the write either succeeds or violates.

- **Concurrent redemptions fail closed.** The second write violates the index and returns
  an error the caller already handles.
- **Stacking stays possible.** The index covers one pair, so a deliberate second offer on
  the same account is unaffected.
- **The migration is the risk.** Existing duplicates violate the index, so the backfill
  has to resolve them before it can be created.
```

### Level 4, in the appendix

Migration steps, the index definition and the backfill query go here. Not in the body,
even when every reader is technical, because they are reference rather than argument.

## 4. A job mismatch caught before prose

### What the author gave

> writing the design doc for self-serve rules in the portal. still not sure whether we
> extend dispatch or stand up a new service, but I want to get the design down while it is
> fresh

### What comes back

This is 2 documents, and the second one cannot be written yet.

**The fork blocks the spec.** A design document with an unresolved fork inside it will
stall in review while the reviewers relitigate the fork. Whatever you write about the
mechanism is provisional until it is settled.

**Split it.** A short decision document on extend-or-build, then the design document once
that lands.

**Want me to start the decision one?** It is smaller than the design document, and it
unblocks it.

Naming the split is worth more than any amount of drafting, and it is only available
before the prose exists.

## 5. Brief input stays brief

### What the author gave

> one pager for moving dedup into dispatch. 3 reasons: it is where the write happens, it
> removes the race, and it is 2 weeks not a quarter

### What comes back

Three reasons, reordered by weight, still 3 bullets. Not 3 paragraphs.

```
**Bottom line:** move dedup into dispatch. It removes the race in 2 weeks rather than a
quarter.

- **It removes the race.** Enforcement moves into the write, so there is no window.
- **It is 2 weeks, not a quarter.** (assumption) 2 weeks of one engineer, unconfirmed.
- **It belongs where the write happens.** Dispatch owns the write already.

**(gap) Success measure:** the propose intent needs a number here and your notes have
none. What would tell you this worked?

**(gap) What this displaces:** what does the engineer stop doing for 2 weeks?
```

The 3 reasons survive as 3 reasons. The 2 missing obligations are raised as gaps rather
than invented, and the unconfirmed estimate is marked rather than stated flat.
