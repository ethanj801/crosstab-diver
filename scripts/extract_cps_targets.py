#!/usr/bin/env python3
"""Compute California citizen-adult raking margins from the Nov. 2020 CPS public-use file."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import zipfile


SOURCE_URL = "https://www2.census.gov/programs-surveys/cps/datasets/2020/supp/nov20pub.zip"
LANDING_PAGE = "https://www.census.gov/data/datasets/2020/demo/cps/cps-voting.html"
DOCUMENTATION_URL = "https://www2.census.gov/programs-surveys/cps/techdocs/cpsnov20.pdf"
# Fixed-width positions are 1-based and inclusive, from the Census record layout.
FIELDS = {
    "HRINTSTA": (57, 58), "GESTFIPS": (93, 94), "PRTAGE": (122, 123),
    "PESEX": (129, 130), "PEEDUCA": (137, 138), "PTDTRACE": (139, 140),
    "PEHSPNON": (157, 158), "PRPERTYP": (161, 162), "PRCITSHP": (172, 173),
    "PWSSWGT": (613, 622),
}
LABELS = {
    "age_group": ["18-29", "30-44", "45-64", "65+"],
    "sex": ["male", "female"],
    "race_ethnicity": ["hispanic", "nh_white", "nh_black", "nh_asian", "nh_other"],
    "education": ["hs_or_less", "some_college_or_associate", "bachelors_or_higher"],
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True,
                        help=f"Downloaded Nov. 2020 CPS ZIP ({SOURCE_URL})")
    parser.add_argument("--output", type=Path,
                        default=Path("data/california-2020/raking_targets_cps_nov2020.json"))
    args = parser.parse_args()
    totals = {field: Counter() for field in LABELS}
    raw_counts = {field: Counter() for field in LABELS}
    total_weight, kept, records = 0, 0, 0
    with zipfile.ZipFile(args.source) as archive, archive.open("nov20pub.dat") as stream:
        for line in stream:
            records += 1
            if len(line.rstrip(b"\r\n")) != 1018:
                raise ValueError(f"unexpected record length at record {records}")
            value = {name: int(line[start - 1:end]) for name, (start, end) in FIELDS.items()}
            if not (value["HRINTSTA"] == 1 and value["GESTFIPS"] == 6 and value["PRPERTYP"] == 2
                    and value["PRTAGE"] >= 18 and value["PRCITSHP"] in (1, 2, 3, 4)):
                continue
            if value["PESEX"] not in (1, 2) or value["PEHSPNON"] not in (1, 2):
                raise ValueError(f"unexpected demographic code at record {records}")
            if not (1 <= value["PTDTRACE"] <= 26 and 31 <= value["PEEDUCA"] <= 46 and value["PWSSWGT"] > 0):
                raise ValueError(f"unexpected CPS value at record {records}")
            age = value["PRTAGE"]
            race = ("hispanic" if value["PEHSPNON"] == 1 else
                    {1: "nh_white", 2: "nh_black", 4: "nh_asian"}.get(value["PTDTRACE"], "nh_other"))
            categories = {
                "age_group": "18-29" if age < 30 else "30-44" if age < 45 else "45-64" if age < 65 else "65+",
                "sex": "male" if value["PESEX"] == 1 else "female",
                "race_ethnicity": race,
                "education": "hs_or_less" if value["PEEDUCA"] <= 39 else "some_college_or_associate" if value["PEEDUCA"] <= 42 else "bachelors_or_higher",
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
            category: {"proportion": totals[field][category] / total_weight,
                       "population_estimate": totals[field][category] / 10000,
                       "unweighted_cps_count": raw_counts[field][category]}
            for category in categories
        }
        for field, categories in LABELS.items()
    }
    result = {
        "source": {
            "name": "U.S. Census Bureau, November 2020 Current Population Survey Voting and Registration Supplement",
            "landing_page": LANDING_PAGE, "data_url": SOURCE_URL, "documentation_url": DOCUMENTATION_URL,
            "source_zip_sha256": hashlib.file_digest(args.source.open("rb"), "sha256").hexdigest(),
            "weight": "PWSSWGT / 10000 (four implied decimal places)",
        },
        "population": "California civilian noninstitutional U.S. citizens age 18 or older, November 2020",
        "population_role": "Proxy for voting-eligible adults, not an exact legal-eligibility count",
        "filters": {"HRINTSTA": 1, "GESTFIPS": 6, "PRPERTYP": 2, "PRTAGE": ">=18", "PRCITSHP": [1, 2, 3, 4]},
        "unweighted_cps_count": kept, "population_estimate": total_weight / 10000,
        "published_table_check": {"table": "Table 4a, California total citizen population", "published_thousands": 25946,
                                   "computed_population_estimate": total_weight / 10000,
                                   "difference_persons_from_published_rounded_thousands": total_weight / 10000 - 25946000},
        "category_mapping": {
            "age_group": "PRTAGE: 18-29, 30-44, 45-64, 65+; topcoded 80 and 85 remain 65+",
            "sex": "PESEX: 1 male; 2 female; source records sex, not gender identity",
            "race_ethnicity": "PEHSPNON=1 Hispanic any race. Otherwise PTDTRACE: 1 White alone, 2 Black alone, 4 Asian alone, all remaining codes nh_other (including multiracial).",
            "education": "PEEDUCA 31-39 hs_or_less; 40-42 some_college_or_associate; 43-46 bachelors_or_higher",
        },
        "margins": margins,
        "limitations": [
            "These are weighted CPS survey estimates, not exact population counts; small categories have sampling error.",
            "Citizen adults are a proxy for voting eligibility. CPS excludes institutional residents and this civilian filter excludes Armed Forces; it does not identify every legal disqualification.",
            "The marginal category boundaries are demonstration choices rather than a universal polling standard.",
            "Do not treat marginal targets as a known joint demographic distribution.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Wrote {args.output} from {kept} California citizen-adult CPS records")


if __name__ == "__main__":
    main()
