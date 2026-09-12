# Project scope

- Aim for a small, self-contained interactive polling demonstration that fits roughly 2–3 hours of total work. Do not expand scope without agreement.
- The proposed MVP lets users change individual respondents' votes or subgroup membership and observe topline and subgroup results, with a control to turn raking on or off. Raking off means unweighted results, not freezing previously calculated weights.
- Investigate how small subgroup samples and weighting can make subgroup results sensitive while topline results remain relatively stable. Treat the statistical mechanism as something to validate, not a predetermined conclusion.
- Explainers and a challenge/game mode are stretch goals, secondary to the agreed MVP.
- Voting scope is the 2020 presidential election only. The sample and raking targets should represent California adults eligible to vote; document any use of citizen adults as a proxy. Keep nonvoting and missing responses distinguishable from candidate choices.

# Collaboration and approval

- Prefer clarification before making consequential design or implementation choices. Present questions in numbered form with inline lettered options (a, b, c) for quick replies.
- Treat requests such as "help me get started" and tentative phrasing such as "maybe" as discovery unless implementation scope is explicitly approved.
- When a user names a plan, memory, file, PR, issue, or other concrete artifact and it cannot be found, stop and ask for the missing location before editing code or adjacent repositories.
- When investigation contradicts or invalidates the agreed plan, report the blocker and present choices. Wait for explicit approval before substituting an approach.
- Before adding or changing user-facing explanatory or narrative copy, including microcopy, surface the exact proposed text for user approval and a prose pass. For each item, state where it goes, its function, whether it can be removed, and what would be lost. Batch related copy reviews when useful.

# Git and coordination

- Stage changes deliberately and make small, logical commits as work progresses. Do not include unrelated changes.
- Never add AI attribution to commits: no AI co-author trailers, session links, generated-by lines, or other AI-authorship markers.
- Maintain `coordination.log.md` as an append-only, gitignored coordination log. Append dated entries for decisions, status, validation, blockers, and open questions. Correct earlier entries by appending a correction, never by rewriting history.
- Keep `AGENTS.md` as the canonical shared instruction file and `CLAUDE.md` as a relative symlink to it.
