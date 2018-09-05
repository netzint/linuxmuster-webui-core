# pyflakes: disable-all
from .api import *
from .managers.centos_manager import *
from .managers.debian_manager import *


def init(plugin_manager):
    import wu
    api.TZManager.any(wu.context)

    from .main import ItemProvider
    from .views import Handler
