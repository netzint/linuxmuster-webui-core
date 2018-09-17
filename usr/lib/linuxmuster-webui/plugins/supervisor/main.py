from jadi import component
from wu.plugins.core.api.sidebar import SidebarItemProvider


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        self.context = context

    def provide(self):
        return [
            {
                'attach': 'category:software',
                'id': 'supervisor',
                'name': _('Supervisor'),
                'icon': 'fas fa-play',
                'url': '/view/supervisor',
                'children': [],
            }
        ]
