"""Correcting a squash match in Django admin stores exactly what was entered."""
from unittest import expectedFailure

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from squash.tests.factories import make_match, make_player


class SquashMatchAdminSaveTests(TestCase):
    def setUp(self):
        admin_user = get_user_model().objects.create_superuser("admin", "admin@example.com", "test-password")
        self.client.force_login(admin_user)
        self.milan = make_player("Milan")
        self.guus = make_player("Guus")
        self.match = make_match(self.milan, self.guus, [(21, 17), (22, 22)], set_type="21")
        self.first_set, self.second_set = self.match.sets.all()

    def admin_post(self, second_set_points=(22, 22), second_set_incomplete=False):
        data = {
            "session": "",
            "player_1": self.milan.pk,
            "player_2": self.guus.pk,
            "date_played": "2026-08-09",
            "set_type": "21",
            "sets-TOTAL_FORMS": "2",
            "sets-INITIAL_FORMS": "2",
            "sets-MIN_NUM_FORMS": "0",
            "sets-MAX_NUM_FORMS": "1000",
            "sets-0-id": self.first_set.pk,
            "sets-0-match": self.match.pk,
            "sets-0-set_number": "1",
            "sets-0-player_1_points": "21",
            "sets-0-player_2_points": "17",
            "sets-1-id": self.second_set.pk,
            "sets-1-match": self.match.pk,
            "sets-1-set_number": "2",
            "sets-1-player_1_points": str(second_set_points[0]),
            "sets-1-player_2_points": str(second_set_points[1]),
            "_save": "Save",
        }
        if second_set_incomplete:
            data["sets-1-is_incomplete"] = "on"
        response = self.client.post(reverse("admin:squash_squashmatch_change", args=[self.match.pk]), data)
        # A 302 means admin accepted the form; a 200 would mean validation errors.
        self.assertEqual(response.status_code, 302)
        self.second_set.refresh_from_db()

    def test_admin_change_page_loads(self):
        response = self.client.get(reverse("admin:squash_squashmatch_change", args=[self.match.pk]))
        self.assertEqual(response.status_code, 200)

    def test_admin_saves_corrected_points(self):
        self.admin_post(second_set_points=(24, 22))
        self.assertEqual((self.second_set.player_1_points, self.second_set.player_2_points), (24, 22))

    @expectedFailure  # Known bug: squash-003 (ticking "is incomplete" in admin is overwritten on save)
    def test_admin_can_mark_set_incomplete(self):
        self.admin_post(second_set_incomplete=True)
        self.assertTrue(self.second_set.is_incomplete)
