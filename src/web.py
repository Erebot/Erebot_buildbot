# -*- encoding: utf-8 -*-

from buildbot.status.web.base import HtmlResource

def authUser(self, request):
    return request.site.buildbot_service.authUser(request)
HtmlResource.authUser = authUser

import os
from twisted.python import log
from buildbot.status.web.baseweb import WebStatus as OrigWebStatus
from buildbot.status.web.feeds import Rss20StatusResource, \
     Atom10StatusResource

class WebStatus(OrigWebStatus):
    def setupSite(self):
        OrigWebStatus.setupSite(self)
        # This replaces the usual "Welcome" page with the waterfall,
        # meaning it will be available at both at "/" and "/waterfall",
        # but it's not that big of a deal really.
#        self.site.resource.putChild('', self.childrenToBeAdded['waterfall'])

    def authUser(self, request):
        """Check that user/passwd is a valid user/pass tuple and can should be
        allowed to perform the action. If this WebStatus is not password
        protected, this function returns False."""
        if not self.isUsingUserPasswd():
            return False
        if self.auth.authenticate(request):
            return True
#        log.msg("Authentication failed: %s" % self.auth.errmsg())
        return False


