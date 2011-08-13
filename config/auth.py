# -*- coding: utf-8 -*-

from buildbot.status.web.auth import BasicAuth
from buildbot.status.web.authz import Authz
import secrets

auth = BasicAuth(secrets.WEB_USERS)
AUTHZ = Authz(
    auth=auth,
    forceBuild='auth',
    forceAllBuilds='auth',
    pingBuilder='auth',
    gracefulShutdown='auth',
    stopBuild='auth',
    stopAllBuilds='auth',
    cancelPendingBuild='auth',
    stopChange='auth',
    cleanShutdown='auth',
)

