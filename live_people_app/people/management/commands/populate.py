import json
import logging

from channels import Group
from django.core.management.base import BaseCommand

from ...factories import PersonFactory
from ...models import Person

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Populate DB with a bunch of fake data"

    def handle(self, *args, **options):
        logger.info('Destroying all people')
        Person.objects.all().delete()
        logger.info('Creating 20 people')
        PersonFactory.create_batch(20)

        logger.info('Notifying connected clients')
        message = {'stream': 'Management', 'payload': {'data': {}, 'action': 'update'}}
        Group('App').send({'text': json.dumps(message)})
