# -*- coding: utf-8 -*-

import re
from buildbot.process import factory
from buildbot.process.properties import WithProperties
from buildbot.steps import shell, transfer
from Erebot_buildbot.config.steps import common
from Erebot_buildbot.config.locks import TAGFILES_LOCK
from Erebot_buildbot.config import misc
from Erebot_buildbot.src.steps import Link
from Erebot_buildbot.src import master

DOC = factory.BuildFactory()
DOC.addStep(common.fill_properties)
DOC.addStep(common.erebot_path)
DOC.addStep(common.clone_rw)

DOC.addStep(master.MasterShellCommand(
    command=" && ".join([
        "/bin/rm -f /tmp/tagfiles.tar.gz",
        "/bin/mkdir -p public_html/tagfiles/",
        "cd public_html/",
        "/bin/tar czvf /tmp/tagfiles.tar.gz tagfiles/",
    ]),
    description=["taring", "tagfiles"],
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
        "/bin/tar zxvf Erebot_tagfiles.tar.gz",
        "/bin/rm -f /tmp/Erebot_tagfiles.tar.gz",
    ]),
    description=["untaring", "tagfiles"],
    descriptionDone=["untar", "tagfiles"],
    locks=[TAGFILES_LOCK.access('exclusive')],
))

DOC.addStep(shell.WarningCountingShellCommand(
    command=WithProperties(
        "phing doc_html"
            " -Dtagfiles.reference=-"
            " -Ddoc_release=snapshot%(buildnumber)d"
    ),
    description=["building", "doc"],
    descriptionDone=["build", "doc"],
    warningPattern=re.compile("^(.*?):([0-9]+): Warning: (.*)$", re.I),
    warningExtractor=
        shell.WarningCountingShellCommand.warnExtractFromRegexpGroups,
    warnOnWarnings=True,
    env={
        # Ensures the output doesn't use
        # some locale-specific formatting.
        'LANG': "en_US.UTF-8",
        'PATH': WithProperties("${PHP%(PHP_MAIN)s_PATH}:${PATH}"),
    },
    maxTime=10*60,
))

DOC.addStep(shell.ShellCommand(
    command=WithProperties(
        "cd docs/ && "

        "/bin/ln -sf -T api %(shortProject)s && "
        "echo -e '\\ntgz archive for %(shortProject)s'\"'\"'s API doc' &&"
        "/usr/bin/find -L %(shortProject)s "
            "-name '*.html' -print0 -o "
            "-name '*.png' -print0 -o "
            "-name '*.css' -print0 -o "
            "-name '*.js' -print0 | "
            "/bin/tar -c -h -z -v -f %(shortProject)s-api.tgz --null -T -; "

        "echo -e '\\nzip archive for %(shortProject)s'\"'\"'s API doc' &&"
        "/usr/bin/zip -v -r -n .png:.gif %(shortProject)s-api.zip "
        "   %(shortProject)s/ -i '*.html' -i '*.png' -i '*.css' -i '*.js'; "

        "echo -e '\\ntgz archive for %(shortProject)s'\"'\"'s end-user doc' &&"
        "/bin/ln -sf -T enduser/html %(shortProject)s && "
        "/bin/tar -c -h -z -v -f %(shortProject)s-enduser.tgz %(shortProject)s; "

        "echo -e '\\nzip archive for %(shortProject)s'\"'\"'s end-user doc' &&"
        "/usr/bin/zip -r %(shortProject)s-enduser.zip %(shortProject)s/; "

        "cd -"
    ),
    description=["archiving", "doc"],
    descriptionDone=["archive", "doc"],
))

DOC.addStep(transfer.FileUpload(
    slavesrc=WithProperties("%(shortProject)s.tagfile.xml"),
    masterdest=WithProperties(
        "public_html/tagfiles/%(shortProject)s.tagfile.xml"
    ),
    maxsize=1 * (1 << 20), # 1 MiB
    locks=[TAGFILES_LOCK.access('exclusive')],
))

DOC.addStep(transfer.FileUpload(
    slavesrc=WithProperties("docs/%(shortProject)s-api.tgz"),
    masterdest=
        WithProperties("public_html/doc/api/%(shortProject)s-api.tgz"),
    maxsize=50 * (1 << 20), # 50 MiB
))

DOC.addStep(transfer.FileUpload(
    slavesrc=WithProperties("docs/%(shortProject)s-api.zip"),
    masterdest=
        WithProperties("public_html/doc/api/%(shortProject)s-api.zip"),
    maxsize=50 * (1 << 20), # 50 MiB
))

