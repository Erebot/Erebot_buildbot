# -*- coding: utf-8 -*-

from buildbot.schedulers import basic, timed
from buildbot.schedulers.filter import ChangeFilter

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

    # This scheduler only executes for the Erebot project
    # and updates the Live instance of the bot.
    basic.Scheduler(
        name="Live",
        treeStableTimer=10 * 60,
        builderNames=[
            'Live',
        ],
        change_filter=ChangeFilter(project='Erebot'),
    ),
]

