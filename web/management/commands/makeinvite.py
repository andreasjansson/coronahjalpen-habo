from django.core.management.base import BaseCommand, CommandError
from ...models import Invite


class Command(BaseCommand):
    help = "Make a new invite"

    def handle(self, *args, **options):
        invite = Invite.objects.create()
        print(invite.get_absolute_url())
