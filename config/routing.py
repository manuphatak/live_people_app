# coding=utf-8
from channels import route, route_class

from live_people_app.people.consumers import AppDemultiplexer, PersonBinding, SyncConsumer

channel_routing = [
    route_class(AppDemultiplexer),
    route('binding.Person', PersonBinding.consumer),
    route('consumer.Sync', SyncConsumer.consumer),
]
