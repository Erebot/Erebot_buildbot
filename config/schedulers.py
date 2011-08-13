# -*- coding: utf-8 -*-

from buildbot.schedulers import basic, timed

# Add a scheduler which will trigger the builder above
# whenever the tree for that component changes and then
# stabilizes.
SCHEDULERS = [
    basic.Scheduler(
        name="full",
        treeStableTimer=60,
        builderNames=[
            'debian-php52',
            'debian-php53',
        ],
    ),
]

