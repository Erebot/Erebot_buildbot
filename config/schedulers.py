# -*- coding: utf-8 -*-

from buildbot.schedulers import basic, timed

SCHEDULERS = [
    # Triggered on every commit by the github hook.
    basic.Scheduler(
        name="Regular",
        treeStableTimer=60,
        builderNames=[
            'Tests PHP 5.2',
            'Tests PHP 5.3',
            'Packaging',
        ],
    ),

    # There's no need to build the API documentation on every commit.
    # Also, the QA tools need not be run on every commit either (this
    # may change later on).
    timed.Nightly(
        name="Nightly",
        branch="master",
        builderNames=[
            'API doc (HTML)',
            'API doc (PDF)',
            'lint',
            'CodeSniffer',
        ],
        # Run the builders twice a day, at 3:30 am/pm,
        # if and only if some change occurred since the last run.
        hour=[3, 15],
        minute=30,
        onlyIfChanged=True,
    ),

    # @TODO: add another Nightly scheduler for Windows (every week).
]

