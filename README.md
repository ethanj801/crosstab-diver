# Crosstab Investigator

Crosstab diving (trying to interpret the voting behavior of smaller groups by breaking them out of a larger poll) is an extremely tempting but statistically unsound idea. Although statistical [pundits](https://x.com/NateSilver538/status/1836964596466233458) inveigh against crosstab diving, it remains a [popular](https://www.jns.org/u.s.-news/new-poll-signals-mamdani-leads-cuomo-by-17-points-among-jewish-new-yorkers) [way](https://www.nbcnews.com/politics/2024-election/poll-shows-biden-support-slumping-michigan-muslims-rcna123732) to get [clicks](https://www.rasmussenreports.com/public_content/politics/general_politics/july_2019/trump_support_up_this_week_among_black_voters).

This repo provides an interactive demonstration of why crosstab diving is problematic, showing how individual responses modify polling results and their crosstabs.

Change a few presidential preferences and compare the movement in a demographic subgroup with the movement in the overall result. Turn raking on to explore how respondents can have different amounts of influence.

## Using the demo

Open the [standalone HTML file](crosstab-investigator.html) in a desktop or laptop browser. Or go to https://ethanj801.github.io/crosstab-investigator/

The demo shows an illustrative mock poll of Georgia in 2020. You can see the overall margin and the margin of any selected subgroup (i.e. a crosstab). You can select respondents, see their demographic information, and change their preference between D and R to watch the margins of both the subgroup and the topline move.

Real polls use **raking** to weight responses. Raking is a process by which pollsters address response bias (different groups participate at rates that don't match their share of the electorate) by reweighting the value of each respondent. You can turn on raking in the demo by using the toggle in the top right. Notice how the poll moves after you do so. You'll also notice that some respondents will now move the topline and their subgroup more or less sharply than before. You can see the weighting of each respondent on their breakdown screen. Weights are normalized to have an average of 1; higher weight means more influence on the poll.

## Data and weighting

The demo uses a mock poll of 600 people (typical size for a state poll) from the state of Georgia in 2020. The mock poll is constructed using respondents from the 2020 Cooperative Election Study (CES). We construct the poll by sampling (with replacement using the CES survey weights) from the set of voters who report either a preference or an early vote for Biden or Trump. When both early votes and preferences are given, we use the early vote. Undecided, other-candidate, intended nonvoting, and missing responses are excluded for simplicity of modeling. 

Raking data is precomputed. Our raking targets Georgia adults who reported in the Census Bureau's November 2020 Current Population Survey (CPS) Voting and Registration Supplement that they voted. The demo matches age, sex, race/ethnicity, and education proportions. As is typical for a poll of this size, we rake only against the individual categories and not against interactions.

It is important to note that this poll is designed to be an illustrative exercise in sensitivity to individual responses, and not an actual replication of a Georgia poll or a diagnostic aid. 

## Developing and rebuilding

The interface uses React, TypeScript, and Vite. Development requires Node.js 22.18 or newer.

```sh
npm install
npm run dev
```

To generate the standalone HTML file:

```sh
npm run build
```

The output can be found at `dist/index.html`.

Prepared data for Georgia is included, but the underlying sample or weighting can be changed using the scripts in the `scripts/` folder. States or sample sizes can be changed relatively easily, but beware, some states have significantly fewer respondents than others, making sampling tricky (e.g. sampling 1000 voters from a state with 600 respondents is less than ideal).

- `scripts/sample_ces.py` draws the sample and exposes sample-size and seed options.
- `scripts/extract_cps_targets.py` extracts demographic calibration targets.
- `scripts/prepare_demo.py` calculates weights and produces the data used by the interface.

After changing the sample or targets, run `npm run prepare:data`, then rebuild the HTML.
