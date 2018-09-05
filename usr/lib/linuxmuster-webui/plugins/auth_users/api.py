import logging
import os
import scrypt
from jadi import component

import wu
from wu.auth import AuthenticationProvider


@component(AuthenticationProvider)
class UsersAuthenticationProvider(AuthenticationProvider):
    id = 'users'
    name = _('Custom users')

    def __init__(self, context):
        self.context = context
        wu.config.data['auth'].setdefault('users', {})

    def get_salt(self):
        return os.urandom(256)

    def hash_password(self, password, salt=None):
        """
        :rtype: str
        """
        password = password.encode('utf-8')
        if not salt:
            salt = self.get_salt()
        return scrypt.encrypt(salt, password, maxtime=1).encode('hex')

    def authenticate(self, username, password):
        self.context.worker.reload_master_config()
        password = password.encode('utf-8')
        if username in wu.config.data['auth']['users']:
            hash = wu.config.data['auth']['users'][username]['password']
            try:
                scrypt.decrypt(hash.decode('hex'), password, maxtime=15)
                return True
            except scrypt.error as e:
                logging.debug('Auth failed: %s' % e)
                return False
        return False

    def authorize(self, username, permission):
        return wu.config.data['auth']['users'].get(username, {}).get('permissions', {}).get(permission['id'], permission['default'])

    def get_isolation_uid(self, username):
        return wu.config.data['auth']['users'][username]['uid']

    def get_profile(self, username):
        if not username:
            return {}
        return wu.config.data['auth']['users'][username]
