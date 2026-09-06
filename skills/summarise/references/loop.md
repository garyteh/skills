<!-- Reference file for the `summarise` skill.
     Read in Full Brief (Reflexion) mode only: at Step 3's drawing work, and
     again at Step 6. Step and layer numbers refer to SKILL.md, which is always
     loaded when this file is. Thresholds come from config.yaml. -->

# Reflexion mode — the drawing runs and the critique loop

Two pieces of machinery, both Reflexion only. Fast mode reaches neither.

## Contents

- Running the drawing work separately (Step 3)
- Step 6 — the critique loop
- Where the host cannot isolate a reviewer

## Running the drawing work separately (Step 3)

Step 3 decides *whether* to run the drawing work separately: yes at 3 or more
structural sections, no below that. This is *how*.

Batch the whole set in one go off the settled structure plan, so they run
concurrently. The plan already names every section, so there is nothing left to
foresee. If a section turns out to need a diagram after all, run that one then.

Give each run:

- That section's content, and 1 line on what the section is for.
- Step 3's type-selection rules, and an instruction to read the mermaid syntax
  appendix before writing any mermaid.
- Any diagram type the reader named in their request.

Each returns exactly 1 diagram with its caption, or the verdict "linear, use a
numbered list" together with the list. It never returns 2 diagrams, never returns
brief prose, and never merges 2 structures into 1 picture.

Checking what comes back is yours, per Step 3. A returned diagram is a draft.

Where the host cannot run this work separately at all, draw the diagrams
yourself, exactly as Fast mode does, and say in the shipped brief that the
diagrams were drawn inline.

## Step 6 — the critique loop

You arrive here with a composed draft that already exits the Step 5 script
cleanly.

The loop rests on 3 defences, and they fix different problems.

- **Isolation.** The reviewer never sees your reasoning, so it grades the draft
  instead of rationalising your choices.
- **A different model.** A reviewer sharing the writer's model favours its own
  output. A different one is a real, if partial, correction.
- **The Step 5 script.** Mechanical gates sit beyond any model's opinion, which is
  why part of the verdict cannot be flattered.

### 6.1 Critique

Run a fresh reviewing pass, isolated from this one, on a **different model from
the one writing the brief**. Same-model reviewers favour their own output, so a
different model is a real, if partial, correction. Where the host cannot choose
the model, run the reviewer anyway and say in the shipped brief that it graded on
the same model.

Give the reviewer the draft, a short context card, and the rubric and config
paths from SKILL.md's reference table, telling it to read both and grade part B
only. The rubric names config keys rather than repeating their values, so a
reviewer without the config file cannot grade B11. Do not paste the rubric into
its prompt, and do not read the rubric yourself; you never need part B verbatim.
Withhold the source, your reasoning, the structure plan, and the reflection note.

The context card is 5 lines and no more:

- The reader's role and the areas they own, as resolved in Step 1, or "not
  established". B1 turns on whether the spine is this reader's stake, and the
  card is the reviewer's only route to that. Without the line it grades a
  blocking gate on nothing and still reports a verdict.
- The depth, and the spine in one sentence.
- Any diagram type the reader named in their request, or "none named".
- Which sections hold structural content, so the reviewer can tell whether each
  one got its own diagram. No mermaid.
- Revision rounds only: the part B gates that passed last round. Write "none yet"
  on the first round.

It returns:

- PASS or FAIL for every part B gate the rubric holds, in numeric order with
  nothing omitted. The rubric groups them by theme rather than by number, so
  numeric order is what makes a missing gate visible as a gap in the sequence.
- The count of failures.
- The full set of gates the rubric marks blocking, not only the blocking ones
  that failed. You never read the rubric yourself, so an intersection alone gives
  you nothing to check the answer against, and the ship condition in 6.3 turns on
  exactly this.
- For each FAIL, one specific instruction that would fix it. Not "tighten the
  prose". Something like "B5 fails, the third paragraph in layer 3 buries its
  point behind 2 clauses of setup, so lead the paragraph with the point".
- Evidence on any gate whose rubric wording asks it to name, quote or count
  something, on a PASS as much as on a FAIL. A bare PASS on a countable gate
  cannot be told apart from not having looked.

### 6.2 Reflect

After each critique, append 2 to 4 lines to a running reflection note. Append,
never overwrite, and carry the whole note into every later round.

A reflection names the habit, not the instance. "I keep putting the deciding delta
below the comparison instead of above it" is useful. "B3 failed" is not, because
the gate list already says that. Each line states what went wrong, why, and the
rule to apply next round. Record fixes that were tried and rejected, so the loop
never attempts the same repair twice.

### 6.3 Revise or ship

Ship when the script exits 0, every blocking part B gate passes, and the number
of failed part B gates is at or under `gates.max_gate_failures` in config.
Otherwise revise and go back to Step 5 in SKILL.md.

**Regression guard.** A revision that fixes one gate must not break another. Each
critique is told which gates passed last round. If a revision fails a gate that
previously passed, reject that revision outright, revert to the previous draft,
and fix the original failure a different way. A rejected revision does not consume
a round, but each distinct repair is attempted once only. Without this the loop
trades one failure for another and never converges.

**Cap the loop at `gates.max_revision_rounds`.** If the final round still fails,
ship the draft with the fewest failures and append one line, **flexible** in
wording but never omitted: `_Shipped with [n] gates failing: [gates]._` Never run
another round past the cap.

Carry everything forward into each revision: the previous draft, the structure
plan, the failed gates, the gates that passed, and the full reflection note. Never
restart from the source.

## Where the host cannot isolate a reviewer

Reflexion's whole value is a grader that cannot see your reasoning. Where the host
offers no way to run one, do not silently drop to Fast and call it Reflexion.

Instead, grade part B yourself against the rubric, in a pass that reads the draft
and nothing else: not your notes, not the structure plan, not the source. Then say
in the shipped brief, in 1 line, that the review was not isolated and which gates
you failed. A self-graded pass catches wording and layering failures. It cannot
catch the failures it already made once, which is exactly why the disclosure
matters.

Reading the rubric yourself is the 1 case where that is allowed, because there is
no reviewer to read it instead.
