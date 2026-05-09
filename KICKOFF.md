# Claude Code Kickoff — SentinelFlow v2 Upgrade

## Your Task (This Session Only)

You are NOT writing code yet. This session is for codebase
audit and planning only. Output ONE document
(`AUDIT_AND_PROPOSAL.md`) and stop.

Read in this exact order:
1. `README.md`
2. `PLAN.md` (the upgrade plan — authoritative; pay special
   attention to Sections 2 (literature), 4 (phase order),
   5 (deliverables with DoDs), 9 (success criteria), and
   10.1 (git policy)).
3. `sentinelflow_journal_v9_final.tex` (current paper draft;
   read-only context).
4. `INCS_870_Project_I__SP26__Team02_final_04072026.pdf` (final
   report; read-only context — extract via `pdftotext` if
   text not directly readable).
5. The actual codebase: walk all `.py`, `.yaml`, `.json`,
   `.md`, and config files under the project root. Build
   a structural mental map.

## Required Output: `AUDIT_AND_PROPOSAL.md`

Produce a single markdown document at the repo root with the
following sections, in order.

### Section 1: Codebase Audit
- Existing module inventory: a table of `path → one-line purpose`.
- Existing test coverage: what is tested, what is not, and
  which tests run on a clean checkout.
- Integration points for upcoming work:
  - Where would a new "channel inspector" plug in (Phase 2)?
  - Where does the audit hash chain currently get written
    and verified?
  - Where is the embedding model loaded (Phase 1.F)?
  - Where is the FAISS secret index built and queried?
  - Where are amplifier keywords / sensitive object lists
    stored (relevant to Phase 3.K adaptive attack)?
- Hidden technical debt that will block Phase 1 or Phase 2
  (hard-coded paths, missing abstractions, fragile tests,
  data files not in repo, etc.). Be specific; vague answers
  are unhelpful.
- Confirm or deny: does the codebase match what
  `sentinelflow_journal_v9_final.tex` describes? Note any
  gap between paper claims and implementation reality.

### Section 2: Reading of PLAN.md
For each Phase 1 deliverable (A, B, C, D, E, F) and each
Phase 2 deliverable (G, H, I, J), produce a sub-section
containing:
- Existing modules to reuse.
- New modules to create (path + one-line purpose).
- External dependencies needed (with version pin if relevant).
  Justify each new dependency.
- External resources required from the user (API keys,
  dataset access, paper-ID confirmations, GitHub repos to
  clone).
- Estimated effort in hours (be realistic — pessimistic is
  fine, aspirational is not).
- Top 1–3 risks and proposed mitigations.

For Phase 3 deliverables (K, L, M, N), a lighter sketch is
acceptable but the same structure should hold.

Flag any deliverable whose feasibility is unclear given the
current codebase. Do not silently assume something will work.

### Section 3: Sequenced Implementation Plan
- A numbered list of work items in your recommended execution
  order. Each item must be small enough to complete in a
  single working session (≤4 hours).
- Respect the Phase 1 → Phase 2 ordering decreed in PLAN.md
  Section 4. Within Phase 1, the suggested intra-phase
  sequence (F → E → D → A → B → C) is a recommendation, not
  a requirement; if you propose a different order, justify it
  in 2–3 sentences.
- For the FIRST work item only, include a detailed sub-plan:
  files to create, function signatures, test cases, the smoke
  test you will use to demonstrate completion.
- Explicitly call out any item that requires the user to
  provide external resources first (API keys, dataset access,
  paper-ID or repo-URL confirmation).

### Section 4: Open Questions for the User
List up to 10 clarification questions you need answered
before starting Phase 1 implementation. Concrete examples of
the kinds of questions that would be useful:
- Does the user's OpenAI account have GPT-4o quota for
  approximately N calls (estimate N based on Phase 1
  deliverable sizing)?
- Is the existing FAISS secret index regeneratable from
  source files in the repo, or should it be treated as a
  fixed binary input?
- Is `Privatris/AgentLeak` GitHub repo accessible to the
  user? If not, what is the fallback for AgentLeak data?
- Is the CNFinBench dataset publicly downloadable as of the
  current date, or does it require contacting authors? How
  should English adaptation be approached if upstream is
  Chinese-only?
- For Phase 1.E (Hard-Negative FPR), are there existing L1
  examples in the repo that can serve as seeds, or must
  these be authored from scratch?
- For Phase 1.F embedding ablation, should the
  finance-finetuned candidate be open-source-only, or are
  paid/API-based encoders acceptable?
- Are there any AWS or infrastructure constraints (the v9
  paper mentions PostgreSQL + pgvector on AWS) that affect
  where new evaluation runs can execute?
- For Phase 2 LangGraph integration, is LangGraph already a
  project dependency, or will adding it conflict with any
  existing pinned package?
- Are there any compute / time-budget constraints on benchmark
  runs (e.g., must complete on a single laptop overnight)?
- Should Phase 1 results targeting v9-reproduction-comparison
  be run with the existing all-MiniLM-L6-v2 first, or with
  the chosen Phase-1-F primary model?

### Section 5: What You Will NOT Do
Explicitly list anything in PLAN.md you are deferring or
descoping in your proposed sequence, with reason. Honest
scope-cutting is more valuable than over-promising. Make
clear which descopes are "skip entirely" versus "defer until
later in the timeline."

### Section 6: Self-Check on Git Policy
Confirm in writing that you have read PLAN.md Section 10.1
and that you understand the following are forbidden without
per-command, in-session authorization:
- `git push` in any form (including `--force-with-lease`).
- Modifying `.git/config` or `.git/hooks/`.
- Any GitHub CLI write command.
- Any other operation that uploads code to a remote.

If you have any uncertainty about whether a planned operation
counts as "uploading to a remote," list it here as a question
for the user.

## Constraints for This Session

- Do NOT modify any existing file.
- Do NOT create any file other than `AUDIT_AND_PROPOSAL.md`
  (and `.claude/settings.json` is already present; do not
  modify it).
- Do NOT install new dependencies.
- Do NOT run experiments (no LLM API calls, no benchmark
  runs, no model downloads beyond what is already cached).
- Do NOT commit anything in this session. Just create
  `AUDIT_AND_PROPOSAL.md` and leave it unstaged for user
  review.
- Do NOT run `git push`, `git remote` (write), `git p4`,
  `git svn`, or any GitHub CLI command that uploads. The
  full forbidden list is in PLAN.md Section 10.1.
- Read-only git commands and read-only filesystem inspection
  (`find`, `grep`, `ls`, `wc -l`, `pdftotext`, etc.) are
  fine.

If you find yourself about to violate any of the above, stop
and write the violation as a question in Section 4 instead.

When `AUDIT_AND_PROPOSAL.md` is written, stop and wait for
user review.