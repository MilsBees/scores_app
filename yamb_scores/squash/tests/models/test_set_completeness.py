"""When is a squash set complete?

Tests marked @expectedFailure describe the *correct* behaviour for a known bug
(backlog item squash-003). They show up as "expected failures" in every test run.
When squash-003 is fixed, remove the markers; the tests must then pass.
"""
from unittest import expectedFailure

from django.test import TestCase

from squash.tests.factories import make_match, make_player


class SquashSetCompletenessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.milan = make_player("Milan")
        cls.guus = make_player("Guus")

    def is_incomplete(self, p1, p2, set_type):
        match = make_match(self.milan, self.guus, [(p1, p2)], set_type=set_type)
        return match.sets.get().is_incomplete

    def test_clear_wins_are_complete(self):
        for p1, p2, set_type in [(11, 9, "11"), (5, 11, "11"), (12, 10, "11"), (21, 15, "21"), (23, 21, "21")]:
            with self.subTest(score=f"{p1}-{p2}", set_type=set_type):
                self.assertFalse(self.is_incomplete(p1, p2, set_type))

    def test_nobody_reached_target_is_incomplete(self):
        for p1, p2, set_type in [(8, 5, "11"), (0, 0, "11"), (20, 18, "21"), (15, 12, "21")]:
            with self.subTest(score=f"{p1}-{p2}", set_type=set_type):
                self.assertTrue(self.is_incomplete(p1, p2, set_type))

    def test_winner_is_player_with_more_points(self):
        match = make_match(self.milan, self.guus, [(11, 9), (7, 11)])
        first, second = match.sets.all()
        self.assertEqual(first.winner, self.milan)
        self.assertEqual(second.winner, self.guus)

    @expectedFailure  # Known bug: squash-003 (the 9 August Milan vs Guus set)
    def test_22_22_in_a_21_point_match_is_incomplete(self):
        self.assertTrue(self.is_incomplete(22, 22, "21"))

    @expectedFailure  # Known bug: squash-003. A tie has no winner, so the set can't be complete.
    def test_tie_at_or_above_target_is_incomplete(self):
        self.assertTrue(self.is_incomplete(11, 11, "11"))

    @expectedFailure  # Known bug: squash-003. A manual "incomplete" flag must survive saving.
    def test_manual_incomplete_flag_survives_save(self):
        match = make_match(self.milan, self.guus, [(21, 15)], set_type="21")
        squash_set = match.sets.get()
        squash_set.is_incomplete = True
        squash_set.save()
        squash_set.refresh_from_db()
        self.assertTrue(squash_set.is_incomplete)

    # Not tested yet: "win by 2" cases such as 11-10 or 21-20. squash-003 will
    # confirm the house rules first, then add them here.
