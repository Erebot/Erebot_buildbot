# -*- encoding: utf-8 -*-

from buildbot.status.web.baseweb import WebStatus as OrigWebStatus
from Erebot_buildbot.src.components import ComponentsResource
from Erebot_buildbot.src.change_hook import CallableChangeHookResource

class WebStatus(OrigWebStatus):
    def __init__(self, *args, **kwargs):
        try:
            change_hook_dialects = args.pop(17)
        except IndexError:
            change_hook_dialects = None
        if 'change_hook_dialects' in kwargs:
            if change_hook_dialects is not None:
                raise Exception("change_hook_dialects passed "
                                "in both args and kwargs")
            change_hook_dialects = kwargs.pop('change_hook_dialects')
        super(WebStatus, self).__init__(*args, **kwargs)
        if change_hook_dialects:
            self.change_hook_dialects = change_hook_dialects
            # Override the usual ChangeHookResource
            # so that callables can be used directly.
            self.putChild("change_hook", CallableChangeHookResource(
                dialects = self.change_hook_dialects))

    def setupUsualPages(self, *args, **kwars):
        super(WebStatus, self).setupUsualPages(*args, **kwargs)
        self.putChild("components", ComponentsResource())

