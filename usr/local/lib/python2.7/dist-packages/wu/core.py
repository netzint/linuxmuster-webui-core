from __future__ import unicode_literals

import locale
import logging
import os
import psutil
import signal
import socket
import sys
import syslog
from jadi import Context
from six.moves import reload_module

import wu
import wu.plugins
from wu.auth import AuthenticationService
from wu.http import HttpRoot, HttpMiddlewareAggregator
from wu.gate.middleware import GateMiddleware
from wu.plugins import PluginManager
from wu.util.sslsocket import SSLSocket
from wu.wsgi import RequestHandler

import gevent
import gevent.ssl
from gevent import monkey
from OpenSSL import SSL, crypto

# Gevent monkeypatch ---------------------
monkey.patch_all(select=True, thread=True, aggressive=False, subprocess=True)

from gevent.event import Event
import threading
threading.Event = Event
# ----------------------------------------

import wu.compat

from socketio.server import SocketIOServer


def run(config=None, plugin_providers=None, product_name='webui', dev_mode=False,
        debug_mode=False, autologin=False):
    """
    A global entry point for Webui.

    :param config: config file implementation instance to use
    :type  config: :class:`wu.config.BaseConfig`
    :param plugin_providers: list of plugin providers to load plugins from
    :type  plugin_providers: list(:class:`wu.plugins.PluginProvider`)
    :param str product_name: a product name to use
    :param bool dev_mode: enables dev mode (automatic resource recompilation)
    :param bool debug_mode: enables debug mode (verbose and extra logging)
    :param bool autologin: disables authentication and logs everyone in as the user running the panel. This is EXTREMELY INSECURE.
    """
    if config is None:
        raise TypeError('`config` can\'t be None')

    reload_module(sys)
    if hasattr(sys, 'setdefaultencoding'):
        sys.setdefaultencoding('utf8')

    wu.product = product_name
    wu.debug = debug_mode
    wu.dev = dev_mode
    wu.dev_autologin = autologin

    wu.init()
    wu.log.set_log_params(tag='master', master_pid=os.getpid())
    wu.context = Context()
    wu.config = config
    wu.plugin_providers = plugin_providers or []
    logging.info('Loading config from %s', wu.config)
    wu.config.load()
    wu.config.ensure_structure()

    if wu.debug:
        logging.warn('Debug mode')
    if wu.dev:
        logging.warn('Dev mode')

    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        logging.warning('Couldn\'t set default locale')

    # install a passthrough gettext replacement since all localization is handled in frontend
    # and _() is here only for string extraction
    __builtins__['_'] = lambda x: x

    logging.info('Webui Core %s', wu.version)
    logging.info('Detected platform: %s / %s', wu.platform, wu.platform_string)

    # Load plugins
    PluginManager.get(wu.context).load_all_from(wu.plugin_providers)
    if len(PluginManager.get(wu.context)) == 0:
        logging.warn('No plugins were loaded!')

    if wu.config.data['bind']['mode'] == 'unix':
        path = wu.config.data['bind']['socket']
        if os.path.exists(path):
            os.unlink(path)
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            listener.bind(path)
        except OSError:
            logging.error('Could not bind to %s', path)
            sys.exit(1)

    if wu.config.data['bind']['mode'] == 'tcp':
        host = wu.config.data['bind']['host']
        port = wu.config.data['bind']['port']
        listener = socket.socket(
            socket.AF_INET6 if ':' in host else socket.AF_INET, socket.SOCK_STREAM
        )
        if wu.platform not in ['freebsd', 'osx']:
            try:
                listener.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 1)
            except socket.error:
                logging.warn('Could not set TCP_CORK')
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        logging.info('Binding to [%s]:%s', host, port)
        try:
            listener.bind((host, port))
        except socket.error as e:
            logging.error('Could not bind: %s', str(e))
            sys.exit(1)

    # Fix stupid socketio bug (it tries to do *args[0][0])
    socket.socket.__getitem__ = lambda x, y: None

    listener.listen(10)

    gateway = GateMiddleware.get(wu.context)
    application = HttpRoot(HttpMiddlewareAggregator([gateway])).dispatch

    wu.server = SocketIOServer(
        listener,
        log=open(os.devnull, 'w'),
        application=application,
        handler_class=RequestHandler,
        policy_server=False,
        transports=[
            str('websocket'),
            str('flashsocket'),
            str('xhr-polling'),
            str('jsonp-polling'),
        ],
    )

    if wu.config.data['ssl']['enable'] and wu.config.data['bind']['mode'] == 'tcp':
        try:
            context = SSL.Context(SSL.TLSv1_2_METHOD)
        except:
            context = SSL.Context(SSL.TLSv1_METHOD)
        context.set_session_id(str(id(context)))
        context.set_options(SSL.OP_NO_SSLv2 | SSL.OP_NO_SSLv3)
        context.set_cipher_list('ALL:!ADH:!EXP:!LOW:!RC2:!3DES:!SEED:!RC4:+HIGH:+MEDIUM')

        certificate = crypto.load_certificate(
            crypto.FILETYPE_PEM,
            open(wu.config.data['ssl']['certificate']).read()
        )
        private_key = crypto.load_privatekey(
            crypto.FILETYPE_PEM,
            open(wu.config.data['ssl']['certificate']).read()
        )

        context.use_certificate(certificate)
        context.use_privatekey(private_key)

        if wu.config.data['ssl']['client_auth']['enable']:
            # todo harden files
            logging.info('Enabling SSL client authentication')
            context.add_client_ca(certificate)
            context.get_cert_store().add_cert(certificate)
            verify_flags = SSL.VERIFY_PEER
            if wu.config.data['ssl']['client_auth']['force']:
                verify_flags |= SSL.VERIFY_FAIL_IF_NO_PEER_CERT
            context.set_verify(verify_flags, AuthenticationService.get(wu.context).client_certificate_callback)
            context.set_verify_depth(0)

        wu.server.ssl_args = {'server_side': True}
        wu.server.wrap_socket = lambda socket, **ssl: SSLSocket(context, socket)
        logging.info('SSL enabled')

    # auth.log
    try:
        syslog.openlog(
            ident=str(wu.product),
            facility=syslog.LOG_AUTH,
        )
    except:
        syslog.openlog(wu.product)

    def cleanup():
        if hasattr(cleanup, 'started'):
            return
        cleanup.started = True
        logging.info('Process %s exiting normally', os.getpid())
        gevent.signal(signal.SIGINT, lambda: None)
        gevent.signal(signal.SIGTERM, lambda: None)
        if wu.master:
            gateway.destroy()

        p = psutil.Process(os.getpid())
        for c in p.children(recursive=True):
            try:
                os.killpg(c.pid, signal.SIGTERM)
                os.killpg(c.pid, signal.SIGKILL)
            except OSError:
                pass

    def signal_handler():
        cleanup()
        sys.exit(0)

    gevent.signal(signal.SIGINT, signal_handler)
    gevent.signal(signal.SIGTERM, signal_handler)

    wu.server.serve_forever()

    if not wu.master:
        # child process, server is stopped, wait until killed
        gevent.wait()

    if hasattr(wu.server, 'restart_marker'):
        logging.warn('Restarting by request')
        cleanup()

        fd = 20  # Close all descriptors. Creepy thing
        while fd > 2:
            try:
                os.close(fd)
                logging.debug('Closed descriptor #%i', fd)
            except OSError:
                pass
            fd -= 1

        logging.warn('Will restart the process now')
        if '-d' in sys.argv:
            sys.argv.remove('-d')
        os.execv(sys.argv[0], sys.argv)
    else:
        if wu.master:
            logging.debug('Server stopped')
            cleanup()
