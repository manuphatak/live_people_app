# coding=utf-8
from channels.binding.websockets import WebsocketBinding
from channels.generic.websockets import WebsocketDemultiplexer

from .models import Person
from ..utils.consumers import ReplyChannelConsumer


class AppDemultiplexer(WebsocketDemultiplexer):
    mapping = {
        'Person': 'binding.Person',
        'Sync': 'consumer.Sync',
    }

    def connection_groups(self, **kwargs):
        return ['App']

    def connect(self, message, **kwargs):
        self.send('Hello', 'world')


class PersonBinding(WebsocketBinding):
    stream = 'Person'
    model = Person
    fields = ['first_name', 'last_name', 'dob', 'zip', 'created']

    def group_names(self, instance, action):
        return ['App']

    def has_permission(self, user, action, pk):
        return True


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
