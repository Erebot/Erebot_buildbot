# -*- coding: utf-8 -*-

from buildbot.status import words
from Erebot_buildbot.config import auth, misc
from Erebot_buildbot.src import github_hook, status
import secrets

STATUS = []
STATUS.append(status.WebStatus(
    http_port='tcp:8010:interface=127.0.0.1',
    authz=auth.AUTHZ,

    revlink=dict(zip(
        misc.COMPONENTS,
        [
            "%s/%s/commit/%%s" % (misc.GITHUB_BASE, c)
            for c in misc.COMPONENTS
        ]
    )),

    # @TODO: use a callable instead, to add other links (eg. "sha:1234567").
    changecommentlink=dict(zip(
        misc.COMPONENTS,
        [(
            r"#(\d+)",
            "%s/%s/issues/\\1" % (misc.GITHUB_BASE, c),
            r"Issue \g<0>"
        ) for c in misc.COMPONENTS]
    )),

    projects=dict(zip(
        misc.COMPONENTS,
        [
            "%s/%s/wiki" % (misc.GITHUB_BASE, c)
            for c in misc.COMPONENTS
        ]
    )),

    repositories=dict(zip(
        misc.COMPONENTS,
        [
            "%s/%s/commits/master" % (misc.GITHUB_BASE, c)
            for c in misc.COMPONENTS
        ]
    )),

    change_hook_dialects={
        'erebot_github': github_hook.GithubChangeHook({
            'user': 'fpoirotte',
            'key': secrets.GITHUB_KEY,
        }),
    },
))

#STATUS.append(words.IRC(
#    host="irc.iiens.net",
#    nick="Ere-build-bot",
#    channels=["#Erebot"],
#    notify_events=['started', 'failure', 'exception', 'finished', 'success'],
#))

