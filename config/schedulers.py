# -*- coding: utf-8 -*-

from buildbot.schedulers import timed, triggerable
from buildbot.schedulers.filter import ChangeFilter
from Erebot_buildbot.config import misc, builders
from Erebot_buildbot.src.schedulers import PerProjectAndBranchScheduler
import secrets

try:
    from buildbot.schedulers.forcesched import ForceScheduler
except ImportError:
    ForceScheduler = None

def _exclude_values(branches):
    if not isinstance(branches, (list, set)):
        branches = [branches]
    def _inner(branch):
        """
        Returns C{True} if the C{branch} to be built
        is not one of the excluded branches.
        """
        return (branch not in branches)
    return _inner

def _has_doc_change(change):
    """
    Returns C{True} if the C{change} contains modifications
    that may impact the documentation.

    You may also force a build by adding the text "[buildbot force]"
    anywhere in the commit message.
    """
    if change.comments is not None and "[buildbot force]" in change.comments:
        return True
    for f in change.files:
        # Ignore changes made to translations.
        if f.startswith(u'data/i18n/'):
            continue
        # Ignore changes made to tests.
        if f.startswith(u'tests/'):
            continue
        return True
    return False

def _has_code_change(change):
    """
    Returns C{True} if the C{change} contains modifications
    to to the code (and so, excludes changes to the
    documentation, code examples and translations).

    You may also force a build by adding the text "[buildbot force]"
    anywhere in the commit message.
    """
    if change.comments is not None and "[buildbot force]" in change.comments:
        return True
    for f in change.files:
        # Ignore changes made to the documentation.
        if f.startswith(u'docs/'):
            continue
        # Ignore changes made to code examples.
        if f.startswith(u'examples/'):
            continue
        # Ignore changes made to translations.
        if f.startswith(u'data/i18n/'):
            continue
        return True
    return False


SCHEDULERS = [
    # Main scheduler for the tests, that will trigger
    # a series of tests for each distrob.
    # The tests are run for Erebot (core), modules & PLOP.
    # Not triggered for GitHub Pages or if the changeset
    # only deals with the documentation.
    PerProjectAndBranchScheduler(
        name="Tests",
        treeStableTimer=3 * 60,
        builderNames=['Tests'],
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
            branch_fn=_exclude_values('gh-pages'),
            filter_fn=_has_code_change,
            category_fn=_exclude_values('transifex'),
        ),
    ),
] + [
    # Create triggerable schedulers for tests
    triggerable.Triggerable(
        name="Tests - %s" % buildslave,
        builderNames=["Tests - %s" % buildslave],
    )
    for buildslave in secrets.BUILDSLAVES
] + [
    # Builds the doc for Erebot (core), modules & PLOP.
    # Not triggered for GitHub Pages.
    PerProjectAndBranchScheduler(
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
                        'Erebot/Erebot_API',
                        'Erebot/Plop',
                        'fpoirotte/XRL',
                    )
            ],
            branch_fn=_exclude_values('gh-pages'),
            filter_fn=_has_doc_change,
            category_fn=_exclude_values('transifex'),
        ),
    ),

    # Runs for Erebot (core), modules, PLOP & Erebot_API
    # Not triggered for GitHub Pages or if the changeset
    # only deals with the documentation.
    PerProjectAndBranchScheduler(
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
                        'Erebot/DependencyInjection'
                    )
            ],
            branch_fn=_exclude_values('gh-pages'),
            filter_fn=_has_code_change,
            category_fn=_exclude_values('transifex'),
        ),
    ),

    # This scheduler is triggered by translation updates
    # in Transifex. It is used to push the new translations
    # to the git repository for the appropriate component.
    PerProjectAndBranchScheduler(
        name="I18N",
        treeStableTimer=3 * 60,
        builderNames=['I18N'],
        change_filter=ChangeFilter(
            category=['transifex'],
        ),
    ),

    # This scheduler only executes for the Erebot project
    # and updates the Live instance of the bot.
    # Not triggered for GitHub Pages or if the changeset
    # only deals with the documentation.
    PerProjectAndBranchScheduler(
        name="Live",
        treeStableTimer=10 * 60,
        builderNames=['Live'],
        change_filter=ChangeFilter(
            project=[
                'Erebot/Erebot',
                'Erebot/www.erebot.net',
            ],
            branch_fn=_exclude_values('gh-pages'),
            filter_fn=_has_code_change,
            category_fn=_exclude_values('transifex'),
        ),
    ),
]

if ForceScheduler:
    from buildbot.schedulers import forcesched
    SCHEDULERS.append(ForceScheduler(
        name="Force",
        branch=forcesched.StringParameter(name="branch", default="master"),
        repository=forcesched.BaseParameter(None),
        project=forcesched.ChoiceStringParameter(
            name="project", choices=list(misc.COMPONENTS), required=True),
        reason=forcesched.StringParameter(name="reason", default="Forced build", size=50),
        revision=forcesched.StringParameter(name="revision", size=45),
        properties=[],
        builderNames=[b.name for b in builders.BUILDERS],
    ))

