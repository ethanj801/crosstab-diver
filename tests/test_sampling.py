import unittest
from scripts.sample_ces import preference


class PreferenceRoutingTests(unittest.TestCase):
    def test_reported_vote_takes_precedence_when_both_items_are_present(self):
        self.assertEqual(preference({"CC20_364a": "1", "CC20_364b": "5"}),
                         ("trump", "reported_early_vote", "CC20_364a"))
        self.assertEqual(preference({"CC20_364a": "2", "CC20_364b": "2"}),
                         ("biden", "reported_early_vote", "CC20_364a"))

    def test_not_yet_voted_routes_to_preference(self):
        self.assertEqual(preference({"CC20_364a": "5", "CC20_364b": "2"}),
                         ("biden", "pre_election_preference", "CC20_364b"))


if __name__ == "__main__":
    unittest.main()
