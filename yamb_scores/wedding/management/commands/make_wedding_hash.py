from getpass import getpass

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Generate a Django password hash for WEDDING_PASSPHRASE_HASH.'

    def handle(self, *args, **options):
        passphrase = getpass('Wedding passphrase: ')
        confirmation = getpass('Repeat passphrase: ')
        if not passphrase:
            raise CommandError('The passphrase cannot be empty.')
        if passphrase != confirmation:
            raise CommandError('The passphrases do not match.')
        self.stdout.write(make_password(passphrase))
