import json

from django.core.management.base import BaseCommand

from wedding.views import _serialize_board


class Command(BaseCommand):
    help = 'Write a JSON backup of the complete wedding board to stdout.'

    def handle(self, *args, **options):
        self.stdout.write(json.dumps(_serialize_board(), ensure_ascii=False, indent=2))
