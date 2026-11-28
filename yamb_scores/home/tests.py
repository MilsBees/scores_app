from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    def test_home_page_links_to_every_game(self):
        response = self.client.get(reverse("home:home"))

        self.assertEqual(response.status_code, 200)
        for url in [reverse("scores:index"), reverse("squash:index"), reverse("sjoelen:index")]:
            with self.subTest(url=url):
                self.assertContains(response, f'href="{url}"')
