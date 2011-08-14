# -*- coding: utf-8 -*-

from buildbot.schedulers import basic, timed

SCHEDULERS = [
    # Triggered on every commit by the github hook.
    basic.Scheduler(
        name="Regular",
        treeStableTimer=60,
        builderNames=[
            'Tests - Debian 6 - PHP 5.2',
            'Tests - Debian 6 - PHP 5.3',
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
            'API doc - HTML',
            'API doc - PDF',
            'Quality Assurance',
        ],
        # Run the builders twice a day, at 3:30 am/pm,
        # if and only if some change occurred since the last run.
        hour=[3, 15],
        minute=30,
        onlyIfChanged=True,
    ),

    # It costs more to run the tests on Windows,
    # so we run the tests on it less often.
    timed.Nightly(
        name="Windows",
        branch="master",
        builderNames=[
            'Tests - WinXP - PHP 5.3',
        ],
        # Run the tests once a week on Mondays, at 5:00am.
        hour=5,
        minute=0,
        dayOfWeek=0,
        onlyIfChanged=True,
    ),
]

