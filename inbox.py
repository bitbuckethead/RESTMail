# -*- coding: utf-8 -*-

import argparse

import gevent
import gevent.monkey

from logbook import Logger

gevent.monkey.patch_select()

import smtpd
import asyncore


log = Logger(__name__)


class InboxServer(smtpd.SMTPServer, object):
    """Logging-enabled SMTPServer instance with handler support."""

    def __init__(self, handler, *args, **kwargs):
        super(InboxServer, self).__init__(*args, **kwargs)
        self._handler = handler

    def process_message(self, peer, mailfrom, rcpttos, data):
        #log.info('Collating message from {0}'.format(mailfrom))
        #log.debug(dict(to=rcpttos, sender=mailfrom, body=data))
        return self._handler(to=rcpttos, sender=mailfrom, body=data)


class Inbox(object):
    """A simple SMTP Inbox."""

    def __init__(self, port=None, address=None):
        self.port = port
        self.address = address
        self.collator = None

    def collate(self, collator):
        """Function decorator. Used to specify inbox handler."""
        self.collator = collator
        return collator

    def serve(self, port=None, address=None):
        """Serves the SMTP server on the given port and address."""
        port = port or self.port
        address = address or self.address

        log.info('Starting SMTP server at {0}:{1}'.format(address, port))

        server = InboxServer(self.collator, (address, port), None)

        try:
            asyncore.loop()
        except KeyboardInterrupt:
            log.info('Cleaning up')

    def dispatch(self):
        """Command-line dispatch."""
        parser = argparse.ArgumentParser(description='Run an Inbox server.')

        parser.add_argument('addr', metavar='addr', type=str, help='addr to bind to')
        parser.add_argument('port', metavar='port', type=int, help='port to bind to')

        args = parser.parse_args()

        self.serve(port=args.port, address=args.addr)
