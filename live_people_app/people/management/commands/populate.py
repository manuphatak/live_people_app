import logging

from django.core.management.base import BaseCommand
from django.db.models.signals import post_save, post_delete
from factory.django import mute_signals

from ...consumers import SyncConsumer, send_notification
from ...factories import PersonFactory
from ...models import Person

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Populate DB with a bunch of fake data"

    def handle(self, *args, **options):
        with mute_signals(post_save, post_delete):
            logger.info('Destroying all people')
            Person.objects.all().delete()
            logger.info('Creating 20 people')
            people = PersonFactory.create_batch(20)

        logger.info('Pushing new people to connected clients')
        SyncConsumer.broadcast('list', people)

        send_notification(
            'info',
            ('<strong>Database Reset!</strong>'
             ' Your data is updated automatically!'
             ' Database intentionally wiped every few minutes.')
        )
