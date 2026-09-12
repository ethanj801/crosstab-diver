# Georgia 2020 demo data provenance

`sample_600.json` contains 600 draws from 1,707 Georgia CES 2020 citizen adults who named Biden or Trump before the election, including reported early votes. Sampling uses CES commonweight with replacement: the sample contains 472 unique source respondents and 128 repeated draws. Source Biden/Trump responses are displayed as D/R. The pool excludes 134 undecided, 40 other-candidate, 90 intended nonvoting, and 4 missing presidential responses, after demographic eligibility exclusions.

Source: [CES 2020 Common Content](https://doi.org/10.7910/DVN/E9N6PH).

```sh
python3 scripts/sample_ces.py
python3 scripts/sample_ces.py --state GA --size 200 --seed 9
```

Raking targets describe Georgia civilian, noninstitutional citizen adults who reported voting in the November 2020 CPS. The 1,209 CPS records represent an estimated 4,887,508 reported voters; the citizen-adult reference is 7,399,525. Both totals match published Table 4a after rounding to thousands. Pre-election preference holders and reported voters are different populations, so this is an illustrative calibration, not a representative election estimate. The interface label “Voter” does not establish validated turnout.

Sources: [CPS November 2020 data](https://www.census.gov/data/datasets/2020/demo/cps/cps-voting.html), [Table 4a](https://www2.census.gov/programs-surveys/cps/tables/p20/585/table04a.xlsx).

```sh
python3 scripts/extract_cps_targets.py --source /path/to/nov20pub.zip
```

`demo.json` contains fixed demographic weights, starting from one and normalized to average one, without trimming. CES weights are not applied again. Raking matches separate age, sex, race/ethnicity, and education margins, not their joint distribution. Some categories are small, and CES/CPS race definitions differ. Preference edits leave weights unchanged. Preparation rejects mismatched states, missing target categories, and failure to converge.

```sh
python3 scripts/prepare_demo.py
python3 scripts/prepare_demo.py --sample data/georgia-2020/sample_200.json
npm run build
```
