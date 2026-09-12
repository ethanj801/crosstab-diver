# California 2020 demo data provenance

`sample_600.json` is a deterministic, weighted resample of California CES 2020 citizen adults. It has 600 demo records but only 530 distinct CES source respondents because sampling is with replacement. Every demo record starts at `base_weight: 1.0`; `ces_commonweight` is retained only as source provenance, so it is not applied a second time.

Create the default sample from the CES CSV supplied outside the repository:

```sh
python3 scripts/sample_ces.py
```

Choose a sample size, seed, or output path when needed:

```sh
python3 scripts/sample_ces.py --size 200 --seed 9 --output data/california-2020/sample_200.json
```

The CES pool uses `inputstate=6`, `cit1=1`, and age 18 or older in 2020. It excludes four records with unknown Hispanic origin because a complete race/ethnicity raking category cannot be assigned. The population is California citizen adults, a proxy for California adults eligible to vote. It is not an individual legal eligibility determination.

The presidential outcome is pre-election preference. `CC20_364a` supplies reported early votes. `CC20_364b` supplies preference for people who had not reported an early vote, including the four California cases where the respondent said they had already voted but gave `CC20_364a=5`. The questionnaire routes those cases to `CC20_364b`; no `CC20_364a=5` fallback is present in the generated sample. A theoretical fallback is explicitly labeled as a status at interview, never as final election nonvoting. The source questionnaire and documentation are included in the supplied CES download; the CES Common Content dataset DOI is [10.7910/DVN/E9N6PH](https://doi.org/10.7910/DVN/E9N6PH).

`raking_targets_cps_nov2020.json` contains age, recorded sex, race/ethnicity, and education margins from the [U.S. Census Bureau's November 2020 CPS Voting and Registration Supplement](https://www.census.gov/data/datasets/2020/demo/cps/cps-voting.html). Recreate it after downloading the public-use ZIP from the URL recorded in the JSON:

```sh
python3 scripts/extract_cps_targets.py --source /path/to/nov20pub.zip
```

The extractor keeps California civilian, noninstitutional citizen adults (`HRINTSTA=1`, `GESTFIPS=6`, `PRPERTYP=2`, age 18+, and `PRCITSHP=1..4`) and applies `PWSSWGT / 10000`. Its 25,946,400 estimate is consistent with Table 4a's published California total citizen population of 25,946,000 after that table's rounding to thousands. CPS targets are survey estimates and exclude institutional residents and the Armed Forces; they remain a citizen-adult proxy rather than a complete legal voting-eligibility frame. They are independent demonstration margins, not a reproduction of the CES weighting procedure or a joint distribution.
