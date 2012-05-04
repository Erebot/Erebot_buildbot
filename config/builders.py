# -*- coding: utf-8 -*-
from buildbot.config import BuilderConfig
from buildbot import locks
from Erebot_buildbot.config import steps
from Erebot_buildbot.src.factory import MultiProjectBuildFactory
import secrets

vm_lock = locks.MasterLock("VM")

BUILDERS = [
    # The "Tests" builder triggers the different "Tests - *" schedulers
    # that require a VM to work properly.
    # Those in turn trigger a build on the various "Tests - *" builders.
    BuilderConfig(
        name='Tests',
        slavenames=['Debian 6'],
        factory=steps.VM_TESTS,
        category='Tests',
    )
] + [
    BuilderConfig(
        name='Tests - %s' % buildslave,
        slavenames=[buildslave],
        factory=steps.TESTS,
        category='Tests',
        locks=(
            [vm_lock.access("exclusive")]
            if secrets.BUILDSLAVES[buildslave].get("vm")
            else []
        ),
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

