from jadi import component

from wu.plugins.core.api.sidebar import SidebarItemProvider


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        self.context = context

    def provide(self):
        return [
            {
                'attach': 'category:general',
                'id': 'auth_users',
                'name': _('Users'),
                'icon': 'fas fa-users',
                'url': '/view/auth-users',
                'children': [],
            }
        ]
