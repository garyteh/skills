# How-to examples

Worked pairs calibrating voice, severity and the refusal to invent. **Flexible.** They
show the judgement, not markup to copy.

## Contents

1. Rewrites
2. Cutting a page down
3. A worked review
4. A worked cold-reader walk
5. Refusing to invent

## 1. Rewrites

### Machinery becomes outcome

> **Now:** This document describes the rule entity lifecycle and its interaction with the
> dispatch service.
>
> **Instead:** Set up a checkout rule and make it live for customers. It takes about 10
> minutes.

Accurate and useless becomes short and usable.

### A category of action becomes an action

> **Now:** Configure the rule parameters accordingly and publish.
>
> **Instead:**
> 1. In the **Rules** list, select **New rule**.
> 2. Enter a name in the **Rule name** field.
> 3. Select **Publish**. The rule appears in the **Live** tab.

"Accordingly" is where a document quietly gives up. Note that this rewrite is only
possible because someone supplied the field names. Without them, the honest output is a
marked gap, not a plausible guess.

### Location before action

> **Now:** Select the **Save** button after entering your details in the form on the
> right.
>
> **Instead:** In the **Rule details** panel, select **Save**.

Three fixes: the location moved to the front, the directional language went, and the
element type came off the label.

### Minimising words

> **Now:** Simply select **Publish** and you're done. It's that easy.
>
> **Instead:** Select **Publish**. The rule appears in the **Live** tab within a minute.

The reassurance became a verification line, which is what the reader actually needed.

### An unresolvable branch

> **Now:** If you're on the new billing screen, select **Rules**.
>
> **Instead:** Look at the top of the page. If you see a **Billing** heading, select
> **Rules**. If you see a **Payments** heading instead, select **Rate plans**.

One of the most common dead stops, and authors almost never see it, because they always
know which screen they are on.

### Link text

> **Now:** For permissions, click here.
>
> **Instead:** For more information about permissions, see **Request edit access to a
> space**.

### A verification line earns its sentence

> **Now:** Publish the rule.
>
> **Instead:** Select **Publish**. The rule appears in the **Live** tab within a minute.
> If it stays in **Draft**, the rule has no audience set.

The failure hint costs one sentence and prevents most of the questions this step
generates.

### A prerequisite discovered too late

> **Now:** (a note beside step 4) You will need edit access for this step.
>
> **Instead:** (in **Before you start**) Edit access to the portal. If you cannot
> see the **New rule** button, you do not have it.

Two problems fixed: it moved to the top, and it came out of a box the reader would skip.

## 2. Cutting a page down

The before page ran 156 words: an opening paragraph on how the dispatch service stores
rules, a "Getting started" heading, and "simply fill in the relevant fields and save your
changes".

The after page runs 112 words. What went: the whole architecture paragraph, the
throat-clearing opener, the hedges, the empty heading, and the vague step.

What arrived: 5 numbered steps with real field names, 2 checkable prerequisites above step
1, a verification line after publish, and one recovery line beside the step that fails.

**The lesson, and it is the one this genre gets wrong most often.** The page dropped from
156 words to 112, which is a 28% cut and not a dramatic one. But every word of prose went
and 5 steps, 2 prerequisites and a recovery line arrived. Brevity here is not a word
count. It is the ratio of content the reader acts on to content they have to get through
first. A page can get **longer** and still pass, as long as what grew was steps,
prerequisites, verification or recovery.

## 3. A worked review

Input: a 4-sentence draft telling the reader to "configure the rule and publish it".

```
Overall: Blocked
A reader cannot complete this task: step 2 is a category of action, not an action, and
nothing on the page names the fields it refers to.

Rubric
Actionability    Blocker      "Configure the rule" cannot be performed
Prerequisites    Blocker      Edit access is assumed and never stated
Verification     Blocker      Nothing says what a successful publish looks like
Orientation      Needs work   Step 1 names no screen
Audience fit     Needs work   "dispatch" undefined in prose
Goal             Pass         First sentence names a reader outcome
Findability      Pass         Headings are task-shaped
Brevity          Pass         No padding, though it is short for the wrong reason
Accessibility    Pass
Maintenance      Needs work   No owner, no review date

Findings
[BLOCKER] Step 2 - "configure the rule" is a category, not an action - the reader has no
way to know which fields exist or which are required.
  Now:      Configure the rule and publish it.
  Instead:  I need 4 things from you before I can write this: which screen this happens
            on, which fields are required, what values are valid, and what the reader
            sees after saving.

[BLOCKER] Before you start - missing - edit access is assumed by step 1 and never stated.
  Instead:  Edit access to the portal. If you cannot see the **New rule** button,
            you do not have it.

[HIGH] Step 3 - no verification - the reader cannot tell whether publishing worked.
```

It does not invent the field names, and it does not hand back a polished rewrite. It names
what it needs.

## 4. A worked cold-reader walk

Same input, different pass.

```
Step 1: "Open the rules page."
  I do not know where the rules page is, or which product I am in. STALL.

Step 2: "Configure the rule and publish it."
  I do not know what configuring means here, which fields exist, or which are
  required. STALL.

Step 3: "Check the rule is live."
  I do not know where to look, or what live looks like. STALL.

Assumed knowledge, none of it defined on the page:
  - what "dispatch" is
  - that rules have an audience, and that publishing without one fails
  - that edit access is a separate permission

Verdict: 3 stalls. A reader matching the stated audience cannot complete this task.
```

Nothing was fixed in this pass. Fixing while walking contaminates the test.

## 5. Refusing to invent

The most important behaviour here, and the easiest to get wrong under pressure to be
helpful.

The author's note says: "Then they set up the rule and publish it."

**The wrong response** writes 5 plausible steps: open a **Rules** menu, select **New**,
fill in name and audience, select **Save**, select **Publish**. Every one of those is
plausible and none of them is known. A reader follows them, cannot find **Rules**, and
stops trusting the page. Worse, the author skims it, recognises the shape, and approves
it.

**The right response:**

> **(gap) Step 4.** I cannot write this yet. To turn "set up the rule and publish it" into
> something a reader can follow I need:
>
> - which screen this happens on, and how the reader gets there
> - which fields exist, which are required, and what values are valid
> - what the reader selects to save, and to publish
> - what appears after a successful publish

Four questions is more useful than 5 invented steps.

**And the disguised version is the same failure.** "Complete the relevant fields and save
your changes" is an invented step wearing a disguise. It looks like prose and it is a hole.
Mark the gap instead.

## What may be strawmanned here

The refusal above covers observables. The decomposition is a different matter: how the task
splits into sub-tasks, what order the steps go in, which failure earns an inline recovery
line, and whether this is one page or three are all things the author settles by reading,
so propose them.

> **(strawman) Shape.** I have split this into 3 sub-tasks: create the rule, set its
> audience, publish it. Publishing is where people get it wrong, so that is where I have
> put the recovery line. Correct me.
