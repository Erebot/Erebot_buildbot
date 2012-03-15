# -*- coding: utf-8 -*-
from buildbot.config import BuilderConfig
from Erebot_buildbot.config import steps
from Erebot_buildbot.src.factory import MultiProjectBuildFactory

BUILDERS = [
    BuilderConfig(
        name='Tests - Debian 6',
        slavenames=['Debian 6'],
        factory=steps.TESTS,
        category='Tests',
    ),
    BuilderConfig(
        name='Tests - WinXP',
        slavenames=['WinXP'],
        factory=steps.TESTS,
        category='Tests',
    ),
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
            'Erebot': steps.LIVE,
            'www.erebot.net': steps.LIVE_WWW,
        }),
        category='Live',
    ),
]

