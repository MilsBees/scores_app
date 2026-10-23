from django.core.management.base import BaseCommand
from django.db import transaction

from wedding.models import BoardColumn, Card, Subtask
from wedding.texts import UI_TEXT


INITIAL_CARDS = [
    ('S', 'echte trouwdatum fixen'),
    ('E', 'hotels op website'),
    ('E', 'vrijdag idee uitwerken'),
    ('M', 'zondag idee uitwerken'),
    ('M', 'rsvp reminders'),
    ('S', 'dagprogramma uitwerken'),
    ('E', 'boek/idee ceremonie / getuigen'),
    ('E', 'gastenboek'),
    ('M', "foto's QR code"),
    ('E', 'programma op website incl. vrijdag & zondag'),
    ('E', 'aankleding ceremonie buiten'),
    ('E', 'aankleding diner'),
    ('E', 'aankleding borrel'),
    ('E', 'aankleding feest'),
    ('M', 'playlist DJ feest'),
    ('S', 'wedding gift'),
    ('E', 'overnachting voor onszelf'),
    ('M', 'vervoer van ons'),
    ('S', 'menu diner proeven / gerechten'),
    ('S', 'ringen'),
    ('S', 'schoenen / accessoires'),
    ('S', 'geloften schrijven'),
    ('E', 'bruidsboeket'),
    ('S', 'ceremoniemuziek'),
    ('S', 'nog vragen'),
    ('M', 'schaakborden'),
    ('M', 'spel/activiteit bedenken'),
    ('M', 'speeches: wie wil?'),
    ('S', 'tafelindeling / seating'),
]


class Command(BaseCommand):
    help = 'Create the initial wedding board tasks once.'

    @transaction.atomic
    def handle(self, *args, **options):
        for position, name in enumerate(UI_TEXT['column_names']):
            BoardColumn.objects.get_or_create(
                name=name,
                defaults={'position': position},
            )

        if Card.objects.exists():
            self.stdout.write('Wedding cards already exist; seed skipped.')
            return

        todo = BoardColumn.objects.get(name=UI_TEXT['column_names'][0])
        for position, (owner, title) in enumerate(INITIAL_CARDS):
            card = Card.objects.create(
                title=title,
                owner=owner,
                column=todo,
                position=position,
            )
            if title == 'wedding gift':
                Subtask.objects.bulk_create([
                    Subtask(card=card, title='voor ons', position=0),
                    Subtask(card=card, title='voor gasten', position=1),
                ])
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(INITIAL_CARDS)} wedding cards.'))
