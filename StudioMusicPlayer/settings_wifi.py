
from StudioMusicPlayer.settings import *

ALLOWED_HOSTS = ['davids-imac.local', '192.168.1.247', 'tara-alienware.local', '192.168.1.171', 'localhost']

INSTALLED_APPS.insert(0, 'daphne')
INSTALLED_APPS.append('channels')

WIFI_ENABLED = True

# Daphne
ASGI_APPLICATION = "StudioMusicPlayer.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
