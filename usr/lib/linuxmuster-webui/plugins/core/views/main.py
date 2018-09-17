import gevent
import json
import logging
import subprocess
from jadi import component

import wu
from wu.api.http import url, HttpPlugin
from wu.plugins import PluginManager, DirectoryPluginProvider

from wu.api.endpoint import endpoint


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url('/')
    @endpoint(page=True, auth=False)
    def handle_root(self, http_context):
        if self.context.identity:
            return http_context.redirect('/view/')
        else:
            return http_context.redirect('/view/login/normal')

    @url('/view/.*')
    @endpoint(page=True, auth=False)
    def handle_view(self, http_context):
        if wu.dev:
            rebuild_all = http_context.env.get('HTTP_CACHE_CONTROL', None) == 'no-cache'

            for provider in wu.plugin_providers:
                if isinstance(provider, DirectoryPluginProvider):
                    logging.debug('Building resources in %s', provider.path)
                    if rebuild_all:
                        cmd = ['webui-dev-multitool', '--rebuild']
                    else:
                        cmd = ['webui-dev-multitool', '--build']
                    p = subprocess.Popen(
                        cmd,
                        cwd=provider.path,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    o, e = p.communicate()
                    if p.returncode != 0:
                        logging.error('Resource compilation failed')
                        logging.error(o + e)

        manager = PluginManager.get(wu.context)
        path = manager.get_content_path('core', 'templates/index.html')
        content = open(path).read() % {
            'prefix': http_context.prefix,
            'plugins': json.dumps(
                dict((manager[n]['info']['name'], manager[n]['info']['title']) for n in manager)
            ),
            'config': json.dumps(wu.config.data),
            'version': wu.version,
            'platform': wu.platform,
            'platformUnmapped': wu.platform_unmapped,
            'bootstrapColor': wu.config.data.get('color', None),
        }
        http_context.add_header('Content-Type', 'text/html')
        http_context.respond_ok()
        return content
