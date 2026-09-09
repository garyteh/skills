# Review

The rubric, the finding format, and the cold-reader simulation. Read at Step 6's
cold-reader pass, and throughout Review mode.

## Contents

1. How to score
2. The shared dimensions
3. The argument dimensions
4. The task dimensions
5. Severity
6. The finding format
7. Dispositions
8. The cold-reader simulation

## 1. How to score

Every dimension scores **Pass**, **Needs work** or **Blocker**.

**Run the test, do not form an impression.** Each dimension below names an action you
perform on the document. An impression is how a reviewer who already knows the answer
passes a broken document.

**Never produce a numeric score.** A score out of 100 implies a precision that does not
exist and gives authors a number to argue with instead of a defect to fix.

Score the whole document: any Blocker means Blocked. One or more Needs work with no
Blocker means Needs work. Everything passing means ready. Do not average. One Blocker
means one reader fails.

Only score the dimensions for the document's genre. A rubric that reports a column of
not-applicable rows teaches the reviewer to skip it.

## 2. The shared dimensions

Both genres.

**Goal.** Read only the title and the first paragraph, then write the document's outcome
in your own words. Blocker: no stated outcome, or the outcome is a system behaviour rather
than something a reader gets or decides. Needs work: buried below the fold.

**Findability.** Read only the headings, in order. Can you reconstruct what the document
covers? Blocker: no headings, or headings that name the document's furniture rather than
its content. Needs work: hierarchy skips a level.

**Cognitive load.** Blocker-class, per the skill's first belief. Mark every sentence that
informs understanding rather than action or decision. Then count what the primary reader
must read against what they may skip. Blocker: the reader has to get through theory or
architecture to reach the first thing they act on; or the document carries more than one
goal; or a section exists that this reader has no use for.

**Brevity.** Count the sentences that are not an action, a prerequisite, a verification, a
recovery, or a load-bearing part of the argument. Check every step against
`style.max_words_per_step` and the opening against `style.max_intro_sentences`.

**Never score a document down for length caused by anything in `style.never_cut`.** A page
that is short because it dropped its prerequisites, its verification lines or its inline
recovery fails those dimensions instead. Brevity here is the ratio of content the reader
acts on to content they have to get through first, not a word count. A document can grow
and still pass.

**Accessibility.** Read it as plain text with no colour, images or layout, then read the
link text out of context. Blocker: a step or a claim depends on colour, position or shape,
or a fact appears only in an image. Needs work: vague link text, bold standing in for a
heading, merged table cells, missing alt text.

**Maintenance.** Look for a named owner and a last-reviewed date, and for version-specific
content that is not labelled as such. Needs work: neither an owner nor a review date.
Incorrect documentation is worse than missing documentation.

## 3. The argument dimensions

Argument genre only.

**Obligations filled.** Take the obligation list for this intent and check each one off
against the document. Blocker: an obligation is neither filled nor marked as a gap.

**Intent and type match.** Does the document do the job its type claims? Blocker: a
specify document with an unresolved fork in it, a decide document with nothing left to
decide, or one document doing 2 jobs.

**Altitude discipline.** Check each section against the level it claims. Blocker: level 4
detail in the body. Needs work: a section spanning 2 levels, or a level 1 section over
`structure.level_1_max_words`.

**Alternatives present.** Blocker: a recommendation with no rejected option and no reason
it was rejected.

**Provenance marked.** Blocker: an unresolved strawman marker, or a claim the author never
made and nothing marks as inferred, retrieved or assumed.

## 4. The task dimensions

Task genre only.

**Audience fit.** List every noun phrase on the page that this reader would not already
hold and that the page does not define. That list is the document's real difficulty.
Blocker: an undefined term inside a step the reader has to perform. Needs work: undefined
terms in the surrounding prose only.

**Prerequisites.** Walk the steps and note every access, permission, credential, file,
value, tool or piece of information the document assumes. Compare against what it states.
Blocker: a requirement discovered mid-procedure, or never stated. Access and permissions
are the usual offenders. Needs work: stated but vague.

**Actionability.** Could you perform each step right now with no interpretation?
"Configure the settings accordingly" fails. "Select **Audience**, then **Everyone**"
passes. Blocker: a category of action rather than an action, or a judgement the reader
cannot make.

**Orientation.** Pick any step at random, in isolation. Can you tell which screen, panel
or dialog you are looking at? Blocker: an element named with no location, or a branch the
reader cannot resolve.

