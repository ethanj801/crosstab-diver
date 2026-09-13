#!/usr/bin/env python3
"""Compute state citizen-adult raking margins from the Nov. 2020 CPS public-use file."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sample_ces import STATES


# Published figures from Census Table 4a, in thousands. Every entry must be read
# from the published table. An absent state records that no check was configured.
PUBLISHED_TABLE_4A = {
    "GA": {"voted_thousands": 4888, "citizen_thousands": 7400},
}
SOURCE_URL = (
    "https://www2.census.gov/programs-surveys/cps/datasets/2020/supp/nov20pub.zip"
)
LANDING_PAGE = "https://www.census.gov/data/datasets/2020/demo/cps/cps-voting.html"
DOCUMENTATION_URL = "https://www2.census.gov/programs-surveys/cps/techdocs/cpsnov20.pdf"
# Fixed-width positions are 1-based and inclusive, from the Census record layout.
FIELDS = {
    "HRINTSTA": (57, 58),
    "GESTFIPS": (93, 94),
    "PRTAGE": (122, 123),
    "PESEX": (129, 130),
    "PEEDUCA": (137, 138),
    "PTDTRACE": (139, 140),
    "PEHSPNON": (157, 158),
    "PRPERTYP": (161, 162),
    "PRCITSHP": (172, 173),
    "PWSSWGT": (613, 622),
    "PES1": (1001, 1002),
}
# PES1 asks whether the person voted on November 3, 2020. Codes 1 and 2 are yes and no.
# -1 is not in universe and -2, -3, -9 are don't know, refused, and no response.
VOTING_CODES = (1, 2, -1, -2, -3, -9)
LABELS = {
    "age_group": ["18-29", "30-44", "45-64", "65+"],
    "sex": ["male", "female"],
    "race_ethnicity": ["hispanic", "nh_white", "nh_black", "nh_asian", "nh_other"],
    "education": ["hs_or_less", "some_college_or_associate", "bachelors_or_higher"],
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help=f"Downloaded Nov. 2020 CPS ZIP ({SOURCE_URL})",
    )
    parser.add_argument("--state", choices=sorted(STATES), default="GA")
    parser.add_argument(
        "--output",
        type=Path,
        help="default: data/<state>-2020/raking_targets_cps_nov2020.json",
    )
    args = parser.parse_args()
    state_name = STATES[args.state][1].replace("-", " ").title()
    if args.output is None:
        args.output = (
            Path("data")
            / f"{STATES[args.state][1]}-2020"
            / "raking_targets_cps_nov2020.json"
        )
    totals = {field: Counter() for field in LABELS}
    raw_counts = {field: Counter() for field in LABELS}
    total_weight, kept, records = 0, 0, 0
    citizen_adult_weight, citizen_adults = 0, 0
    with (
        zipfile.ZipFile(args.source) as archive,
        archive.open("nov20pub.dat") as stream,
    ):
        for line in stream:
            records += 1
            if len(line.rstrip(b"\r\n")) != 1018:
                raise ValueError(f"unexpected record length at record {records}")
            value = {
                name: int(line[start - 1 : end])
                for name, (start, end) in FIELDS.items()
            }
            if not (
                value["HRINTSTA"] == 1
                and value["GESTFIPS"] == STATES[args.state][0]
                and value["PRPERTYP"] == 2
                and value["PRTAGE"] >= 18
                and value["PRCITSHP"] in (1, 2, 3, 4)
            ):
                continue
            if value["PES1"] not in VOTING_CODES:
                raise ValueError(f"unexpected PES1 code at record {records}")
            citizen_adults += 1
            citizen_adult_weight += value["PWSSWGT"]
            if value["PES1"] != 1:
                continue
            if value["PESEX"] not in (1, 2) or value["PEHSPNON"] not in (1, 2):
                raise ValueError(f"unexpected demographic code at record {records}")
            if not (
                1 <= value["PTDTRACE"] <= 26
                and 31 <= value["PEEDUCA"] <= 46
                and value["PWSSWGT"] > 0
            ):
                raise ValueError(f"unexpected CPS value at record {records}")
            age = value["PRTAGE"]
            race = (
                "hispanic"
                if value["PEHSPNON"] == 1
                else {1: "nh_white", 2: "nh_black", 4: "nh_asian"}.get(
                    value["PTDTRACE"], "nh_other"
                )
            )
            categories = {
                "age_group": "18-29"
                if age < 30
                else "30-44"
                if age < 45
                else "45-64"
                if age < 65
                else "65+",
                "sex": "male" if value["PESEX"] == 1 else "female",
                "race_ethnicity": race,
                "education": "hs_or_less"
                if value["PEEDUCA"] <= 39
                else "some_college_or_associate"
                if value["PEEDUCA"] <= 42
                else "bachelors_or_higher",
            }
            kept += 1
            total_weight += value["PWSSWGT"]
            for field, category in categories.items():
                totals[field][category] += value["PWSSWGT"]
                raw_counts[field][category] += 1
    if records != 134122:
        raise ValueError(f"unexpected total record count: {records}")
    margins = {
        field: {
            category: {
                "proportion": totals[field][category] / total_weight,
                "population_estimate": totals[field][category] / 10000,
                "unweighted_cps_count": raw_counts[field][category],
            }
            for category in categories
        }
        for field, categories in LABELS.items()
    }
    published = PUBLISHED_TABLE_4A.get(args.state)
    published_checks = (
        [
            {
                "table": f"Table 4a, {state_name} total voted",
                "published_thousands": published["voted_thousands"],
                "computed_population_estimate": total_weight / 10000,
                "difference_persons_from_published_rounded_thousands": total_weight
                / 10000
                - published["voted_thousands"] * 1000,
            },
            {
                "table": f"Table 4a, {state_name} total citizen population",
                "published_thousands": published["citizen_thousands"],
                "computed_population_estimate": citizen_adult_weight / 10000,
                "difference_persons_from_published_rounded_thousands": citizen_adult_weight
                / 10000
                - published["citizen_thousands"] * 1000,
            },
        ]
        if published
        else "No published Table 4a figures are configured for this state."
    )
    result = {
        "source": {
            "name": "U.S. Census Bureau, November 2020 Current Population Survey Voting and Registration Supplement",
            "landing_page": LANDING_PAGE,
            "data_url": SOURCE_URL,
            "documentation_url": DOCUMENTATION_URL,
            "source_zip_sha256": hashlib.file_digest(
                args.source.open("rb"), "sha256"
            ).hexdigest(),
            "weight": "PWSSWGT / 10000 (four implied decimal places)",
        },
        "state": args.state,
        "population": f"{state_name} civilian noninstitutional U.S. citizens age 18 or older who reported voting in the November 2020 election",
        "population_role": "Reported voters. Self-reported participation, not a validated vote record or a legal-eligibility count",
        "filters": {
            "HRINTSTA": 1,
            "GESTFIPS": STATES[args.state][0],
            "PRPERTYP": 2,
            "PRTAGE": ">=18",
            "PRCITSHP": [1, 2, 3, 4],
            "PES1": 1,
        },
        "unweighted_cps_count": kept,
        "population_estimate": total_weight / 10000,
        "citizen_adult_reference": {
            "unweighted_cps_count": citizen_adults,
            "population_estimate": citizen_adult_weight / 10000,
            "reported_turnout_rate": total_weight / citizen_adult_weight,
        },
        "published_table_checks": published_checks,
        "category_mapping": {
            "age_group": "PRTAGE: 18-29, 30-44, 45-64, 65+; topcoded 80 and 85 remain 65+",
            "sex": "PESEX: 1 male; 2 female; source records sex, not gender identity",
            "race_ethnicity": "PEHSPNON=1 Hispanic any race. Otherwise PTDTRACE: 1 White alone, 2 Black alone, 4 Asian alone, all remaining codes nh_other (including multiracial).",
            "education": "PEEDUCA 31-39 hs_or_less; 40-42 some_college_or_associate; 43-46 bachelors_or_higher",
            "voting": "PES1=1 reported voting. Codes 2, -2, -3, and -9 are excluded, matching the published Total voted column.",
        },
        "margins": margins,
        "limitations": [
            "These are weighted CPS survey estimates, not exact population counts; small categories have sampling error.",
            "Citizen adults are a proxy for voting eligibility. CPS excludes institutional residents and this civilian filter excludes Armed Forces; it does not identify every legal disqualification.",
            "The marginal category boundaries are demonstration choices rather than a universal polling standard.",
            "Do not treat marginal targets as a known joint demographic distribution.",
            "Voting is self-reported. Survey respondents overstate voting, and CPS does not validate reports against voter files.",
            "People who did not answer PES1 are excluded from the voted total rather than counted as nonvoters, following the published table.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        f"Wrote {args.output} from {kept} {state_name} reported-voter CPS records ({citizen_adults} citizen adults)"
    )


if __name__ == "__main__":
    main()
