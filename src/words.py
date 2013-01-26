# -*- coding: utf-8 -*-

from buildbot.status import words
from buildbot.status.results import SUCCESS
from zope.interface import implements
from twisted.python import log, failure
from twisted.application import internet

from buildbot.interfaces import IStatusReceiver
from buildbot.status import base

try:
    from buildbot.status.words import IChannel
except:
    IChannel = None

try:
    from buildbot.status.words import maybeColorize
except:
    maybeColorize = lambda text, color, useColors: text

# twisted.internet.ssl requires PyOpenSSL, so be resilient if it's missing
try:
    from twisted.internet import ssl
    have_ssl = True
except ImportError:
    have_ssl = False

class IRCContact(words.IRCContact):
    implements(IStatusReceiver)
    muted = False

    def send(self, message):
        if self.muted:
            return
        if hasattr(self, 'channel'): # buildbot < 0.8.6
            self.channel.msgOrNotice(self.dest,
                message.encode("utf-8", "replace"))
        else:
            self.bot.msgOrNotice(self.dest,
                message.encode("utf-8", "replace"))

    def act(self, action):
        if self.muted:
            return
        if hasattr(self, 'channel'): # buildbot < 0.8.6
            self.channel.me(self.dest, action.encode("utf-8", "replace"))
        else:
            self.bot.describe(self.dest, action.encode("utf-8", "replace"))

    def buildStarted(self, builderName, build):
        builder = build.getBuilder()
        log.msg('[Contact] Builder %r in category %s started' % (builder, builder.category))

        # only notify about builders we are interested in

        if (self.bot.categories != None and
           builder.category not in self.bot.categories):
            log.msg('Not notifying for a build in the wrong category')
            return

        if not self.notify_for('started'):
            return

        if self.useRevisions:
            r = "build containing revision(s) [%s] on %s started for %s" % \
                (build.getRevisions(), builder.getName(), build.getProperty('project'))
        else:
            r = "build #%d of %s started for %s, including [%s]" % \
                (build.getNumber(),
                 builder.getName(),
                 build.getProperty('project'),
                 ", ".join([str(c.revision) for c in build.getChanges()])
                 )

        self.send(r)

    def buildFinished(self, builderName, build, results):
        builder = build.getBuilder()

        if (self.bot.categories != None and
            builder.category not in self.bot.categories):
            return

        if not self.notify_for_finished(build):
            return

        builder_name = builder.getName()
        buildnum = build.getNumber()
        buildrevs = build.getRevisions()
        project = build.getProperty('project')

        results = self.getResultsDescriptionAndColor(build.getResults())
        if self.reportBuild(builder_name, buildnum):
            if self.useRevisions:
                r = "build containing revision(s) [%s] on %s for %s is complete: %s" % \
                    (buildrevs, builder_name, project, results[0])
            else:
                r = "build #%d of %s for %s is complete: %s" % \
                    (buildnum, builder_name, project, results[0])

            r += ' [%s]' % maybeColorize(" ".join(build.getText()), results[1], self.useColors)
            buildurl = self.bot.status.getURLForThing(build)
            if buildurl:
                r += "  Build details are at %s" % buildurl

            if self.bot.showBlameList and build.getResults() != SUCCESS and len(build.changes) != 0:
                r += '  blamelist: ' + ', '.join(list(set([c.who for c in build.changes])))

            self.send(r)


class IrcStatusBot(words.IrcStatusBot):
    """I represent the buildbot to an IRC server.
    """
    if IChannel:
        implements(IChannel)
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

    def __init__(self, host, nick, channels, pm_to_nicks=[],
                 port=6667, allowForce=True,
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
        self.pm_to_nicks = pm_to_nicks
        self.password = password
        self.allowForce = allowForce
        self.categories = categories
        self.notify_events = notify_events
        log.msg('Notify events %s' % notify_events)
        try:
            self.f = IrcStatusFactory(self.nick, self.password,
                                      self.channels, self.categories,
                                      self.notify_events,
                                      noticeOnChannel = noticeOnChannel,
                                      showBlameList = showBlameList)
        except TypeError:
            # Newer versions have an additional parameter ()
            self.f = IrcStatusFactory(self.nick, self.password,
                                      self.channels, self.pm_to_nicks,
                                      self.categories, self.notify_events,
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

