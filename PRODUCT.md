# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

Desktop and laptop browsers only. The deliverable is a self-contained HTML file that can be opened directly, with its code, styles, and demo data embedded.

## Stack

Implemented: React and TypeScript for the interface, Vite for development and bundling, and Python for sample preparation and demographic raking weights. Maintain separate source modules and generate the single-file deliverable through the build.

With demographics and targets fixed, Python can calculate weights once per prepared sample. The browser calculates original and edited results using equal or prepared weights. The demo needs no application backend or Python runtime in the browser. Demographic editing would require revisiting where weights are calculated.

## Users

Politically engaged general readers who encounter polls, such as an NYT reader or occasional FiveThirtyEight reader, without assumed fluency in polling methods.

## Product Purpose

Help readers interpret striking polling subgroup results more carefully. Through editing individual preferences, visitors should see that a small subgroup can move substantially while the whole-sample result changes little, and connect that difference to subgroup size.

Weighting is a secondary learning layer: visitors inspect individual influence and compare the same edits with and without demographic raking. Do not assume weighting always makes subgroup sensitivity worse. [VISION.md](VISION.md) is the concise statement of purpose and intended learning outcomes.

## Operating Context

Visitors open a populated sample, initially unweighted and unfiltered. They select respondents, explicitly change preferences, and use demographic filters to compare subgroup and whole-sample margins. They can keep exploring and editing, toggle weighting, and reset preferences to repeat an experiment.

Each opening or refresh starts fresh. Edits persist throughout the current session when filters, pages, selection, or weighting mode change.

## Capabilities and Constraints

- Keep the project small and self-contained, within the agreed roughly two-to-three-hour scope.
- Use a default sample of 600 records with binary D/R preferences, sourced from California CES 2020 presidential preferences. Sample size is configurable in the preparation script, not a requested interface control.
- Show race/ethnicity, age, education, and sex filters together. Each chooses one category or All; conditions across dimensions form an intersection.
- Compare original and current margins under the same selected weighting mode. Raking off means equal weights. Show subgroup record counts and expose individual weights.
- Preserve respondent positions after preference edits. Selection and editing are separate actions; selected and changed records have distinct indicators. Paginate large groups.
- Show the whole-sample result once when unfiltered. An empty subgroup retains its identity and zero count, with an unavailable margin. Clear selection when navigation hides the selected respondent; preserve edits.
- Reset all original preferences, including offscreen records, while retaining filters and weighting mode. Manual reversal is available; undo history and saved sessions are outside the initial scope.
- Treat the data as an illustrative toy, not a representative election estimate. Demographic-only raking is the initial weighting model.
- Demographic editing, games, tutorials, extra outcome categories, partisan weighting, related-group results, the miniature overview, and more realistic population anchoring remain deferred.

## Evidence on Hand

- [Sample and calibration data](data/california-2020/README.md): CES pre-election preferences, including reported early votes, restricted to source Biden/Trump responses; California demographic targets from CPS reported voters. The populations differ. The 600 resampled records include repeated source respondents with distinct demo IDs.
- [Preparation scripts](scripts/): sampling, CPS target extraction, and demographic weight preparation are implemented. The browser app is in `src/`; `npm run build` generates `dist/index.html`.
- [Exploratory mockups](mockups/poll-layouts.html): structural references with invented values and older labels; later decisions supersede them.

## Product Principles

- Let direct interaction make the statistical relationship tangible.
- Give subgroup size and its change prominence alongside the topline change.
- Keep comparisons honest and distinguish observed sensitivity from claims about real-world poll accuracy.
- Keep text sparse; use the approved functional wording and review any new explanatory copy with Ethan.

Detailed interaction decisions and the approved copy batch live in the local, gitignored `design-decisions.md`; status and provenance are in `coordination.log.md`. `AGENTS.md` governs collaboration and review. These records retain detail and history without expanding the vision.
