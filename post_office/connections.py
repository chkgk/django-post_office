from threading import local

from django.core.mail import get_connection

from .settings import get_backend

from .logutils import setup_loghandlers
logger = setup_loghandlers("INFO")


# Copied from Django 1.8's django.core.cache.CacheHandler
class ConnectionHandler:
    """
    A Cache Handler to manage access to Cache instances.

    Ensures only one instance of each alias exists per thread.
    """
    def __init__(self):
        self._connections = local()

    def __getitem__(self, alias):
        try:
            return self._connections.connections[alias]
        except AttributeError:
            logger.info('connections does not exist, alias %s' % alias)
            self._connections.connections = {}
        except KeyError:
            logger.info('alias %s does not exist' % alias)
            pass

        try:
            backend = get_backend(alias)
        except KeyError:
            raise KeyError('%s is not a valid backend alias' % alias)

        connection = get_connection(backend)
        connection.open()
        self._connections.connections[alias] = connection
        logger.info("delivering a new connection")
        return connection

    def all(self):
        return getattr(self._connections, 'connections', {}).values()

    def close(self):
        logger.info('closing all connections')
        for connection in self.all():
            connection.close()


connections = ConnectionHandler()