**Verification.** Find every consequential action and check each is followed by an
observable result. Blocker: the final outcome has no verification.

**Recovery.** Find the steps where a reader could plausibly get it wrong. Blocker: an
irreversible or expensive step with no warning. Needs work: recovery in an appendix, far
from the step.

**Self-containment.** Follow every link. Blocker: a linked page holds a value, a step or a
requirement needed to finish. Also check for pronouns whose referent is more than one
sentence back, and sections that only make sense read from the top.

This dimension **inverts in the argument genre**, where pushing reference detail out to an
appendix or a link is correct. Do not score an argument document against it.

## 5. Severity

- **Blocker.** A reader following this document cannot complete the task, or completes it
  wrongly. Or, in an argument document, cannot reach the decision the document exists to
  produce. Missing permission, undefined term inside a step, invented detail, an
  unresolvable branch, a missing obligation.
- **High.** The reader can finish but will hesitate, backtrack, or ask for help.
- **Medium.** Correctness of style that affects comprehension. Passive voice in a step, a
  buried location, a missing verification line.
- **Low.** Consistency and formatting.
- **Suggestion.** A preference. Where you cannot name the rule a finding breaks, it is
  this, and the author is free to ignore it.

## 6. The finding format

**Flexible.** Nothing downstream parses this, so adapt it where a document needs it. Keep
the order, because an author skimming a long report reads the top of it: the single worst
problem, then the rubric, then the findings.

```
Overall: <Ready | Needs work | Blocked>
<One sentence naming the single thing most likely to make a reader fail.>

Rubric
<Every dimension for this genre, one line each, failing ones first.>

Findings
[BLOCKER] <where> - <what breaks> - <why the reader fails>
  Now:      <quoted original>
  Instead:  <concrete replacement>
```

Discipline that keeps a review usable:

- Support every finding with the rule it breaks. If you cannot name the rule, mark it a
  suggestion.
- One finding per issue. Where the same issue recurs, report it once as `[GLOBAL]` with a
  count and 2 examples.
- Respect `rounds.max_findings_per_pass`. Past that, report the worst and say how many you
  held back.
- Say what works. An author who only ever receives criticism stops asking.
- Never flag the same text under 2 dimensions. Pick the more severe.
- Never resolve a finding by guessing. Half of them exist precisely because the
  information is missing, and the author is the only source.

## 7. Dispositions

Every finding gets one before the handoff, so an answered finding cannot silently
disappear. Group the questions by the section they sit in, so consecutive questions share
a context. Give knowledge questions a free-text answer and decisions a set of options,
and let every decision carry a leave-it option.

| Disposition | Means |
|---|---|
| Fixed | You changed something |
| Answered | The author supplied the missing knowledge, now written in |
| Accepted | The author chose to leave it, reason recorded |
| Deferred | Stays open, marked in the draft, author agreed to ship with it |

Nothing closes on your say-so. Answered means they told you, not that you worked out a
plausible answer. Cap repeat cycles at `rounds.max_fix_rounds`; past that, say which
findings still stand and stop asking.

## 8. The cold-reader simulation

The usability test, not the edit. Adopt total ignorance: you know nothing about this
subject beyond what the document says, and your own sense of how such things usually work
is exactly the bias being tested. If the document does not say it, you do not know it.

Walk the document in order. At every step or section, answer out loud:

1. **Where am I?** Do I know which screen, system or context this refers to?
2. **What do I do?** Is this something I could perform or conclude, or a category I would
   have to interpret?
3. **What do I need?** Am I assumed to hold access, a file, a value, a permission or a
   piece of context nobody told me to get?
4. **Do I know these words?** Name every term this reader would not hold, even where it
   feels obvious.
5. **Did it work?** Can I tell, from the document, whether I did it right?

Report every stall as a numbered list against the step it happened on, then list the full
set of assumed knowledge you collected, then give a verdict: "4 stalls, a reader matching
the stated audience cannot complete this task."

Two failure classes to hunt specifically, because authors almost never see them in their
own work:

- **Undeterminable branches.** "If you are on the new billing screen, select **Rules**."
  How does the reader know which screen they are on?
- **Unstated prior state.** A step that only works because an earlier action left the
  system, or the screen, in a state nobody wrote down.

**Do not fix anything in this pass.** Report only. Fixing while walking contaminates the
test, because you stop reading as a reader the moment you start writing as an editor.
