# -*- coding: utf-8 -*-
from buildbot.config import BuilderConfig
from buildbot import locks
from Erebot_buildbot.config import steps, misc
from Erebot_buildbot.src.factory import MultiProjectBuildFactory
import secrets

vm_lock = locks.MasterLock("VM")
qa_lock = locks.SlaveLock("QA", maxCount=2)
doc_lock = locks.SlaveLock("doc", maxCount=2)
packaging_lock = locks.SlaveLock("packaging", maxCount=2)
live_lock = locks.SlaveLock("live", maxCount=1)

BUILDERS = [
    # The "Tests" builder triggers the different "Tests - *" schedulers.
    # Those in turn trigger a build on each "Tests - *" builder.
    BuilderConfig(
        name='Tests',
        slavenames=['Debian (x64)'],
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
        locks=[doc_lock.access("counting")],
    ),

    BuilderConfig(
        name='Packaging',
        slavenames=['Debian (x64)'],
        factory=steps.PACKAGE,
        category='Packaging',
        locks=[packaging_lock.access("counting")],
    ),

    BuilderConfig(
        name='Quality Assurance',
        slavenames=['Debian (x64)'],
        factory=steps.QA,
        category='QA',
        locks=[qa_lock.access("counting")],
    ),

    BuilderConfig(
        name='I18N',
        slavenames=['Debian (x64)'],
        factory=steps.I18N,
        category='I18N',
    ),

    BuilderConfig(
        name='Live',
        slavenames=['Debian (x64)'],
        factory=MultiProjectBuildFactory({
            'Erebot/Erebot': steps.LIVE,
            'Erebot/www.erebot.net': steps.LIVE_WWW,
        }),
        category='Live',
        locks=[live_lock.access("exclusive")],
    ),
]

