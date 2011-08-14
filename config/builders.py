# -*- coding: utf-8 -*-
from buildbot.config import BuilderConfig
from Erebot_buildbot.config import steps

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
        name='Tests - WinXP - PHP 5.3',
        slavenames=['WinXP - PHP 5.3'],
        factory=steps.TESTS,
        category='Tests',
    ),
    BuilderConfig(
        name='API doc - HTML',
        slavenames=[
            'Debian 6 - PHP 5.2',
            'Debian 6 - PHP 5.3',
        ],
        factory=steps.HTML_DOC,
        category='API',
    ),
    BuilderConfig(
        name='API doc - PDF',
        slavenames=[
            'Debian 6 - PHP 5.2',
            'Debian 6 - PHP 5.3',
        ],
        factory=steps.PDF_DOC,
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
]

