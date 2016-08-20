# coding=utf-8
import os

import channels.asgi

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
channel_layer = channels.asgi.get_channel_layer()
