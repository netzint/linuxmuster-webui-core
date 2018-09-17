from jadi import component

from wu.plugins.core.api.sidebar import SidebarItemProvider


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        pass

    def provide(self):
        return [
            {
                'attach': 'category:general',
                'name': _('Settings'),
                'icon': 'fas fa-sliders-h',
                'url': '/view/settings',
                'children': [
                ]
            }
        ]
