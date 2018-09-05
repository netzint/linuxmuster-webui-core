from jadi import component
from wu.plugins.dashboard.api import Widget
from wu.plugins.services.api import ServiceManager


@component(Widget)
class ServiceWidget(Widget):
    id = 'service'
    name = _('Service')
    template = '/services:resources/partial/widget.html'
    config_template = '/services:resources/partial/widget.config.html'

    def __init__(self, context):
        Widget.__init__(self, context)

    def get_value(self, config):
        manager_id = config.get('manager_id', None)
        service_id = config.get('service_id', None)
        if not manager_id or not service_id:
            return None
        for mgr in ServiceManager.all(self.context):
            if mgr.id == manager_id:
                svc = mgr.get_service(service_id)
                return {
                    'id': svc.id,
                    'name': svc.name,
                    'managerId': svc.manager.id,
                    'state': svc.state,
                    'isRunning': svc.running,
                }
