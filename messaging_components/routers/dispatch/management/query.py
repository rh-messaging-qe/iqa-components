from collections import namedtuple
from typing import NamedTuple

from messaging_abstract.component import Router
from proton import Url, SSLDomain
from proton.utils import BlockingConnection, SyncRequestResponse
import proton
import logging


class RouterQuery(object):
    """
    Provides methods that can be used to query the Dispatch Router.
    Connections are closed after each query.
    """
    def __init__(self, host="0.0.0.0", port=5672, router: Router=None):

        self._logger = logging.getLogger(self.__module__)
        self.port = port
        self.host = host
        self._router = router
        self._connection_options = {
            'sasl_enabled': False,
            'ssl_domain': None,
            'allow_insecure_mechs': True,
            'user': None,
            'password': None
        }

        if self._router:
            # Enable SASL when credentials provided
            self._connection_options['sasl_enabled'] = self._router.has_ssl_keys() or self._router.has_credentials()

            # If SSL certificates provided, use them
            if self._router.has_ssl_keys():
                ssl_domain = SSLDomain(SSLDomain.MODE_CLIENT)
                ssl_domain.set_credentials(self._router.pem_file, self._router.key_file, self._router.key_password)
                self._connection_options['ssl_domain'] = ssl_domain

            # If User and Password provided
            if self._router.has_credentials():
                self._connection_options['user'] = self._router.user
                self._connection_options['password'] = self._router.password

    def query(self, entity_type: str='org.apache.qpid.dispatch.router.node') -> NamedTuple:
        """
        Queries the related router instance, retrieving information for
        the provided Entity Type. The result is an array of a named tuple,
        whose fields are the attribute names returned by the router.
        In example, if querying entity type: org.apache.qpid.dispatch.allocator,
        the results can be accessed as: result.typeName, result.typeSize, ...
        same names returned by the router.
        :param entity_type:
        :return:
        """
        # Scheme to use
        scheme = 'amqp'
        if self._connection_options['ssl_domain']:
            scheme = 'amqps'

        # URL to test
        url = Url("%s://%s:%s/$management" % (scheme, self.host, self.port))
        self._logger.info("Querying router at: %s://%s:%s/$management" % (scheme, self.host, self.port))

        # Proton connection
        self._logger.debug("Connection options: %s" % self._connection_options)
        connection = BlockingConnection(url, **self._connection_options)

        # Proton sync client
        client = SyncRequestResponse(connection, url.path)

        # Request message object
        request = proton.Message()
        request.properties = {u'operation': u'QUERY', u'entityType': u'%s' % entity_type}
        request.body = {u'attributeNames': []}

        # Sending the request
        response = client.call(request)

        # Closing connection
        client.connection.close()

        # Namedtuple that represents the query response from the router
        # so fields can be read based on their attribute names.
        RouterQueryResults = namedtuple('RouterQueryResults', response.body["attributeNames"])
        records = []

        for record in response.body["results"]:
            records.append(RouterQueryResults(*record))

        return records

    # Entities that can be queried
    def listener(self):
        return self.query(entity_type='org.apache.qpid.dispatch.listener')

    def connector(self):
        return self.query(entity_type='org.apache.qpid.dispatch.connector')

    def router(self):
        return self.query(entity_type='org.apache.qpid.dispatch.router')

    def address(self):
        return self.query(entity_type='org.apache.qpid.dispatch.router.address')

    def config_address(self):
        return self.query(entity_type='org.apache.qpid.dispatch.router.config.address')

    def config_autolink(self):
        return self.query(entity_type='org.apache.qpid.dispatch.router.config.autoLink')

    def config_linkroute(self):
        return self.query(entity_type='org.apache.qpid.dispatch.router.config.linkRoute')

    def config_exchange(self):
        return self.query(entity_type='org.apache.qpid.dispatch.router.config.exchange')

    def config_binding(self):
        return self.query(entity_type='org.apache.qpid.dispatch.router.config.binding')

    def node(self):
        return self.query(entity_type='org.apache.qpid.dispatch.router.node')

    def ssl_profile(self):
        return self.query(entity_type='org.apache.qpid.dispatch.sslProfile')

    def connection(self):
        return self.query(entity_type='org.apache.qpid.dispatch.connection')

    def allocator(self):
        return self.query(entity_type='org.apache.qpid.dispatch.allocator')

    def log_stats(self):
        return self.query(entity_type='org.apache.qpid.dispatch.logStats')

    def router_link(self):
        return self.query(entity_type='org.apache.qpid.dispatch.router.link')

    def policy(self):
        return self.query(entity_type='org.apache.qpid.dispatch.policy')

    def vhost(self):
        return self.query(entity_type='org.apache.qpid.dispatch.vhost')

    def vhost_user_group_settings(self):
        return self.query(entity_type='org.apache.qpid.dispatch.vhostUserGroupSettings')

    def vhost_stats(self):
        return self.query(entity_type='org.apache.qpid.dispatch.vhostStats')

    def auth_service_plugin(self):
        return self.query(entity_type='org.apache.qpid.dispatch.authServicePlugin')

    def configuration_entity(self):
        return self.query(entity_type='org.apache.qpid.dispatch.configurationEntity')

    def log(self):
        return self.query(entity_type='org.apache.qpid.dispatch.log')

    def console(self):
        return self.query(entity_type='org.apache.qpid.dispatch.console')

    def management(self):
        return self.query(entity_type='org.apache.qpid.dispatch.management')
