# -*- coding: utf-8 -*-

from buildbot.status import words
from zope.interface import implements
from twisted.python import log, failure
from twisted.application import internet

from buildbot.interfaces import IStatusReceiver
from buildbot.status import base

# twisted.internet.ssl requires PyOpenSSL, so be resilient if it's missing
try:
    from twisted.internet import ssl
    have_ssl = True
except ImportError:
    have_ssl = False

class IRCContact(words.IRCContact):
    implements(IStatusReceiver)

    def send(self, message):
        self.channel.msgOrNotice(self.dest, message.encode("utf-8", "replace"))

    def act(self, action):
        self.channel.me(self.dest, action.encode("utf-8", "replace"))


class IrcStatusBot(words.IrcStatusBot):
    """I represent the buildbot to an IRC server.
    """
    implements(words.IChannel)
    contactClass = IRCContact

class IrcStatusFactory(words.IrcStatusFactory):
    protocol = IrcStatusBot

class IRC(words.IRC):
    implements(IStatusReceiver)
    """I am an IRC bot which can be queried for status information. I
    connect to a single IRC server and am known by a single nickname on that
    server, however I can join multiple channels."""

    in_test_harness = False

    compare_attrs = ["host", "port", "nick", "password",
                     "channels", "allowForce", "useSSL",
                     "categories"]

    def __init__(self, host, nick, channels, port=6667, allowForce=True,
                 categories=None, password=None, notify_events={},
                 noticeOnChannel = False, showBlameList = True,
                 useSSL=False):
        base.StatusReceiverMultiService.__init__(self)

        assert allowForce in (True, False) # TODO: implement others

        # need to stash these so we can detect changes later
        self.host = host
        self.port = port
        self.nick = nick
        self.channels = channels
        self.password = password
        self.allowForce = allowForce
        self.categories = categories
        self.notify_events = notify_events
        log.msg('Notify events %s' % notify_events)
        self.f = IrcStatusFactory(self.nick, self.password,
                                  self.channels, self.categories, self.notify_events,
                                  noticeOnChannel = noticeOnChannel,
                                  showBlameList = showBlameList)
        # don't set up an actual ClientContextFactory if we're running tests.
        if self.in_test_harness:
            return

        if useSSL:
            # SSL client needs a ClientContextFactory for some SSL mumbo-jumbo
            if not have_ssl:
                raise RuntimeError("useSSL requires PyOpenSSL")
            cf = ssl.ClientContextFactory()
            c = internet.SSLClient(self.host, self.port, self.f, cf)
        else:
            c = internet.TCPClient(self.host, self.port, self.f)

        c.setServiceParent(self)


