# -*- coding: utf-8 -*-

from buildbot.status import words
from buildbot.status.html import WebStatus
from Erebot_buildbot.config import auth, misc
import secrets

STATUS = []
STATUS.append(WebStatus(
    http_port='tcp:8010:interface=127.0.0.1',
    authz=auth.AUTHZ,

    revlink=dict(zip(
        misc.components,
        [
            "%s/%s/commit/%%s" % (misc.GITHUB_BASE, c) \
            for c in misc.components
        ]
    )),

    changecommentlink=dict(zip(
        misc.components,
        [(
            r"#(\d+)",
            "%s/%s/issues/\\1" % (misc.GITHUB_BASE, c),
            r"Issue \g<0>"
        ) for c in misc.components]
    )),

    projects=dict(zip(
        misc.components,
        ["%s/%s/wiki" % (misc.GITHUB_BASE, c) for c in misc.components]
    )),

    repositories=dict(zip(
        misc.components,
        [
            "%s/%s/commits/master" % (misc.GITHUB_BASE, c) \
            for c in misc.components
        ]
    )),

    change_hook_dialects={
        'erebot_github': {'user': 'fpoirotte', 'key': secrets.GITHUB_KEY},
    },
))

#STATUS.append(words.IRC(
#    host="irc.iiens.net",
#    nick="Ere-build-bot",
#    channels=["#Erebot"],
#    notify_events=['started', 'failure', 'exception', 'finished', 'success'],
#))

