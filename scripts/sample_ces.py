#!/usr/bin/env python3
"""Draw an equal-weight demo sample from the weighted California CES 2020 pool."""

import argparse
import collections
import csv
import hashlib
import json
import math
from pathlib import Path
import random
import sys


ROOT = Path(__file__).resolve().parents[1]
MISSING = {"", "NA"}
DIMENSIONS = ("age_group", "sex", "race_ethnicity", "education", "presidential_preference")
EARLY_VOTE = {"1": "trump", "2": "biden", "3": "other", "4": "not_sure", "5": "did_not_vote"}
PREFERENCE = {"1": "trump", "2": "biden", "3": "other", "4": "will_not_vote", "5": "not_sure"}
MAJOR_PARTY = {"trump", "biden"}
EXCLUDED_PREFERENCE = {
    "other": "other_candidate_preference",
    "not_sure": "undecided_presidential_preference",
    "will_not_vote": "intends_not_to_vote",
    "no_presidential_vote_reported_at_interview": "no_presidential_vote_at_interview",
    "missing": "missing_presidential_preference",
}
REQUIRED = {"caseid", "inputstate", "cit1", "birthyr", "gender", "race", "hispanic", "educ", "commonweight", "CC20_364a", "CC20_364b"}


def positive_int(value):
    value = int(value)
    if value < 1:
        raise argparse.ArgumentTypeError("sample size must be a positive integer")
    return value


def preference(row):
    """Prefer the pre-election preference item when it was asked.

    The 364a item is asked of people who reported already voting.  Its code 5
    cannot establish eventual election-day nonvoting: it is a response during
    the pre-election field period, and the questionnaire routes those cases to
    364b for a preference.
    """
    early, intended = row["CC20_364a"], row["CC20_364b"]
    if early not in MISSING and early not in EARLY_VOTE:
        raise ValueError(f"Unexpected CC20_364a code: {early}")
    if intended not in MISSING and intended not in PREFERENCE:
        raise ValueError(f"Unexpected CC20_364b code: {intended}")
    if early not in MISSING and early != "5":
        if intended not in MISSING:
            raise ValueError("Unexpected conflicting early-vote/preference routing")
        return EARLY_VOTE[early], "reported_early_vote", "CC20_364a"
    if intended not in MISSING:
        return PREFERENCE[intended], "pre_election_preference", "CC20_364b"
    if early == "5":
        return "no_presidential_vote_reported_at_interview", "reported_no_presidential_vote_at_interview", "CC20_364a"
    return "missing", "missing", None


def load_pool(source):
    pool, exclusions = [], collections.Counter()
    seen = set()
    with source.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        missing_columns = REQUIRED - set(reader.fieldnames or [])
        if missing_columns:
            raise ValueError(f"Missing columns: {sorted(missing_columns)}")
        for row in reader:
            if row["inputstate"] != "6":
                continue
            if row["cit1"] != "1":
                exclusions["noncitizen" if row["cit1"] == "2" else "citizenship_unknown"] += 1
                continue
            age = 2020 - int(row["birthyr"])
            if age < 18:
                exclusions["under_18_by_year_of_birth"] += 1
                continue
            weight = float(row["commonweight"])
            if not math.isfinite(weight) or weight <= 0:
                raise ValueError("Citizen adult has a nonpositive or nonfinite commonweight")
            race, hispanic = row["race"], row["hispanic"]
            if race == "3" or hispanic == "1":
                race_ethnicity = "hispanic"
            elif hispanic == "2":
                if race not in {"1", "2", "4", "5", "6", "7", "8"}:
                    raise ValueError(f"Unexpected race code: {race}")
                race_ethnicity = {"1": "nh_white", "2": "nh_black", "4": "nh_asian"}.get(race, "nh_other")
            else:
                exclusions["hispanic_origin_unknown"] += 1
                continue
            if row["gender"] not in {"1", "2"} or row["educ"] not in {"1", "2", "3", "4", "5", "6"}:
                raise ValueError("Unexpected gender or education code")
            if row["caseid"] in seen:
                raise ValueError("Duplicate CES source caseid")
            seen.add(row["caseid"])
            vote, vote_kind, vote_question = preference(row)
            if vote not in MAJOR_PARTY:
                exclusions[EXCLUDED_PREFERENCE[vote]] += 1
                continue
            pool.append({
                "source_caseid": row["caseid"], "state_fips": "06", "citizen": True,
                "age_2020": age,
                "age_group": "18-29" if age < 30 else "30-44" if age < 45 else "45-64" if age < 65 else "65+",
                "sex": "male" if row["gender"] == "1" else "female",
                "race_ethnicity": race_ethnicity,
                "education": "hs_or_less" if int(row["educ"]) <= 2 else "some_college_or_associate" if int(row["educ"]) <= 4 else "bachelors_or_higher",
                "presidential_preference": vote, "presidential_response_kind": vote_kind,
                "presidential_source_question": vote_question,
                "source_codes": {key: row[key] for key in ("gender", "race", "hispanic", "educ", "CC20_364a", "CC20_364b")},
                "ces_commonweight": weight,
            })
    if not pool:
        raise ValueError("No eligible California source respondents")
    return sorted(pool, key=lambda person: person["source_caseid"]), exclusions


