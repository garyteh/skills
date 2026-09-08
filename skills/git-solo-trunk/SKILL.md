---
name: git-solo-trunk
description: Gets a change onto a repository's default branch, main or master, with no pull request in between, whether the change is sitting uncommitted in the working tree or already on a local branch in this checkout or a separate one, and brings the repository's other checkouts back into step afterwards. Use when someone says to commit and push directly, put this on main or master, skip the PR, merge my branch into the default branch themselves, or asks how to ship a change in a repository they are the only contributor to. Not for repositories with review gates or protected branches, where a change belongs on a branch behind a pull request.
---

# Git solo trunk

One contributor, no review gate, so a finished change goes onto the default branch of the remote and nowhere else first.

Requires a shell that runs `git` and a repository with a remote.

`remote` and `default_branch` come from `config.yaml`. Read them before running anything. The examples below write `origin` and `main` where those values go.

## Find the default branch

Never assume `main` or `master`. Ask the remote:

    git remote set-head origin --auto
    git symbolic-ref --short refs/remotes/origin/HEAD

The first command creates the pointer where it is missing and repairs it where it is stale, so run it even when the second one already answers. It contacts the remote. Where that is not possible, read the existing pointer alone, and fall back to `git remote show origin` for the `HEAD branch` line.

Strip the remote prefix from the answer: `origin/main` names the branch `main`.

Use `default_branch` from config instead where it is set.

## Pick the route

Where the change currently sits decides how it gets onto the default branch. Check with `git status` and `git worktree list`.

| Where the change is | Route |
| --- | --- |
| Uncommitted, in a checkout that has the default branch out | 1. Commit here, then push |
| On a local branch, with the default branch checked out in this same directory | 2. Fast-forward the default branch onto it |
| On a branch in a separate checkout, or the default branch is checked out elsewhere | 3. Push the branch at the default branch ref |

Route 3 is the one that catches people. Git refuses a branch that is checked out somewhere else:

    fatal: 'main' is already used by worktree at '/path/to/repo'

So there is no switching onto the default branch to merge, and pushing the branch straight at the ref is the route rather than a workaround. It puts the same commit on the default branch that the merge would.

## Route 1, commit and push from the default branch

    git add path/to/changed
    git commit
    git fetch origin
    git rebase origin/main
    git push

Rebase rather than merge, so the trunk stays a single line of work.

## Route 2, fast-forward the default branch onto a branch

Bring the default branch current first, or the push that follows is rejected:

    git fetch origin
    git switch main
    git merge --ff-only origin/main
    git merge --ff-only my-task
    git push

Where that second `--ff-only` refuses, the branch was cut from an older trunk. Rebase it onto the current one, then fast-forward:

    git switch my-task
    git rebase origin/main
    git switch main
    git merge --ff-only my-task
    git push

A plain `git merge my-task` also gets past the refusal, and is the wrong answer. With one contributor it buries a merge commit in the trunk that records nothing about the change. `--ff-only` is what makes the divergence surface instead.

## Route 3, push the branch at the default branch ref

From the branch's own checkout:

    git fetch origin
    git rebase origin/main
    git push origin HEAD:main

## Read the rejection

The push succeeds only as a fast-forward, which is the safety property worth having.

- **Non-fast-forward.** The default branch moved while you worked. Fetch, rebase onto `origin/main`, push again.
- **Review or branch protection.** A different animal, and retrying cannot fix it. Stop, put the change on a branch, and open a pull request.

Never force-push the default branch, with or without a lease. A rejection is information about the remote; forcing discards whatever landed there.

## Verify with a separate read

The push output only echoes back what was asked for. Fetch and compare the two commits:

    git fetch origin
    git rev-parse HEAD origin/main

Run it from the checkout that did the push. Two identical hashes mean it landed. Anything else means it did not, whatever the push printed.

## Clean up the merged branch

    git branch -d my-task

`-d` refuses to drop a branch whose commits are nowhere else, which is the check worth keeping; `-D` skips it. Where the branch went up by pushing at the default branch ref, `-d` prints a warning that it is merged to the remote-tracking branch but not to `HEAD`, then deletes it. That warning is the expected outcome, not a failure.

Where the branch lived in a separate checkout, remove that too, running the removal from outside the directory being removed:

    git worktree remove ../my-task

## Undo without rewriting

Anything already pushed gets undone with a new commit:

    git revert <commit>
    git push

No force push, no `reset --hard` followed by a force push, no amending a commit that has been pushed.

Being the only contributor does not make rewriting safe, and it is the reasoning that leads straight to it. One person still has other checkouts, worktrees and automation holding the old commit, and each of them hits a divergence the next time it fetches. A revert costs one commit; the rewrite costs a repair in every copy.

## Bring the other checkouts into step

Any other checkout, the primary one included, holds an older commit after a push. Run this there before starting new work:

    git fetch origin
    git merge --ff-only origin/main

`--ff-only` so a checkout that has quietly diverged says so, instead of being papered over with a merge commit.
