from jadi import component
from wu.auth import PermissionProvider
from wu.plugins.core.api.sidebar import SidebarItemProvider


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        self.context = context

    def provide(self):
        return [
            {
                'attach': 'category:system',
                'id': 'power',
                'name': _('Power'),
                'icon': 'bolt',
                'url': '/view/power',
                'children': [],
            }
        ]


@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'power:manage',
                'name': _('Shutdown and reboot the system'),
                'default': True,
            },
        ]