def margins(rows, weighted):
    total = sum(row["ces_commonweight"] if weighted else 1 for row in rows)
    result = {}
    for dimension in DIMENSIONS:
        counts = collections.defaultdict(float)
        for row in rows:
            counts[row[dimension]] += row["ces_commonweight"] if weighted else 1
        result[dimension] = {key: value / total for key, value in sorted(counts.items())}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path.home() / "Downloads/dataverse_files/CES20_Common_OUTPUT_vv.csv")
    parser.add_argument("--size", type=positive_int, default=600)
    parser.add_argument("--seed", type=int, default=2020)
    parser.add_argument("--output", type=Path, help="default: data/california-2020/sample_<size>.json")
    args = parser.parse_args()
    try:
        pool, exclusions = load_pool(args.input)
        weights = [row["ces_commonweight"] for row in pool]
        total_weight = sum(weights)
        draws = random.Random(args.seed).choices(pool, weights=weights, k=args.size)
        sample = [{"id": f"ca2020-{i + 1:06d}", **row, "draw_probability": row["ces_commonweight"] / total_weight, "base_weight": 1.0} for i, row in enumerate(draws)]
        result = {
            "schema_version": 1, "sample_size": args.size, "seed": args.seed,
            "population": "California citizen adults aged 18+ who named Trump or Biden; proxy for voting eligibility, not an eligibility determination",
            "election": "2020 US presidential election",
            "outcome": "Pre-election Trump or Biden preference, with reported early votes where available",
            "preference_restriction": "The pool keeps only Trump and Biden responses. Another candidate, undecided, an intention not to vote, and missing responses are removed before sampling and counted in source_exclusions.",
            "source_file": args.input.name, "source_sha256": hashlib.file_digest(args.input.open("rb"), "sha256").hexdigest(),
            "source_dataset_doi": "10.7910/DVN/E9N6PH",
            "source_weight": "commonweight", "source_pool_size": len(pool),
            "source_exclusions": dict(sorted(exclusions.items())),
            "sampling_method": "Independent draws with replacement, probability proportional to commonweight, from caseid-sorted source pool",
            "unique_source_respondents": len({row["source_caseid"] for row in sample}),
            "duplicate_draws": len(sample) - len({row["source_caseid"] for row in sample}),
            "respondent_identity_note": "These are 600 resampled demo records, not 600 unique CES respondents; repeated source_caseid values retain distinct demo IDs.",
            "weight_usage": "Sampling already uses CES weights. Each draw starts with base_weight=1; ces_commonweight is provenance, not a second analysis weight.",
            "source_weighted_margins": margins(pool, True), "sample_unweighted_margins": margins(sample, False),
            "respondents": sample,
        }
        output = args.output or ROOT / "data" / "california-2020" / f"sample_{args.size}.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
        print(f"Wrote {len(sample)} draws ({result['unique_source_respondents']} unique CES respondents) from {len(pool)} source respondents to {output}")
    except (OSError, ValueError) as error:
        parser.exit(1, f"error: {error}\n")


if __name__ == "__main__":
    main()
