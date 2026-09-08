---
name: git-worktree
description: Isolates a task in its own git worktree, so one repository carries several checkouts at once without them treading on each other, and tears the worktree down once its branch is merged. Works with either main or master as the default branch. Use when a task is about to start and the repository may be worked on from more than one place, when you are asked to work in a worktree, spin up a separate checkout, work in parallel with another stream of work, or keep the primary checkout clean, and again when work done in an isolated checkout is finished and the worktree needs removing.
metadata:
  internal: true
---

# Git worktree

A worktree is a second checkout of one repository, on its own branch, in its own directory. Commits made inside it touch nothing else until they are pushed.

Requires a shell that runs `git` 2.5 or later, and a repository with a remote. Where the host offers its own worktree management, use that and skip the commands here; the outcome is the same and the rest of this page still applies.

`remote`, `default_branch`, `worktree_root` and `branch_prefix` come from `config.yaml`. Read them before running anything. The examples below write `origin` and `main` where those values go.

## Enter one before the first edit

Create a worktree at the start of a task, before touching a file, whenever any of these hold:

- Another stream of work may be running against the same repository.
- The primary checkout has work in progress that has to stay untouched.
- The task may be abandoned, and reverting a whole directory is cheaper than unpicking a checkout.

Skip it if you are already inside one. Inside a worktree these two paths differ; in the primary checkout they are the same:

    git rev-parse --git-dir
    git rev-parse --git-common-dir

## Find the default branch

Never assume `main` or `master`. Ask the remote:

    git remote set-head origin --auto
    git symbolic-ref --short refs/remotes/origin/HEAD

The first command creates the pointer where it is missing and repairs it where it is stale, so run it even when the second one already answers. It contacts the remote. Where that is not possible, read the existing pointer alone, and fall back to `git remote show origin` for the `HEAD branch` line.

Strip the remote prefix from the answer: `origin/main` names the branch `main`.

Use `default_branch` from config instead where it is set.

## Create it

    git fetch origin
    git worktree add ../my-task -b my-task origin/main

Three parts of that line matter:

- **Branch from the fetched remote ref, not the local branch.** The local copy of the default branch goes stale the moment another stream of work lands something, and a worktree cut from a stale base is a rebase you have to do later.
- **Put the directory beside the repository, not inside it.** A worktree nested in the repository shows up as untracked files, gets swept into builds, and lands in commits made from the primary checkout. `worktree_root` decides where it goes.
- **Name the branch for the task**, with `branch_prefix` in front where config sets one. The directory takes the same name, so one name identifies both.

## Work inside it

Run every command from that directory, including the commits.

Do not switch the worktree onto the default branch. Git refuses a branch that is checked out somewhere else, and the refusal names the other directory:

    fatal: 'main' is already used by worktree at '/path/to/repo'

That is the constraint the rest of this page is shaped around, not a fault to work past.

## Get the branch onto the default branch

Two endings, depending on whether the repository reviews changes.

**Where it does**, push the branch and open a pull request:

    git push -u origin my-task

**Where it does not**, push the branch straight at the default branch ref:

    git push origin HEAD:main

This succeeds only as a fast-forward, which is the safety property worth having: a rejection means the default branch moved while you were working. Rebase onto it and retry:

    git fetch origin
    git rebase origin/main
    git push origin HEAD:main

Never force-push the default branch. A rejection is information about the remote, and forcing discards whatever landed there.

Then verify with a separate read. The push output only echoes back what was asked for, so fetch and compare the two commits:

    git fetch origin
    git rev-parse HEAD origin/main

Two identical hashes mean it landed. Anything else means it did not, whatever the push printed.

## Tear it down

Nothing in a worktree is worth keeping once its branch is on the default branch.

Run the removal from the primary checkout, not from inside the worktree. Removing the directory you are standing in succeeds and leaves the shell pointing at a directory that has gone, so every command after it fails for an unrelated-looking reason.

    git worktree remove ../my-task
    git branch -d my-task

That order, not the reverse. Git refuses to delete a branch that a worktree has checked out:

    error: cannot delete branch 'my-task' used by worktree at '/path/to/my-task'

`git branch -d` refuses to drop a branch whose commits are nowhere else, which is the check worth keeping; `-D` skips it. Where the branch went up by pushing at the default branch ref, `-d` prints a warning that it is merged to the remote-tracking branch but not to `HEAD`, then deletes it. That warning is the expected outcome, not a failure.

`git worktree remove` refuses while the directory holds modified **or untracked** files, and build output counts. Read `git status` in the worktree and decide, rather than reaching for `--force`.

Where a worktree directory was deleted by hand, git still lists it as `prunable` until told:

    git worktree prune

## Bring the other checkouts into step

A push at the default branch ref leaves every other checkout, the primary one included, holding an older commit. Run this there before starting new work:

    git fetch origin
    git merge --ff-only origin/main

`--ff-only` so a checkout that has quietly diverged says so, instead of being papered over with a merge commit.
