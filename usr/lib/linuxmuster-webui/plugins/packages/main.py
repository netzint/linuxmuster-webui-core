from jadi import component

from wu.auth import PermissionProvider
from wu.plugins.core.api.sidebar import SidebarItemProvider
from .api import PackageManager


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        self.context = context

    def provide(self):
        children = [{
            'attach': 'packages',
            'name': mgr.name,
            'icon': 'fas fa-box',
            'url': '/view/packages/%s' % mgr.id,
            'children': [],
        } for mgr in PackageManager.all(self.context)]
        return [
            {
                'attach': 'category:system',
                'id': 'packages',
                'name': _('Packages'),
                'icon': 'fas fa-box',
                'url': '/view/packages/%s' % PackageManager.all(self.context, ignore_exceptions=True)[0].id,
                'children': children,
            }
        ]


@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'packages:install',
                'name': _('Install/remove packages'),
                'default': True,
            },
        ]
