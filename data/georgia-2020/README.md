# Georgia 2020 demo data

The three JSON files in this directory contain the sample, demographic calibration targets, and prepared browser data.

Run the commands below from the repository root with Python 3.11 or newer. The scripts use only the standard library. The original CES CSV and CPS ZIP are not included.

## Sample: `sample_600.json`

The included sample contains 600 draws from 1,707 Georgia CES 2020 citizen adults who named Biden or Trump before the election, including reported early votes. Sampling uses CES `commonweight` with replacement and seed `2020`, producing 472 unique source respondents and 128 repeated draws. Each draw has a distinct demo ID.

Before sampling, the script excludes 24 noncitizens and 3 records with unknown Hispanic origin. It also excludes 134 undecided, 40 other-candidate, 90 intended nonvoting, and 4 missing presidential responses.

Source: [CES 2020 Common Content](https://doi.org/10.7910/DVN/E9N6PH). The sampler expects a CSV with numeric source codes; the included sample was generated from `CES20_Common_OUTPUT_vv.csv`.

```sh
python3 scripts/sample_ces.py \
  --input /path/to/CES20_Common_OUTPUT_vv.csv \
  --state GA --size 600 --seed 2020
```

Change `--size` or `--seed` to draw a different sample. The default output filename follows the sample size, such as `sample_200.json`. The JSON records the source hash, exclusions, sampling settings, and source respondent IDs.

## Calibration targets: `raking_targets_cps_nov2020.json`

Targets describe Georgia civilian, noninstitutional U.S. citizens aged 18 or older who reported voting in the November 2020 CPS Voting and Registration Supplement.

The 1,209 CPS records represent an estimated 4,887,508 reported voters. The citizen-adult reference is 7,399,525. Both totals match published Table 4a after rounding to thousands. These are weighted survey estimates; voting is self-reported rather than validated.

Sources: [CPS November 2020 data](https://www.census.gov/data/datasets/2020/demo/cps/cps-voting.html), [Table 4a](https://www2.census.gov/programs-surveys/cps/tables/p20/585/table04a.xlsx).

Download the November 2020 public-use ZIP, `nov20pub.zip`. The extractor reads `nov20pub.dat` directly from the archive.

```sh
python3 scripts/extract_cps_targets.py \
  --source /path/to/nov20pub.zip --state GA
```

The output records separate age, sex, race/ethnicity, and education proportions, along with category mappings and source metadata. CES and CPS race definitions differ, and some categories have small samples. The CES preference holders and CPS reported voters are different populations, so these targets provide an illustrative calibration.

## Prepared browser data: `demo.json`

Preparation maps source Biden/Trump preferences to D/R and calculates demographic raking weights. Weights start at one and are normalized to average one, without trimming. CES weights already determined sampling probabilities and are not applied again.

Raking matches the separate demographic proportions, not their joint distribution. Preferences do not enter the calculation, so editing them in the browser leaves weights fixed. Preparation rejects mismatched states, absent target categories, and failure to converge.

Regenerate from the included sample and targets:

```sh
python3 scripts/prepare_demo.py
```

For a different sample size, pass the generated sample explicitly:

```sh
python3 scripts/prepare_demo.py \
  --sample data/georgia-2020/sample_200.json
```

By default, preparation reads the targets and writes `demo.json` beside the selected sample. Use `--targets` and `--output` to override those paths.

After regenerating the browser data, rebuild and update the standalone HTML included in the repository:

```sh
npm run build
cp dist/index.html crosstab-investigator.html
```
