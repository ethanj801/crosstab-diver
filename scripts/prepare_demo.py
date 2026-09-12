#!/usr/bin/env python3
"""Prepare binary demo records and fixed demographic raking weights (stdlib only)."""

import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "california-2020"


def rake(records, targets, *, tolerance=1e-8, max_iterations=1000):
    """IPF over marginal targets, starting from equal weights, normalized to mean 1.

    CES weights already determined sampling probabilities. Applying them again
    here would count them twice. Preference is deliberately never used in IPF.
    No trimming, joint targets, or automatic category merging is performed.
    """
    if not records:
        raise ValueError("Cannot rake an empty sample.")
    if not targets or not 0 < tolerance < 1 or max_iterations < 1:
        raise ValueError("Provide targets, a positive tolerance, and iterations.")
    cells = []
    for dimension, categories in targets.items():
        if not categories or any(not math.isfinite(p) or p <= 0 for p in categories.values()):
            raise ValueError(f"Targets must be finite and positive: {dimension}")
        if not math.isclose(sum(categories.values()), 1, abs_tol=1e-9):
            raise ValueError(f"Targets must sum to one: {dimension}")
        if any(record.get(dimension) not in categories for record in records):
            raise ValueError(f"Sample contains an unmapped category: {dimension}")
        for category, proportion in categories.items():
            indices = [i for i, r in enumerate(records) if r[dimension] == category]
            if not indices:
                raise ValueError(f"Cannot rake: no records for {dimension}={category}. "
                                 "Choose a larger sample or review the sampling/target categories.")
            cells.append((indices, proportion))

    weights = [1.0] * len(records)
    for iteration in range(1, max_iterations + 1):
        for indices, proportion in cells:
            factor = proportion * len(records) / sum(weights[i] for i in indices)
            for i in indices:
                weights[i] *= factor
        if any(not math.isfinite(w) or w <= 0 for w in weights):
            raise ValueError("Raking produced nonpositive or nonfinite weights.")
        total = sum(weights)
        error = max(abs(sum(weights[i] for i in indices) / total - p)
                    for indices, p in cells)
        if error <= tolerance:
            weights = [w * len(records) / total for w in weights]
            return weights, {"iterations": iteration, "max_absolute_margin_error": error,
                             "tolerance": tolerance, "min_weight": min(weights),
                             "max_weight": max(weights), "mean_weight": sum(weights) / len(weights)}
    raise ValueError(f"Raking did not converge after {max_iterations} iterations.")


def prepare(sample, target_data):
    records = sample["respondents"]
    if len({r["id"] for r in records}) != len(records):
        raise ValueError("Demo record IDs must be unique, including repeated source draws.")
    if any(r["presidential_preference"] not in ("biden", "trump") for r in records):
        raise ValueError("The binary demo accepts only source Biden/Trump preferences.")
    targets = {dim: {cat: value["proportion"] for cat, value in cats.items()}
               for dim, cats in target_data["margins"].items()}
    weights, diagnostics = rake(records, targets)
    return {
        "raking": {"method": "iterative proportional fitting", "starting_weight": 1,
                   "normalization": "mean one", "trimming": None,
                   "dimensions": list(targets), **diagnostics},
        "respondents": [
            {"id": r["id"], "number": i + 1, "age": r["age_2020"],
             **{dim: r[dim] for dim in targets},
             "preference": "D" if r["presidential_preference"] == "biden" else "R",
             "weight": weights[i]}
            for i, r in enumerate(records)
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", type=Path, default=DATA / "sample_600.json")
    parser.add_argument("--targets", type=Path, default=DATA / "raking_targets_cps_nov2020.json")
    parser.add_argument("--output", type=Path, default=DATA / "demo.json")
    args = parser.parse_args()
    try:
        sample_bytes, target_bytes = args.sample.read_bytes(), args.targets.read_bytes()
        demo = prepare(json.loads(sample_bytes), json.loads(target_bytes))
        demo["sources"] = {
            "sample": {"file": args.sample.name, "sha256": hashlib.sha256(sample_bytes).hexdigest()},
            "targets": {"file": args.targets.name, "sha256": hashlib.sha256(target_bytes).hexdigest()},
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(demo, indent=2) + "\n")
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"Preparation failed: {error}\n")
    print(f"Prepared {len(demo['respondents'])} records at {args.output}")
    print(json.dumps(demo["raking"], indent=2))


if __name__ == "__main__":
    main()
