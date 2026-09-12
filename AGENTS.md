# Project scope

- Aim for a small, self-contained interactive polling demonstration that fits roughly 2–3 hours of total work. Do not expand scope without agreement.
- Target desktop and laptop browsers only. Phone/mobile layouts and touch-specific interaction support are outside the agreed scope.
- The core MVP is a populated main page where users change individual respondents' presidential preferences and compare subgroup changes with topline changes. Begin with direct interaction; tutorials and explainer popups are optional later additions.
- Weighting is a secondary learning layer, with a control to turn raking on or off. Raking off means unweighted results, not freezing previously calculated weights. Editing demographic membership is a secondary feature.
- Investigate how small subgroup samples and weighting can make subgroup results sensitive while topline results remain relatively stable. Treat the statistical mechanism as something to validate, not a predetermined conclusion.
- Explainers and a challenge/game mode are stretch goals, secondary to the agreed MVP.
- The MVP is an illustrative binary D/R toy model, using California CES 2020 presidential-preference records as source material. Use D and R as the displayed outcome labels. A binary sample retains source Biden/Trump preferences, mapped to D/R; do not invent candidate choices for excluded responses.
- Realistic population sampling and alignment with real-world election results are deferred. Treat any California demographic targets used in the toy as reference calibration targets, without claiming that a preference-filtered sample represents all eligible adults. Preserve source provenance and document exclusions.

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
- Maintain `design-decisions.md` as a gitignored record of factual, agreed design intent. Keep open proposals clearly separate from confirmed decisions. Ethan authorizes adding information to the coordination/decision records as work proceeds; explicitly flag new design-decision entries to him so he can check alignment. This does not authorize deciding unresolved design choices or bypassing approval of user-facing copy.
- Maintain `future_directions.md` as a gitignored record of improvements Ethan could pursue with more time. Include the motivation and relevant tradeoffs for each idea. These are deferred possibilities, not commitments or authorization to expand the MVP; keep them distinct from confirmed design decisions and pre-submission requirements in EthanToDo.md.
- `EthanToDo.md` is Ethan's gitignored checklist of things to do before submission. When Ethan starts wrapping up, finishing the project, or preparing to submit, read it and proactively remind him of outstanding items. Do not mark his review tasks complete without his confirmation.
- Keep `AGENTS.md` as the canonical shared instruction file and `CLAUDE.md` as a relative symlink to it.
