# coding=utf-8
import logging

from channels.binding.websockets import WebsocketBinding
from channels.generic.websockets import WebsocketDemultiplexer

from .forms import PersonForm
from .models import Person
from ..utils.consumers import ReplyChannelConsumer

logger = logging.getLogger(__name__)


class AppDemultiplexer(WebsocketDemultiplexer):
    mapping = {
        'Person': 'binding.Person',
        'Sync': 'consumer.Sync',
    }

    def connection_groups(self, **kwargs):
        return ['App']


class PersonBinding(WebsocketBinding):
    stream = 'Person'
    model = Person
    fields = ['first_name', 'last_name', 'dob', 'zip', 'created']

    def group_names(self, instance, action):
        return ['App']

    def has_permission(self, user, action, pk):
        return True

    def create(self, data):
        f = PersonForm(data)
        if f.is_valid():
            f.save()
            logger.debug('person created person=%r', f.instance)
        else:
            logger.error('person not created. data invalid data=%s', data)

    def update(self, pk, data):
        instance = self.model.objects.get(pk=pk)
        f = PersonForm(data, instance=instance)
        if f.is_valid():
            f.save()
            logger.debug('person updated person=%r', f.instance)
        else:
            logger.error('person not updated. data invalid data=%s', data)


class SyncConsumer(ReplyChannelConsumer):
    model = Person
    stream = 'Sync'
    fields = ['first_name', 'last_name', 'dob', 'zip', 'created']
    actions = ['details', 'list']

    def has_permission(self, user, action, pk):
        return True

    def details(self):
        return self.queryset.get(pk=self.pk)

    def list(self):
        return self.queryset
