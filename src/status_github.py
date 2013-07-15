# -*- encoding: utf-8 -*-

from twisted.internet import defer, reactor

from buildbot.status.base import StatusReceiverService
from buildbot.status.results import (
    Results,
    SUCCESS,
    WARNINGS,
    FAILURE,
    SKIPPED,
    EXCEPTION,
    RETRY,
)
from Erebot_buildbot.src.github_hook import gh_api

class GithubStatus(StatusReceiverService):
    api_base = "https://api.github.com"

    def __init__(self, token):
        self._token = token

    @defer.inlineCallbacks
    def _get_last_change(self, bs):
        sssid = bs.bsdict['sourcestampsetid']
        ss = yield bs.master.db.sourcestamps.getSourceStamps(sssid)
        when = None
        last_ch = None
        for sourcestamp in ss:
            change = yield bs.master.db.changes.getChange(
                            sourcestamp['changeids'])
            if when is None or change['when_timestamp'] >= when:
                when = change['when_timestamp']
                last_ch = change
        defer.returnValue(last_ch)

    @defer.inlineCallbacks
    def _submitted(self, bss):
        last_ch = yield self._get_last_change(bss)
        gh_api(
            "%s/repos/%s/statuses/%s" % (
                self.api_base,
                last_ch['project'],
                last_ch['revision'],
            ),
            self._token,
            {
                "state": "pending",
                "target_url": "%scomponents?revision=%d" % (
                    misc.BUILDBOT_URL,
                    last_ch['revision'],
                ),
                "description": "Buildbot is processing the change...",
            }
        )
        def finished(buildset):
            return reactor.callLater(0.1, self._finished, buildset)
        bss.waitUntilFinished(finished)

    @defer.inlineCallbacks
    def _finished(self, bss):
        last_ch = yield self._get_last_change(bss)
        states = {
            SUCCESS: 'success',
            WARNINGS: 'success',
            FAILURE: 'failure',
        }
        desc = "%s: %s" % (Results[bss.getResults()], bss.getReason())

        gh_api(
            "%s/repos/%s/statuses/%s" % (
                self.api_base,
                last_ch['project'],
                last_ch['revision'],
            ),
            self._token,
            {
                "state": states.get(bss.getResults(), 'error'),
                "target_url": "%scomponents?revision=%d" % (
                    misc.BUILDBOT_URL,
                    last_ch['revision'],
                ),
                "description": desc,
            }
        )

    def buildsetSubmitted(self, buildset):
        reactor.callLater(0.1, self._submitted, buildset)

