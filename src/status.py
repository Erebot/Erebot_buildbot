# -*- encoding: utf-8 -*-

from buildbot.status.web.baseweb import WebStatus as OrigWebStatus
from Erebot_buildbot.src.components import ComponentsResource
from Erebot_buildbot.src.change_hook import CallableChangeHookResource
from Erebot_buildbot.src.status_json import JsonStatusResource

class WebStatus(OrigWebStatus):
    def __init__(self, http_port=None, distrib_port=None, allowForce=None,
                 public_html="public_html", site=None, numbuilds=20,
                 num_events=200, num_events_max=None, auth=None,
                 order_console_by_time=False, changecommentlink=None,
                 revlink=None, projects=None, repositories=None,
                 authz=None, logRotateLength=None, maxRotatedFiles=None,
                 change_hook_dialects = None, provide_feeds=None):

        if change_hook_dialects is None:
            change_hook_dialects = {}

        # Call the original initializer without the
        # change_hook_dialects information.
        OrigWebStatus.__init__(self, http_port, distrib_port, allowForce,
                                public_html, site, numbuilds,
                                num_events, num_events_max, auth,
                                order_console_by_time, changecommentlink,
                                revlink, projects, repositories,
                                authz, logRotateLength, maxRotatedFiles,
                                {}, provide_feeds)

        if change_hook_dialects:
            self.change_hook_dialects = change_hook_dialects
            # Override the usual ChangeHookResource
            # so that callables can be used directly.
            self.putChild("change_hook", CallableChangeHookResource(
                dialects = self.change_hook_dialects))

    def setupUsualPages(self, *args, **kwargs):
        OrigWebStatus.setupUsualPages(self, *args, **kwargs)
        self.putChild("components", ComponentsResource())

    def setupSite(self):
        provide_feeds = list(self.provide_feeds)
        try:
            provide_feeds.remove('json')
        except ValueError:
            pass
        OrigWebStatus.setupSite(self)
        if 'json' in self.provide_feeds:
            status = self.getStatus()
            self.site.resource.putChild("json", JsonStatusResource(status))
