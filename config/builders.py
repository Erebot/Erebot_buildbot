# -*- coding: utf-8 -*-
from buildbot.config import BuilderConfig
from Erebot_buildbot.config import steps

BUILDERS = [
    BuilderConfig(
        name='debian-php52',
        slavename='Debian 6 - PHP 5.2',
        factory=steps.fact,
    ),
    BuilderConfig(
        name='debian-php53',
        slavename='Debian 6 - PHP 5.3',
        factory=steps.fact,
    ),
]

