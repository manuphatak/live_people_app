# coding=utf-8
import json
import logging

from channels import Group
from channels.binding.websockets import WebsocketBinding, WebsocketDemultiplexer

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

    @classmethod
    def broadcast(cls, action, data):
        self = cls()
        if action not in self.actions:
            raise ValueError('Invalid Action.  Whitelisted actions=%s' % self.actions)
        self.action = action
        self.pk = None
        self.data = data
        self.payload = self.serialize(self.data)

        assert self.stream is not None
        message = cls.encode(self.stream, self.payload)
        self.group_send(message)

    def group_names(self, action):
        return ['App']

    def group_send(self, message):
        for group_name in self.group_names(self.action):
            group = Group(group_name)
            group.send(message)


def send_notification(action, html, timeout=60):
    message = {
        'stream': 'Notification',
        'payload': {
            'action': action,
            'data': {
                'html': html,
                'timeout': timeout
            },
        },
    }
    Group('App').send({'text': json.dumps(message)})
