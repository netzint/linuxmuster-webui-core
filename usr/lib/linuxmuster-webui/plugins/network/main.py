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
                'id': 'network',
                'name': _('Network'),
                'icon': 'fas fa-plug',
                'url': '/view/network',
                'children': [],
            }
        ]


@component(PermissionProvider)
class Permissions(PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'network:configure',
                'name': _('Configure network interfaces'),
                'default': True,
            },
            {
                'id': 'network:updown',
                'name': _('Activate/deactivate network interfaces'),
                'default': True,
            },
        ]
