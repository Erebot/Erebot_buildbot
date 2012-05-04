# -*- coding: utf-8 -*-
from buildbot.config import BuilderConfig
from buildbot import locks
from Erebot_buildbot.config import steps
from Erebot_buildbot.src.factory import MultiProjectBuildFactory
import secrets

vm_lock = locks.MasterLock("VM")

BUILDERS = [
    # The "Tests" builder triggers the different "Tests - *" schedulers.
    # Those in turn trigger a build on each "Tests - *" builder.
    BuilderConfig(
        name='Tests',
        slavenames=['Debian 6'],
        factory=steps.VM_TESTS,
        category='Tests',
        # Serialize execution of tests. This aims at reducing
        # the load on both the CPU and RAM on the Debian host.
        locks=[vm_lock.access("exclusive")],
    )
] + [
    # Create a "Tests - *" builder for each distro we support.
    BuilderConfig(
        name='Tests - %s' % buildslave,
        slavenames=[buildslave],
        factory=steps.TESTS,
        category='Tests',
    )
    for buildslave in secrets.BUILDSLAVES
] + [
    BuilderConfig(
        name='Documentation',
        slavenames=['Debian 6'],
        factory=steps.DOC,
        category='API',
    ),
    BuilderConfig(
        name='Packaging',
        slavenames=['Debian 6'],
        factory=steps.PACKAGE,
        category='Packaging',
    ),
    BuilderConfig(
        name='Quality Assurance',
        slavenames=['Debian 6'],
        factory=steps.QA,
        category='QA',
    ),
    BuilderConfig(
        name='Live',
        slavenames=['Debian 6'],
        factory=MultiProjectBuildFactory({
            'Erebot/Erebot': steps.LIVE,
            'Erebot/www.erebot.net': steps.LIVE_WWW,
        }),
        category='Live',
    ),
]

