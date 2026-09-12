# California 2020 demo data provenance

`sample_600.json` is a deterministic, weighted resample of California CES 2020 citizen adults who named Trump or Biden. It has 600 demo records but only 529 distinct CES source respondents because sampling is with replacement. Every demo record starts at `base_weight: 1.0`; `ces_commonweight` is retained only as source provenance, so it is not applied a second time.

Create the default sample from the CES CSV supplied outside the repository:

```sh
python3 scripts/sample_ces.py
```

Choose a sample size, seed, or output path when needed:

```sh
python3 scripts/sample_ces.py --size 200 --seed 9 --output data/california-2020/sample_200.json
```

The CES pool uses `inputstate=6`, `cit1=1`, and age 18 or older in 2020. It excludes four records with unknown Hispanic origin because a complete race/ethnicity raking category cannot be assigned.

The pool then keeps only the respondents who named Trump or Biden, which removes 189 other-candidate, 336 undecided, 130 intend-not-to-vote, and 9 missing responses and leaves 4,212 of the 4,876 eligible respondents. `source_exclusions` reports each count. With raking off, a single D/R flip changes the whole-sample margin by 200/N percentage points (about 0.33 for 600 records). With raking on, the change is 200 times the record’s weight divided by the sum of weights. The sample therefore describes Californians who had settled on a major-party candidate during the pre-election period, a narrower population than all citizen adults. Citizenship stands in for California adults eligible to vote. It is not an individual legal eligibility determination.

The presidential outcome is pre-election preference. `CC20_364a` supplies reported early votes. `CC20_364b` supplies preference for people who had not reported an early vote, including the four California cases where the respondent said they had already voted but gave `CC20_364a=5`. The questionnaire routes those cases to `CC20_364b`; no `CC20_364a=5` fallback is present in the generated sample. A theoretical fallback is explicitly labeled as a status at interview, never as final election nonvoting. The source questionnaire and documentation are included in the supplied CES download; the CES Common Content dataset DOI is [10.7910/DVN/E9N6PH](https://doi.org/10.7910/DVN/E9N6PH).

`raking_targets_cps_nov2020.json` contains age, recorded sex, race/ethnicity, and education margins for Californians who reported voting, from the [U.S. Census Bureau's November 2020 CPS Voting and Registration Supplement](https://www.census.gov/data/datasets/2020/demo/cps/cps-voting.html). Recreate it after downloading the public-use ZIP from the URL recorded in the JSON:

```sh
python3 scripts/extract_cps_targets.py --source /path/to/nov20pub.zip
```

The extractor keeps California civilian, noninstitutional citizen adults (`HRINTSTA=1`, `GESTFIPS=6`, `PRPERTYP=2`, age 18+, and `PRCITSHP=1..4`), then keeps the ones who reported voting (`PES1=1`), and applies `PWSSWGT / 10000`. Both totals match Table 4a after that table's rounding to thousands: 16,893,488 reported voters against a published 16,893,000, and 25,946,400 citizen adults against a published 25,946,000. The citizen-adult figures remain in the JSON under `citizen_adult_reference`, which also carries the 65.1 percent reported turnout rate. CPS targets are survey estimates and exclude institutional residents and the Armed Forces. Voting here is self-reported and unvalidated, so the margins describe people who said they voted. They are independent demonstration margins, not a reproduction of the CES weighting procedure or a joint distribution. Reported voting is the closest CPS analogue to the sample's population of people who had settled on a candidate, and it narrows the gap: the mean absolute distance between target and sample margins falls from 3.13 points under citizen-adult targets to 2.31 points. A gap remains, because holding a preference before the election and voting are different things, so raking to these margins still assumes the two populations share a demographic composition. The largest residual is education, where reported voters hold bachelor's degrees at 43.0 percent against 35.8 percent in the sample.

`demo.json` contains the browser’s records and demographic raking weights. Weights start at one and are normalized to average one, with no trimming. Preparation stops if a required category is absent or the targets cannot be reached within the iteration limit. Preference edits leave these weights unchanged.

```sh
python3 scripts/prepare_demo.py
python3 scripts/prepare_demo.py --sample data/california-2020/sample_200.json
```
