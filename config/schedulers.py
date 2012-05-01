# -*- coding: utf-8 -*-

from buildbot.schedulers import timed
from buildbot.schedulers.filter import ChangeFilter
from Erebot_buildbot.config import misc, builders

try:
    from buildbot.schedulers.basic import SingleBranchScheduler
except:
    from buildbot.schedulers.basic import Scheduler as SingleBranchScheduler

try:
    from buildbot.schedulers.forcesched import ForceScheduler
except ImportError:
    ForceScheduler = None

def _exclude_gh_pages(branch):
    """
    Returns C{True} if the C{branch} to be built
    is not "gh-pages" which serves a special role.
    """
    return branch != 'gh-pages'

def _exclude_if_only_doc(change):
    """
    Returns C{True} if the C{change} contains
    modifications to something other than the
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
    SingleBranchScheduler(
        name="Tests",
        treeStableTimer=3 * 60,
        builderNames=[
            'Tests - Debian 6',
            'Tests - WinXP',
        ],
        change_filter=ChangeFilter(
            project=[
                p for p in misc.COMPONENTS if
                    p.startswith('Erebot/Erebot_Module_') or
                    p in (
                        'Erebot/Erebot',
                        'Erebot/Plop',
                        'fpoirotte/XRL',
                    )
            ],
            branch_fn=_exclude_gh_pages,
            filter_fn=_exclude_if_only_doc,
        ),
    ),

    # Builds the doc for Erebot (core), modules & PLOP.
    # Not triggered for GitHub Pages.
    SingleBranchScheduler(
        name="Documentation",
        treeStableTimer=3 * 60,
        builderNames=[
            'Documentation',
        ],
        change_filter=ChangeFilter(
            project=[
                p for p in misc.COMPONENTS if
                    p.startswith('Erebot/Erebot_Module_') or
                    p in (
                        'Erebot/Erebot',
                        'Erebot/Plop',
                        'fpoirotte/XRL',
                    )
            ],
            branch_fn=_exclude_gh_pages,
        ),
    ),

    # Runs for Erebot (core), modules, PLOP & Erebot_API
    # Not triggered for GitHub Pages or if the changeset
    # only deals with the documentation.
    SingleBranchScheduler(
        name="Common",
        treeStableTimer=3 * 60,
        builderNames=[
            'Packaging',
            'Quality Assurance',
        ],
        change_filter=ChangeFilter(
            project=[
                p for p in misc.COMPONENTS if
                    p.startswith('Erebot/Erebot_Module_') or
                    p in (
                        'Erebot/Erebot',
                        'Erebot/Plop',
                        'Erebot/Erebot_API',
                        'fpoirotte/XRL',
                    )
            ],
            branch_fn=_exclude_gh_pages,
            filter_fn=_exclude_if_only_doc,
        ),
    ),

    # This scheduler only executes for the Erebot project
    # and updates the Live instance of the bot.
    # Not triggered for GitHub Pages or if the changeset
    # only deals with the documentation.
    SingleBranchScheduler(
        name="Live",
        treeStableTimer=10 * 60,
        builderNames=[
            'Live',
        ],
        change_filter=ChangeFilter(
            project=[
                'Erebot/Erebot',
                'Erebot/www.erebot.net',
            ],
            branch_fn=_exclude_gh_pages,
            filter_fn=_exclude_if_only_doc,
        ),
    ),
]

if ForceScheduler:
    from buildbot.schedulers.forcesched import (
        FixedParameter,
        ChoiceStringParameter,
        BaseParameter,
        StringParameter,
    )
    SCHEDULERS.append(ForceScheduler(
        name="force",
        branch=FixedParameter(name="branch", default="master"),
        repository=BaseParameter(None),
        project=ChoiceStringParameter(
            name="project", choices=list(misc.COMPONENTS)),
        reason=StringParameter(name="reason", default="Forced build", size=50),
        revision=StringParameter(name="revision", size=45),
        properties=[],
        builderNames=[b.name for b in builders.BUILDERS],
    ))

