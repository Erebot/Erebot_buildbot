# -*- coding: utf-8 -*-

from buildbot.process import factory
from buildbot.process.properties import WithProperties
from buildbot.steps import shell, transfer
from Erebot_buildbot.config.steps import common
from Erebot_buildbot.config.locks import TAGFILES_LOCK
from Erebot_buildbot.config import misc
from Erebot_buildbot.src.steps import Link
from Erebot_buildbot.src import master

DOC = factory.BuildFactory()
DOC.addStep(common.erebot_path)
DOC.addStep(common.clone)

DOC.addStep(master.MasterShellCommand(
    command=" && ".join([
        "rm -f /tmp/tagfiles.tar.gz",
        "mkdir -p public_html/tagfiles/",
        "cd public_html/",
        "tar czvf /tmp/tagfiles.tar.gz tagfiles/",
    ]),
    description=["tar", "tagfiles"],
    descriptionDone=["tar", "tagfiles"],
    locks=[TAGFILES_LOCK.access('exclusive')],
))

DOC.addStep(transfer.FileDownload(
    mastersrc="/tmp/tagfiles.tar.gz",
    slavedest="/tmp/Erebot_tagfiles.tar.gz",
    locks=[TAGFILES_LOCK.access('exclusive')],
))

DOC.addStep(shell.ShellCommand(
    command=" && ".join([
        "cd /tmp/",
        "tar zxvf Erebot_tagfiles.tar.gz",
        "rm -f /tmp/Erebot_tagfiles.tar.gz",
    ]),
    description=["untar", "tagfiles"],
    descriptionDone=["untar", "tagfiles"],
    locks=[TAGFILES_LOCK.access('exclusive')],
))

DOC.addStep(shell.WarningCountingShellCommand(
    command="phing doc_html -Dtagfiles.reference=-",
    description="HTML doc",
    descriptionDone="HTML doc",
    warningPattern="^(.*?):([0-9]+): [Ww]arning: (.*)$",
    warningExtractor=
        shell.WarningCountingShellCommand.warnExtractFromRegexpGroups,
    warnOnWarnings=True,
    env={
        # Ensures the output doesn't use
        # some locale-specific formatting.
        'LANG': "en_US.UTF-8",
        'PATH': WithProperties("%(EREBOT_PATH)s:${PATH}"),
    },
    maxTime=10*60,
))

DOC.addStep(shell.ShellCommand(
    command="phing doc_pdf",
    description="PDF doc",
    descriptionDone="PDF doc",
    env={
        # Ensures the output doesn't use
        # some locale-specific formatting.
        'LANG': "en_US.UTF-8",
        'PATH': WithProperties("%(EREBOT_PATH)s:${PATH}"),
    },
    maxTime=10*60,
))

DOC.addStep(shell.ShellCommand(
    command=WithProperties(
        "cd docs/ && "
        "ln -sf html %(project)s && "
        "find -L %(project)s "
        "-name '*.html' -print0 -o "
        "-name '*.png' -print0 -o "
        "-name '*.css' -print0 -o "
        "-name '*.js' -print0 | "
        "tar -c -z -v -f %(project)s.tgz --null -T -; "
        "cd -"
    ),
))

DOC.addStep(transfer.FileUpload(
    slavesrc=WithProperties("%(project)s.tagfile"),
    masterdest=WithProperties(
        "public_html/tagfiles/%(project)s.tagfile"
    ),
    maxsize=1 * (1 << 20), # 1 MiB
    locks=[TAGFILES_LOCK.access('exclusive')],
))

DOC.addStep(transfer.FileUpload(
    slavesrc=WithProperties("docs/latex/refman.pdf"),
    masterdest=
        WithProperties("public_html/doc/pdf/%(project)s.pdf"),
    maxsize=20 * (1 << 20), # 20 MiB
))

DOC.addStep(transfer.FileUpload(
    slavesrc=WithProperties("docs/%(project)s.tgz"),
    masterdest=
        WithProperties("public_html/doc/html/%(project)s.tgz"),
    maxsize=50 * (1 << 20), # 50 MiB
))

DOC.addStep(master.MasterShellCommand(
    command=WithProperties(
        "tar -z -x -v -f public_html/doc/html/%(project)s.tgz -C "
            "public_html/doc/html/"
    ),
    description=["untar", "doc"],
    descriptionDone=["untar", "doc"],
))

DOC.addStep(Link(
    label="Code Coverage",
    href=WithProperties(
        "%(buildbotURL)s/doc/coverage/%(project)s/",
        buildbotURL=lambda _: misc.BUILDBOT_URL.rstrip('/'),
    ),
))

DOC.addStep(Link(
    label="Online doc",
    href=WithProperties(
        "%(buildbotURL)s/doc/html/%(project)s/",
        buildbotURL=lambda _: misc.BUILDBOT_URL.rstrip('/'),
    ),
))

DOC.addStep(Link(
    label="Tarball doc",
    href=WithProperties(
        "%(buildbotURL)s/doc/html/%(project)s.tgz",
        buildbotURL=lambda _: misc.BUILDBOT_URL.rstrip('/'),
    ),
))

DOC.addStep(Link(
    label="PDF doc",
    href=WithProperties(
        "%(buildbotURL)s/doc/pdf/%(project)s.pdf",
        buildbotURL=lambda _: misc.BUILDBOT_URL.rstrip('/'),
    ),
))

