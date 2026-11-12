---
title: "Git workflow"
linkTitle: "Git workflow"
description: "How Katzenpost repositories pin, merge, review and release with git."
author: ["David Stainton"]
draft: false
url: "docs/git_workflow"
---

Katzenpost is spread over many repositories that depend on one
another, so git history is part of the build. A dependency names a
commit in another repository, and that commit must stay reachable for
as long as anything names it. Use this checklist when a change crosses
repositories or when you merge, review or release.

## Checklist

1. **Pin to a commit, never a branch name.** A branch moves; a commit
   hash does not. In Cargo write `rev = "<full sha>"`; in Go use the
   pseudo-version, such as `v0.0.0-20191109021931-daa7c04131f5`.
   Pinning to the head commit of an open pull request lets downstream
   work proceed before the upstream change merges.
2. **Merge pinned pull requests with a merge commit.** Squash and
   rebase merges replace the pull request's commits with new ones.
   Once the branch is deleted, the pinned commits are unreachable and
   downstream builds fail.
3. **Repin after the upstream merges.** Move the downstream pin to a
   commit on `main`, so that no build depends on a feature branch for
   long.
4. **Chain cross-repository changes, source first.** Land the change in
   the repository that everything else depends on, then in each
   dependent in order, then tag the release. For example, a fix in
   highctidh-rs goes through hpqc, then pigeonhole_protocols, then
   hushphone.
5. **Make release builds reproducible.** Sort inputs, keep build paths
   out of the output, set a fixed `SOURCE_DATE_EPOCH`, and keep
   changelog dates in the past. Before tagging, build twice in
   different directories and check that the outputs are
   byte-identical.
6. **Tags publish releases.** If the release from a tag fails, leave
   the tag alone; fix the problem and tag the next patch version.
7. **Review by a second person.** In the repositories that require
   review, someone who did not open the pull request approves and
   merges it. Never merge your own pull request there.
8. **A red check is a failure.** It is a failure even when `main`
   shows the same failure. Runner images and toolchains change under
   you: `ubuntu-latest` moves to each new Ubuntu release, and a new Go
   release can reject a prebuilt cgo library. Pin the runner image,
   such as `runs-on: ubuntu-24.04`, where a job depends on its
   packages.

## Sources

- Scott Chacon and Ben Straub, Pro Git:
  [Basic Branching and Merging](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging)
  and [Rebasing](https://git-scm.com/book/en/v2/Git-Branching-Rebasing).
- GitHub, [About merge methods on GitHub](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github).
- The Cargo Book, [Specifying dependencies from git repositories](https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html#specifying-dependencies-from-git-repositories).
- Go Modules Reference, [Pseudo-versions](https://go.dev/ref/mod#pseudo-versions).
- reproducible-builds.org, [SOURCE_DATE_EPOCH](https://reproducible-builds.org/docs/source-date-epoch/)
  and [Build path](https://reproducible-builds.org/docs/build-path/).
- [GitHub Actions runner images](https://github.com/actions/runner-images).
