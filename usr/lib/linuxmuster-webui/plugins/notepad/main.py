from jadi import component

from wu.plugins.core.api.sidebar import SidebarItemProvider


@component(SidebarItemProvider)
class ItemProvider(SidebarItemProvider):
    def __init__(self, context):
        pass

    def provide(self):
        return [
            {
                'attach': 'category:tools',
                'name': _('Notepad'),
                'icon': 'pencil',
                'url': '/view/notepad',
                'children': [
                ]
            }
        ]
