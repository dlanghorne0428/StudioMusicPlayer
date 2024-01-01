
from StudioMusicPlayer.settings import *

ALLOWED_HOSTS = ['davids-imac.local', 'FXC-Mini-PC.local', 'Studio-Laptop.local', 'tara-alienware.local', 'localhost']
ALLOWED_HOSTS += ['192.168.1.{}'.format(i) for i in range(256)]

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
