"""Yamb scoresheet scoring and validation rules (as currently implemented)."""
from django.test import TestCase

from yamb.forms import YambScoresheetForm

from .factories import COMPLETE_SHEET, COMPLETE_SHEET_FINAL_SCORE, make_player


class YambScoresheetRuleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.player = make_player("Anna")

    def form(self, **overrides):
        return YambScoresheetForm(data={"player": self.player.pk, **COMPLETE_SHEET, **overrides})

    def cleaned(self, **overrides):
        form = self.form(**overrides)
        self.assertTrue(form.is_valid(), form.errors)
        return form.cleaned_data

    def test_complete_sheet_totals(self):
        data = self.cleaned()
        self.assertEqual(
            [data[f"row_{r}_total"] for r in ["1", "2", "3", "4", "5", "6", "h", "l", "fh", "c", "s", "p"]],
            [0, 20, 0, -40, 0, 120, 106, 30, 120, 120, 80, 100],
        )
        self.assertEqual(data["final_score"], COMPLETE_SHEET_FINAL_SCORE)

    def test_number_rows_score_relative_to_twelve(self):
        # Row N total = (sum of the four cells - 12) * N * 10
        data = self.cleaned(row_3_down=5, row_3_up=5, row_3_l=5, row_3_s=5)
        self.assertEqual(data["row_3_total"], (20 - 12) * 30)
        data = self.cleaned(row_6_down=0, row_6_up=0, row_6_l=0, row_6_s=0)
        self.assertEqual(data["row_6_total"], -12 * 60)

    def test_h_gets_30_bonus_per_column_where_h_plus_l_reaches_50(self):
        data = self.cleaned(row_h_down=30, row_l_down=20)  # 50 -> bonus
        self.assertEqual(data["row_h_total"], 30 + 27 + 26 + 25 + 30)
        data = self.cleaned(row_h_down=29, row_l_down=20)  # 49 -> no bonus
        self.assertEqual(data["row_h_total"], 29 + 27 + 26 + 25)

    def test_totals_wait_until_row_is_complete(self):
        data = self.cleaned(row_1_s=None, row_l_up=None)
        self.assertIsNone(data["row_1_total"])
        self.assertIsNone(data["row_h_total"])  # H and L are only totalled together
        self.assertIsNone(data["row_l_total"])
        self.assertIsNone(data["final_score"])

    def test_both_h_and_l_zero_is_allowed(self):
        self.cleaned(row_h_down=0, row_l_down=0)

    def test_invalid_values_are_rejected(self):
        cases = {
            "row 1 above 5": {"row_1_down": 6},
            "row 6 negative": {"row_6_s": -1},
            "row H above 30": {"row_h_up": 31},
            "H not greater than L": {"row_h_l": 8, "row_l_l": 8},
            "FH not 0 or 40": {"row_fh_down": 20},
            "C not 0 or 60": {"row_c_up": 30},
            "S not 0 or 80": {"row_s_l": 40},
            "P not 0 or 100": {"row_p_s": 50},
            "not a whole number": {"row_2_down": "abc"},
        }
        for label, overrides in cases.items():
            with self.subTest(label):
                self.assertFalse(self.form(**overrides).is_valid())

    def test_player_required_when_sheet_has_data(self):
        form = YambScoresheetForm(data={"player": "", **COMPLETE_SHEET})
        self.assertFalse(form.is_valid())
        self.assertIn("player", form.errors)
