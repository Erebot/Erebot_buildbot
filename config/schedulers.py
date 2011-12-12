# -*- coding: utf-8 -*-

from buildbot.schedulers import basic, timed
from buildbot.schedulers.filter import ChangeFilter
from Erebot_buildbot.config import misc

def exclude_gh_pages(branch):
    return branch != 'gh-pages'

SCHEDULERS = [
    # Triggered on every commit by the github hook.
    # Runs for Erebot (core), modules & PLOP.
    basic.Scheduler(
        name="Extras",
        treeStableTimer=3 * 60,
        builderNames=[
            'Tests - Debian 6 - PHP 5.2',
            'Tests - Debian 6 - PHP 5.3',
            'Tests - Debian 6 - PHP 5.4',
            'Tests - WinXP - PHP 5.3',
            'Documentation',
        ],
        change_filter=ChangeFilter(
            project=[
                p for p in misc.COMPONENTS if
                    p.startswith('Erebot_Module_') or
                    p in ('Erebot', 'Plop')
            ],
            branch_fn=exclude_gh_pages,
        ),
    ),

    # Triggered on every commit by the github hook.
    # Runs for Erebot (core), modules, PLOP & Erebot_API
    basic.Scheduler(
        name="Regular",
        treeStableTimer=3 * 60,
        builderNames=[
            'Packaging',
            'Quality Assurance',
        ],
        change_filter=ChangeFilter(
            project=[
                p for p in misc.COMPONENTS if
                    p.startswith('Erebot_Module_') or
                    p in ('Erebot', 'Plop', 'Erebot_API')
            ],
            branch_fn=exclude_gh_pages,
        ),
    ),

    # This scheduler only executes for the Erebot project
    # and updates the Live instance of the bot.
    basic.Scheduler(
        name="Live",
        treeStableTimer=10 * 60,
        builderNames=[
            'Live',
        ],
        change_filter=ChangeFilter(
            project=['Erebot', 'www.erebot.net'],
            branch_fn=exclude_gh_pages,
        ),
    ),
]

