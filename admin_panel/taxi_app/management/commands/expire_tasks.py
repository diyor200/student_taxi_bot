from django.core.management.base import BaseCommand
from datetime import datetime
from ...models import Direction

class Command(BaseCommand):
    help = 'Expire tasks that are past due'

    def handle(self, *args, **kwargs):
        expired_count = Direction.objects.filter(
            created_at__lt=datetime.now(), status=1
        ).update(status=3)
        self.stdout.write(
            self.style.SUCCESS(f'{expired_count} tasks marked as expired')
        )
