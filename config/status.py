# -*- coding: utf-8 -*-

from Erebot_buildbot.config import auth, misc
from Erebot_buildbot.src import github_hook, status, words
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

    changecommentlink=dict(zip(
        misc.COMPONENTS,

        # Refs to issues for this component.
        [(
            r"(?<![0-9a-zA-Z-])#(\d+)",
            "%s/%s/issues/\\1" % (misc.GITHUB_BASE, c),
            r"Issue \g<0>"
        ) for c in misc.COMPONENTS] +

        # Refs to commits for this component.
        [(
            r"sha:([0-9a-fA-F]{7,40})(?![0-9a-fA-F])",
            "%s/%s/commit/\\1" % (misc.GITHUB_BASE, c),
            r"Commit \g<1>"
        ) for c in misc.COMPONENTS] +

        # Other types of references.
        [
            # Refs to github users.
            (
                r"(?<![0-9a-zA-Z-])@([0-9a-fA-F-]+)",
                "%s/\\1" % misc.GITHUB_BASE,
                r"Github user \g<1>"
            ),

            # Refs to issues in other projects.
            (
                r"([0-9a-zA-Z-]+\/[0-9a-zA-Z_-]+)#(\d+)",
                "%s/\\1/issues/\\2" % misc.GITHUB_BASE,
                r"Issue \g<2> in \g<1>"
            ),

            # Refs to commits in other projects.
            # Eg. "foo/bar@1234567".
            # 7 to 40 hexadecimal digits may be used.
            (
                r"([0-9a-zA-Z-]+\/[0-9a-zA-Z_-]+)@([0-9a-fA-F]{7,40})(?![0-9a-fA-F])",
                "%s/\\1/commit/\\2" % misc.GITHUB_BASE,
                r"Commit \g<2> in \g<1>"
            ),
        ],
    )),

    projects=dict(zip(
        misc.COMPONENTS,
        [
            "%s/%s/" % (misc.GITHUB_BASE, c)
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
            'user': ('Erebot', 'fpoirotte'),
            'key': secrets.GITHUB_KEY,
        }),
    },
))

STATUS.append(words.IRC(
    host="irc.iiens.net",
    nick="Ere-build-bot",
    channels=["#Erebot"],
))

