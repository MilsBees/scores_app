"""Every URL in the project must be classified in config/url_registry.py."""
from django.test import SimpleTestCase
from django.urls import URLPattern, URLResolver, get_resolver

from config.url_registry import IGNORED_NAMESPACES, READ_URLS, SEPARATELY_PROTECTED_URLS, WRITE_URLS


def all_url_names(patterns=None, namespace=None):
    names = set()
    for entry in patterns if patterns is not None else get_resolver().url_patterns:
        if isinstance(entry, URLResolver):
            # Use the app namespace (yamb is included as namespace "yamb" but its
            # app_name is "scores", which is what the code reverses with).
            child_namespace = entry.app_name or entry.namespace or namespace
            if child_namespace in IGNORED_NAMESPACES:
                continue
            names |= all_url_names(entry.url_patterns, child_namespace)
        elif isinstance(entry, URLPattern):
            if entry.name is None:
                names.add(f"<unnamed: {entry.pattern}>")
            else:
                names.add(f"{namespace}:{entry.name}" if namespace else entry.name)
    return names


class UrlRegistryTests(SimpleTestCase):
    def test_every_url_is_classified(self):
        classified = READ_URLS | WRITE_URLS | SEPARATELY_PROTECTED_URLS
        unclassified = all_url_names() - classified
        self.assertEqual(
            unclassified,
            set(),
            "New URL(s) found. Add each one to READ_URLS or WRITE_URLS in config/url_registry.py.",
        )

    def test_registry_has_no_stale_entries(self):
        stale = (READ_URLS | WRITE_URLS | SEPARATELY_PROTECTED_URLS) - all_url_names()
        self.assertEqual(stale, set(), "These names in config/url_registry.py no longer exist.")

    def test_no_url_is_in_two_groups(self):
        self.assertFalse(READ_URLS & WRITE_URLS)
        self.assertFalse((READ_URLS | WRITE_URLS) & SEPARATELY_PROTECTED_URLS)

    def test_every_app_has_write_urls_registered(self):
        for namespace in ["scores", "squash", "sjoelen"]:
            with self.subTest(app=namespace):
                self.assertTrue(any(name.startswith(f"{namespace}:") for name in WRITE_URLS))
