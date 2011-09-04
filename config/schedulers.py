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
            'Tests - WinXP - PHP 5.3',
            'Packaging',
            'Quality Assurance',
            'API documentation',
        ],
    ),
]

