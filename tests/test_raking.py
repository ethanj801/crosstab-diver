import json
import math
import unittest
from pathlib import Path
from scripts.prepare_demo import prepare, rake

DATA = Path(__file__).resolve().parents[1] / "data"


class RakingTests(unittest.TestCase):
    def test_one_margin_has_known_weights(self):
        weights, _ = rake([{"sex": "a"}, {"sex": "a"}, {"sex": "a"}, {"sex": "b"}],
                          {"sex": {"a": 0.5, "b": 0.5}})
        for value, expected in zip(weights, [2 / 3, 2 / 3, 2 / 3, 2]):
            self.assertAlmostEqual(value, expected)

    def test_actual_samples_match_targets_and_preserve_outcomes(self):
        for state in ("georgia",):
            with self.subTest(state=state):
                folder = DATA / f"{state}-2020"
                sample = json.loads((folder / "sample_600.json").read_text())
                targets = json.loads((folder / "raking_targets_cps_nov2020.json").read_text())
                demo = prepare(sample, targets)
                records = demo["respondents"]
                self.assertEqual(len(records), len(sample["respondents"]))
                self.assertEqual([r["preference"] for r in records],
                                 ["D" if r["presidential_preference"] == "biden" else "R"
                                  for r in sample["respondents"]])
                self.assertEqual(len({r["id"] for r in records}), len(records))
                total = sum(r["weight"] for r in records)
                self.assertAlmostEqual(total, len(records))
                self.assertTrue(all(math.isfinite(r["weight"]) and r["weight"] > 0 for r in records))
                for dim, cats in targets["margins"].items():
                    for cat, target in cats.items():
                        actual = sum(r["weight"] for r in records if r[dim] == cat) / total
                        self.assertLessEqual(abs(actual - target["proportion"]), 1e-8)
                for record in sample["respondents"]:
                    record["presidential_preference"] = "trump"
                self.assertEqual([r["weight"] for r in prepare(sample, targets)["respondents"]],
                                 [r["weight"] for r in records])

    def test_preparation_rejects_mixed_states(self):
        sample = json.loads((DATA / "georgia-2020/sample_600.json").read_text())
        targets = json.loads((DATA / "georgia-2020/raking_targets_cps_nov2020.json").read_text())
        targets["filters"]["GESTFIPS"] = 12
        with self.assertRaisesRegex(ValueError, "same state"):
            prepare(sample, targets)

    def test_missing_category_is_reported(self):
        with self.assertRaisesRegex(ValueError, "no records for sex=b"):
            rake([{"sex": "a"}], {"sex": {"a": 0.5, "b": 0.5}})

    def test_incompatible_joint_support_does_not_silently_pass(self):
        with self.assertRaisesRegex(ValueError, "did not converge"):
            rake([{"x": "a", "y": "a"}, {"x": "b", "y": "b"}],
                 {"x": {"a": 0.8, "b": 0.2}, "y": {"a": 0.2, "b": 0.8}},
                 max_iterations=20)


if __name__ == "__main__":
    unittest.main()
