from jadi import component

from wu.plugins.core.api.sidebar import SidebarItemProvider
from wu.auth import PermissionProvider

from .api import ServiceManager


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        self.context = context

    def provide(self):
        children = [{
            'attach': 'services',
            'name': mgr.name,
            'icon': 'cog',
            'url': '/view/services/%s' % mgr.id,
            'children': [],
        } for mgr in ServiceManager.all(self.context)]

        return [
            {
                'attach': 'category:software',
                'name': _('Services'),
                'icon': 'cogs',
                'url': '/view/services',
                'children': children
            }
        ]

@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'services:manage',
                'name': _('Manage system services'),
                'default': True,
            },
        ]