DOC.addStep(transfer.FileUpload(
    slavesrc=WithProperties("docs/%(shortProject)s-enduser.tgz"),
    masterdest=
        WithProperties("public_html/doc/enduser/%(shortProject)s.tgz"),
    maxsize=50 * (1 << 20), # 50 MiB
))

DOC.addStep(transfer.FileUpload(
    slavesrc=WithProperties("docs/%(shortProject)s-enduser.zip"),
    masterdest=
        WithProperties("public_html/doc/enduser/%(shortProject)s.zip"),
    maxsize=50 * (1 << 20), # 50 MiB
))

DOC.addStep(master.MasterShellCommand(
    command=WithProperties(
        "/bin/tar -z -x -v -f public_html/doc/api/%(shortProject)s-api.tgz "
            "-C public_html/doc/api/; "
    ),
    description=["untaring", "API", "doc"],
    descriptionDone=["untar", "API", "doc"],
))

DOC.addStep(shell.ShellCommand(
    command=WithProperties(
        " && ".join([
            "/bin/mv docs/%(shortProject)s-enduser.tgz ./",
            "/usr/bin/git fetch -t %(rw_repository)s +gh-pages --progress",
            "/usr/bin/git reset --hard FETCH_HEAD",
            "/bin/rm -rf docs/ buildenv/ tests/ vendor/ *.tagfile.xml",
            "/usr/bin/git branch -M gh-pages",
            "/usr/bin/git remote add "
                "-t gh-pages origin %(rw_repository)s",
            "/usr/bin/git rm -rf --ignore-unmatch '*'",
            "/bin/tar -z -x -v --strip-components=1 "
                "-f %(shortProject)s-enduser.tgz",
            "/usr/bin/touch .nojekyll",
            "/bin/rm -f %(shortProject)s-enduser.tgz",
            "(" +
            "; ".join([
                "/usr/bin/git add '*.html'",
                "/usr/bin/git add  '*.js'",
                "/usr/bin/git add  objects.inv",
                "/usr/bin/git add  _static/",
                "/usr/bin/git add  _sources/",
                "/usr/bin/git add  .buildinfo",
                "/usr/bin/git add  .nojekyll",
            ]) +
            "; :)",
            "/usr/bin/git commit -m "
                "'Rebuild end-user doc for "
                "%(got_revision)s [%(buildnumber)d]'",
            "/usr/bin/git push",
        ])
    ),
    description=["pushing", "end-user", "doc"],
    descriptionDone=["push", "end-user", "doc"],
))

DOC.addStep(shell.SetProperty(
    command="/usr/bin/git rev-parse HEAD",
    property="doc_revision"
))

DOC.addStep(Link(
    label="Code Coverage",
    href=WithProperties(
        "%(buildbotURL)s/doc/coverage/%(shortProject)s/",
        buildbotURL=lambda _: misc.BUILDBOT_URL.rstrip('/'),
    ),
))

DOC.addStep(Link(
    label="API doc (tar)",
    href=WithProperties(
        "%(buildbotURL)s/doc/api/%(shortProject)s-api.tgz",
        buildbotURL=lambda _: misc.BUILDBOT_URL.rstrip('/'),
    ),
))

DOC.addStep(Link(
    label="API doc (zip)",
    href=WithProperties(
        "%(buildbotURL)s/doc/api/%(shortProject)s-api.zip",
        buildbotURL=lambda _: misc.BUILDBOT_URL.rstrip('/'),
    ),
))

DOC.addStep(Link(
    label="End-user doc (tar)",
    href=WithProperties(
        "%(buildbotURL)s/doc/enduser/%(shortProject)s.tgz",
        buildbotURL=lambda _: misc.BUILDBOT_URL.rstrip('/'),
    ),
))

DOC.addStep(Link(
    label="End-user doc (zip)",
    href=WithProperties(
        "%(buildbotURL)s/doc/enduser/%(shortProject)s.zip",
        buildbotURL=lambda _: misc.BUILDBOT_URL.rstrip('/'),
    ),
))

DOC.addStep(Link(
    label="API doc (online)",
    href=WithProperties(
        "%(buildbotURL)s/doc/api/%(shortProject)s/",
        buildbotURL=lambda _: misc.BUILDBOT_URL.rstrip('/'),
    ),
))

DOC.addStep(Link(
    label="End-user doc (online)",
    href=WithProperties(
        "http://%(ghUser)s.github.com/%(shortProject)s/"
    ),
))

