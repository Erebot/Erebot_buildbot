# -*- coding: utf-8 -*-

from buildbot.status.web.auth import BasicAuth
from buildbot.status.web.authz import Authz
import secrets

auth = BasicAuth(secrets.WEB_USERS)
_policy = 'auth'
AUTHZ = Authz(
    auth=auth,
    forceBuild=_policy,
    forceAllBuilds=_policy,
    pingBuilder=_policy,
    gracefulShutdown=_policy,
    stopBuild=_policy,
    stopAllBuilds=_policy,
    cancelPendingBuild=_policy,
    stopChange=_policy,
    cleanShutdown=_policy,
    showUsersPage=_policy,
)

