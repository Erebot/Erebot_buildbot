# -*- coding: utf-8 -*-
from buildbot.config import BuilderConfig
from Erebot_buildbot.config import steps, misc, locks
from Erebot_buildbot.src.factory import MultiProjectBuildFactory
import secrets

BUILDERS = [
    # The "Tests" builder triggers the different "Tests - *" schedulers.
    # Those in turn trigger a build on each "Tests - *" builder.
    BuilderConfig(
        name='Tests',
        slavenames=['Debian (x64)'],
        factory=steps.VM_TESTS,
        category='Tests',
    )
] + [
    # Create a "Tests - *" builder for each distro we support.
    BuilderConfig(
        name='Tests - %s' % buildslave,
        slavenames=[conf.get('login', buildslave)],
        factory=steps.TESTS,
        category='Tests',
    )
    for buildslave, conf in secrets.BUILDSLAVES.iteritems()
] + [
    BuilderConfig(
        name='Documentation',
        slavenames=['Debian (x64)'],
        factory=steps.DOC,
        category='API',
        locks=[locks.DOC_LOCK.access("counting")],
    ),

    BuilderConfig(
        name='Packaging',
        slavenames=['Debian (x64)'],
        factory=steps.PACKAGE,
        category='Packaging',
        locks=[locks.PACKAGING_LOCK.access("counting")],
    ),

    BuilderConfig(
        name='Quality Assurance',
        slavenames=['Debian (x64)'],
        factory=steps.QA,
        category='QA',
        locks=[locks.QA_LOCK.access("counting")],
    ),

    BuilderConfig(
        name='I18N',
        slavenames=['Debian (x64)'],
        factory=steps.I18N,
        category='I18N',
    ),
]

