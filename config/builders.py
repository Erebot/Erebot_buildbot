# -*- coding: utf-8 -*-
from buildbot.config import BuilderConfig
from Erebot_buildbot.config import steps
from Erebot_buildbot.src.factory import MultiProjectBuildFactory

BUILDERS = [
    BuilderConfig(
        name='Tests - Debian 6 - PHP 5.2',
        slavenames=['Debian 6 - PHP 5.2'],
        factory=steps.TESTS,
        category='Tests',
    ),
    BuilderConfig(
        name='Tests - Debian 6 - PHP 5.3',
        slavenames=['Debian 6 - PHP 5.3'],
        factory=steps.TESTS,
        category='Tests',
    ),
    BuilderConfig(
        name='Tests - Debian 6 - PHP 5.4',
        slavenames=['Debian 6 - PHP 5.4'],
        factory=steps.TESTS,
        category='Tests',
    ),
    BuilderConfig(
        name='Tests - WinXP - PHP 5.3',
        slavenames=['WinXP - PHP 5.3'],
        factory=steps.TESTS,
        category='Tests',
    ),
    BuilderConfig(
        name='API documentation',
        slavenames=[
            'Debian 6 - PHP 5.2',
            'Debian 6 - PHP 5.3',
        ],
        factory=steps.DOC,
        category='API',
    ),
    BuilderConfig(
        name='Packaging',
        slavenames=['Debian 6 - PHP 5.3'],
        factory=steps.PACKAGE,
        category='Packaging',
    ),
    BuilderConfig(
        name='Quality Assurance',
        slavenames=['Debian 6 - PHP 5.3'],
        factory=steps.QA,
        category='QA',
    ),
    BuilderConfig(
        name='Live',
        slavenames=['Debian 6 - PHP 5.3'],
        factory=MultiProjectBuildFactory({
            'Erebot': steps.LIVE,
            'www.erebot.net': steps.LIVE_WWW,
        }),
        category='Live',
    ),
]

