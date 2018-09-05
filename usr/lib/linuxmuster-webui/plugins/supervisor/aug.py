import wu
from jadi import component
from wu.plugins.augeas.api import AugeasEndpoint, Augeas
from wu.util import platform_select
from wu.plugins import PluginManager


@component(AugeasEndpoint)
class SupervisorEndpoint(AugeasEndpoint):
    id = 'supervisor'
    path = platform_select(
        debian='/etc/supervisor/supervisord.conf',
        default='/etc/supervisor.conf',
    )

    def get_augeas(self):
        return Augeas(
            modules=[{
                'name': 'Supervisor',
                'lens': 'Supervisor.lns',
                'incl': [
                    self.path,
                ]
            }],
            loadpath=PluginManager.get(wu.context).get_content_path('supervisor', ''),
        )

    def get_root_path(self):
        return '/files' + self.path
