# -*- coding: utf-8 -*-

from buildbot.schedulers import basic, timed

SCHEDULERS = [
    # Triggered on every commit by the github hook.
    basic.Scheduler(
        name="Regular",
        treeStableTimer=3 * 60,
        builderNames=[
            'Tests - Debian 6 - PHP 5.2',
            'Tests - Debian 6 - PHP 5.3',
            'Packaging',
            'Quality Assurance',
            'API documentation',
        ],
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

