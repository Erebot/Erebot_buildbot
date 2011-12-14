# -*- coding: utf-8 -*-

from buildbot.schedulers import basic, timed
from buildbot.schedulers.filter import ChangeFilter
from Erebot_buildbot.config import misc

def _exclude_gh_pages(branch):
    """
    Returns C{True} if the C{branch} to be built
    is not "gh-pages" which serves a special role.
    """
    return branch != 'gh-pages'

def _exclude_if_only_doc(change):
    """
    Returns C{True} if the C{change} contains
    modifications to something else than the
    documentation.
    """
    for f in change.files:
        if not f.startswith(u'docs/'):
            return True
    return False

SCHEDULERS = [
    # Runs the tests for Erebot (core), modules & PLOP.
    # Not triggered for GitHub Pages or if the changeset
    # only deals with the documentation.
    basic.Scheduler(
        name="Tests",
        treeStableTimer=3 * 60,
        builderNames=[
            'Tests - Debian 6 - PHP 5.2',
            'Tests - Debian 6 - PHP 5.3',
            'Tests - Debian 6 - PHP 5.4',
            'Tests - WinXP - PHP 5.3',
        ],
        change_filter=ChangeFilter(
            project=[
                p for p in misc.COMPONENTS if
                    p.startswith('Erebot_Module_') or
                    p in ('Erebot', 'Plop')
            ],
            branch_fn=_exclude_gh_pages,
            filter_fn=_exclude_if_only_doc,
        ),
    ),

    # Builds the doc for Erebot (core), modules & PLOP.
    # Not triggered for GitHub Pages.
    basic.Scheduler(
        name="Documentation",
        treeStableTimer=3 * 60,
        builderNames=[
            'Documentation',
        ],
        change_filter=ChangeFilter(
            project=[
                p for p in misc.COMPONENTS if
                    p.startswith('Erebot_Module_') or
                    p in ('Erebot', 'Plop')
            ],
            branch_fn=_exclude_gh_pages,
        ),
    ),

    # Runs for Erebot (core), modules, PLOP & Erebot_API
    # Not triggered for GitHub Pages or if the changeset
    # only deals with the documentation.
    basic.Scheduler(
        name="Common",
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
            branch_fn=_exclude_gh_pages,
            filter_fn=_exclude_if_only_doc,
        ),
    ),

    # This scheduler only executes for the Erebot project
    # and updates the Live instance of the bot.
    # Not triggered for GitHub Pages or if the changeset
    # only deals with the documentation.
    basic.Scheduler(
        name="Live",
        treeStableTimer=10 * 60,
        builderNames=[
            'Live',
        ],
        change_filter=ChangeFilter(
            project=['Erebot', 'www.erebot.net'],
            branch_fn=_exclude_gh_pages,
            filter_fn=_exclude_if_only_doc,
        ),
    ),
]

