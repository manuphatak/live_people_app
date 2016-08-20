# coding=utf-8
import json

from channels.generic.websockets import WebsocketDemultiplexer
from django.core.serializers import serialize
from django.db.models import QuerySet


class Consumer(object):
    stream = NotImplemented
    actions = ()

    @classmethod
    def encode(cls, stream, payload):
        raise NotImplementedError()

    @classmethod
    def consumer(cls, message, **kwargs):
        from django.contrib.auth.models import AnonymousUser

        # INBOUND
        self = cls()
        self.message = message
        self.kwargs = kwargs
        self.user = getattr(self.message, "user", AnonymousUser())
        self.action, self.pk, self.data = self.deserialize(self.message)
        self.data = self.run_action(self.action, self.pk)

        if not self.data: return self

        # OUTBOUND
        self.payload = self.serialize(self.data)

        if self.payload == {}: return self

        assert self.stream is not None
        message = cls.encode(self.stream, self.payload)
        self.send(message)
        return self

    def serialize(self, message):
        raise NotImplementedError()

    def deserialize(self, message):
        raise NotImplementedError()

    def run_action(self, action, pk):
        if action not in self.actions:
            raise ValueError('Bad action. Action must be white listed.  action=%s' % action)

        if not self.has_permission(self.user, action, pk):
            return

        method = getattr(self, action)
        return method()

    def has_permission(self, user, action, pk):
        raise NotImplementedError()

    def send(self, message):
        raise NotImplementedError()


class ReplyChannelConsumer(Consumer):
    model = NotImplemented

    @classmethod
    def encode(cls, stream, payload):
        return WebsocketDemultiplexer.encode(stream, payload)

    @classmethod
    def serialize_data(cls, instance, fields):
        fields = None if fields == ['__all__'] else fields
        if isinstance(instance, QuerySet):
            data = serialize('json', instance, fields=fields)
            return json.loads(data)

        data = serialize('json', [instance], fields=fields)
        return json.loads(data)[0]['fields']

    @property
    def queryset(self):
        return self.model.objects.all()

    @property
    def model_label(self):
        return "%s.%s" % (
            self.model._meta.app_label.lower(),
            self.model._meta.object_name.lower(),
        )

    def serialize(self, data):
        payload = {
            "action": self.action,
            "data": self.serialize_data(data, self.fields),
            "model": self.model_label,
        }
        if self.pk is not None:
            payload['pk'] = self.pk
        return payload

    def deserialize(self, message):
        """
        You must hook this up behind a Deserializer, so we expect the JSON
        already dealt with.
        """
        action = message['action']
        pk = message.get('pk', None)
        data = message.get('data', None)
        return action, pk, data

    def send(self, message):
        self.message.reply_channel.send(message)
