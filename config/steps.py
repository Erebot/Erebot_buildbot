# -*- coding: utf-8 -*-

from buildbot.process import factory, properties
from buildbot.steps import source, shell, transfer, master
from Erebot_buildbot.src.steps import Link, PhingPHPUnit

#for component in components:
fact = factory.BuildFactory()

# Complete checkout.
fact.addStep(source.Git(
#        mode='incremental',
#        method='clean',
    mode='copy',
    repourl='%s.git',
    submodules=True,
    progress=True,
#        retryFetch=True,
#        clobberOnFailure=True,
))

#    if name == 'Core':
#        fact.addStep(shell.ShellCommand(
#            command=' && '.join([
#                'cd ..',
#                'mkdir -p pear.erebot.net',
#                'cd pear.erebot.net',
#                'ln -s ../../logging/trunk/data Plop',
#            ]),
#            description="symlink Plop",
#            descriptionDone="symlink Plop",
#        ))
#        fact.addStep(shell.ShellCommand(
#            command=' && '.join([
#                'mkdir -p vendor',
#                'cd vendor',
#                'ln -s /var/local/buildbot/git/dependency-injection/lib dependency-injection',
#            ]),
#            description="symlink DIC",
#            descriptionDone="symlink DIC",
#        ))

#    fact.addStep(shell.Compile(
#        command="phing",
#        env={
#            'LANG': "en_US.UTF-8",
#            'PATH': "/var/local/buildbot/bin/:${PATH}",
#        },
#        warnOnWarnings=True,
#        warnOnFailure=True,
#        warningPattern="^\\[i18nStats\\] (.*?):([0-9]+): [Ww]arning: (.*)$",
#        warningExtractor=
#            shell.WarningCountingShellCommand.warnExtractFromRegexpGroups,
#        maxTime=10*60,
#    ))

#    fact.addStep(shell.ShellCommand(
#        command=properties.WithProperties(
#        """
#        for f in `ls -1 RELEASE-*`;
#        do
#            mv -v ${f} ${f}snapshot%(got_revision)s;
#        done
#        """
#        ),
#        description=["prepare", "build"],
#        descriptionDone=["prepare", "build"],
#    ))

#    fact.addStep(transfer.FileDownload(
#        mastersrc='/home/qa/master/buildenv/sign',
#        slavedest='/tmp/buildbot.sign',
#        mode=0600,
#    ))

#    fact.addStep(transfer.FileDownload(
#        mastersrc='/home/qa/master/buildenv/certificate.p12',
#        slavedest='/tmp/buildbot.p12',
#        mode=0600,
#    ))

#    fact.addStep(shell.ShellCommand(
#        command=" && ".join([
#            "mv -f CREDITS CREDITS.buildbot",
#            "echo 'Buildbot Continuous Integration [Ere-build-bot] <buildbot@erebot.net> (lead)' > CREDITS",
#            "cat CREDITS.buildbot >> CREDITS",
#            "mkdir -p /tmp/release-%s" % pkg_name,
#            "pyrus.phar /tmp/release-%s set handle Ere-build-bot" % pkg_name,
#            "pyrus.phar /tmp/release-%s set openssl_cert /tmp/buildbot.p12" % pkg_name,
#            "cat /tmp/buildbot.sign | phing release -Dstability=snapshot",
#        ]) + "; " + " && ".join([
#            "mv -f CREDITS.buildbot CREDITS",
#            "rm -rf /tmp/release-%s" % pkg_name,
#        ]),
#        description="snapshot",
#        descriptionDone="snapshot",
#        haltOnFailure=True,
#        env={
#            'PATH': '/var/local/buildbot/bin:${PATH}',
#        },
#        maxTime=10*60,
#        locks=[pirum_lock.access('exclusive')],
#    ))

#    fact.addStep(shell.ShellCommand(
#        command="rm -f /tmp/buildbot.sign /tmp/buildbot.p12",
#        description=["buildenv", "cleanup"],
#        descriptionDone=["buildenv", "cleanup"],
#        haltOnFailure=True,
#    ))

#    fact.addStep(shell.ShellCommand(
#        command=properties.WithProperties(
#        """
#        for f in `ls -1 RELEASE-*`;
#        do
#            mv -v ${f} ${f%%snapshot%(got_revision)s};
#        done
#        """
#        ),
#        description=["finalize", "build"],
#        descriptionDone=["finalize", "build"],
#    ))

#    fact.addStep(shell.SetProperty(
#        command="ls -1 %s-*.tgz" % pkg_name,
#        description="version",
#        descriptionDone="version",
#        extract_fn=get_pear_pkg,
#    ))

#    fact.addStep(PhingPHPUnit(
#        command="phing test",
#        description="tests",
#        descriptionDone="tests",
#        warnOnWarnings=True,
#        env={
#            'PATH': '/var/local/buildbot/bin:${PATH}'
#        },
#        maxTime=10*60,
#    ))

#    fact.addStep(shell.ShellCommand(
#        # We can't run them all together, because of what seems
#        # like a conflict between these tools.
#        # (I suspect CodeSniffer is messing up the include_path).
#        command=" && ".join([
#            "phing qa_lint",
#            "phing qa_codesniffer",
#            "phing qa_duplicates",
#            "phing qa_mess",
#        ]),
#        description="QA",
#        descriptionDone="QA",
#        warnOnWarnings=True,
#        env={
#            'PATH': '/var/local/buildbot/bin:${PATH}'
#        },
#        maxTime=15*60,
#    ))

#    fact.addStep(master.MasterShellCommand(
#        command=
#            "rm -f /tmp/tagfiles.tar.gz && "
#            "cd public_html/ && "
#            "mkdir -p public_html/tagfiles/ &&"
#            "tar czvf /tmp/tagfiles.tar.gz tagfiles/",
#        description=["tar", "tagfiles"],
#        descriptionDone=["tar", "tagfiles"],
#        locks=[tagfiles_lock.access('exclusive')],
#    ))

#    fact.addStep(transfer.FileDownload(
#        mastersrc="/tmp/tagfiles.tar.gz",
#        slavedest="/tmp/Erebot_tagfiles.tar.gz",
#        locks=[tagfiles_lock.access('exclusive')],
#    ))

#    fact.addStep(shell.ShellCommand(
#        command=
#            "cd /tmp/ && "
#            "tar zxvf Erebot_tagfiles.tar.gz && "
#            "rm -f /tmp/Erebot_tagfiles.tar.gz",
#        description=["untar", "tagfiles"],
#        descriptionDone=["untar", "tagfiles"],
#        locks=[tagfiles_lock.access('exclusive')],
#    ))

#    fact.addStep(shell.WarningCountingShellCommand(
#        command="phing doc_html -Dtagfiles.reference=-",
#        description="HTML doc",
#        descriptionDone="HTML doc",
#        warningPattern="^(.*?):([0-9]+): [Ww]arning: (.*)$",
#        warningExtractor=
#            shell.WarningCountingShellCommand.warnExtractFromRegexpGroups,
#        warnOnWarnings=True,
#        env={
#            'PATH': '/var/local/buildbot/bin:${PATH}'
#        },
#        maxTime=10*60,
#    ))

#    fact.addStep(shell.ShellCommand(
#        command="phing doc_pdf",
#        description="PDF doc",
#        descriptionDone="PDF doc",
#        env={
#            'PATH': '/var/local/buildbot/bin:${PATH}'
#        },
#        maxTime=10*60,
#    ))

#    fact.addStep(shell.ShellCommand(
#        command=
#            "cd docs/ && "
#            "ln -sf html %(module)s && "
#            "find -L %(module)s "
#            "-name '*.html' -print0 -o "
#            "-name '*.png' -print0 -o "
#            "-name '*.css' -print0 -o "
#            "-name '*.js' -print0 | "
#            "tar -c -z -v -f %(module)s.tgz --null -T -; "
#            "cd -" % {
#                "module": pkg_name,
#            },
#    ))

#    fact.addStep(transfer.FileUpload(
#        slavesrc="%s.tagfile" % pkg_name,
#        masterdest="public_html/tagfiles/%s.tagfile" % pkg_name,
#        maxsize=1 * (1 << 20), # 1 MiB
#        locks=[tagfiles_lock.access('exclusive')],
#    ))

#    fact.addStep(transfer.FileUpload(
#        slavesrc="docs/latex/refman.pdf",
#        masterdest="public_html/doc/pdf/%s.pdf" % pkg_name,
#        maxsize=20 * (1 << 20), # 20 MiB
#    ))

#    fact.addStep(transfer.FileUpload(
#        slavesrc="docs/%s.tgz" % pkg_name,
#        masterdest="public_html/doc/html/%s.tgz" % pkg_name,
#        maxsize=50 * (1 << 20), # 50 MiB
#    ))

#    fact.addStep(master.MasterShellCommand(
#        command=
#            "tar -z -x -v -f public_html/doc/html/%(module)s.tgz -C "
#            "public_html/doc/html/" % {
#                "module": pkg_name,
#            },
#        description=["untar", "doc"],
#        descriptionDone=["untar", "doc"],
#    ))

#    fact.addStep(transfer.DirectoryUpload(
#        slavesrc="%s/trunk/docs/coverage/" % path,
#        masterdest="public_html/doc/coverage/%s/" % pkg_name,
#        doStepIf=lambda step: step.getProperty('Passed'),
#        maxsize=10 * (1 << 20), # 10 MiB
#    ))

#    fact.addStep(transfer.FileUpload(
#        slavesrc=properties.WithProperties("%(pear_pkg)s.tgz"),
#        masterdest=properties.WithProperties(
#            "/var/www/pear/get/%(pear_pkg)s.tgz"
#        ),
#        mode=0644,
#        doStepIf=generated_pear_pkg,
#        maxsize=50 * (1 << 20), # 50 MiB
#    ))

#    fact.addStep(transfer.FileUpload(
#        slavesrc=properties.WithProperties("%(pear_pkg)s.tgz.pubkey"),
#        masterdest=properties.WithProperties(
#            "/var/www/pear/get/%(pear_pkg)s.tgz.pubkey"
#        ),
#        mode=0644,
#        doStepIf=generated_pear_pkg,
#        maxsize=20 * (1 << 10), # 20 KiB
#    ))

#    fact.addStep(transfer.FileUpload(
#        slavesrc=properties.WithProperties("%(pear_pkg)s.pem"),
#        masterdest=properties.WithProperties(
#            "/var/www/pear/get/%(pear_pkg)s.pem"
#        ),
#        mode=0644,
#        doStepIf=generated_pear_pkg,
#        maxsize=20 * (1 << 10), # 20 KiB
#    ))

#    fact.addStep(Link(label="Code Coverage", href="%sdoc/coverage/%s/" % (
#        c['buildbotURL'],
#        pkg_name
#    )))

#    fact.addStep(Link(label="Online doc", href="%sdoc/html/%s/" % (
#        c['buildbotURL'],
#        pkg_name
#    )))

#    fact.addStep(Link(label="Tarball doc", href="%sdoc/html/%s.tgz" % (
#        c['buildbotURL'],
#        pkg_name
#    )))

#    fact.addStep(Link(label="PDF doc", href="%sdoc/pdf/%s.pdf" % (
#        c['buildbotURL'],
#        pkg_name
#    )))

#    fact.addStep(Link(
#        label="PEAR Package",
#        href=properties.WithProperties(
#            "http://pear.erebot.net/get/%(pear_pkg)s.tgz"
#        ),
#        doStepIf=generated_pear_pkg,
#    ))

#    fact.addStep(master.MasterShellCommand(
#        command="&&".join([
#            "/var/www/clean-pear.sh",
#            "/usr/bin/pirum build /var/www/pear",
#            "rm -rf /tmp/pirum_*",
#            "chmod -R a+r /var/www/pear/rest/",
#            "find /var/www/pear/rest -type d -exec chmod a+x '{}' '+'"
#        ]),
#        description=['PEAR', 'repos.', 'update'],
#        descriptionDone=['PEAR', 'repos.', 'update'],
#        doStepIf=generated_pear_pkg,
#        locks=[pirum_lock.access('exclusive')],
#    ))

#    repos_dir = "/tmp/pear-%s" % pkg_name

#    fact.addStep(shell.ShellCommand(
#        command=" && ".join([
#            "mkdir -p %s/bin" % repos_dir,
#            "pyrus.phar %(repos)s set bin_dir %(repos)s/bin" % {
#                'repos': repos_dir,
#            },
#        ]),
#        description=['PEAR2', 'creation'],
#        descriptionDone=['PEAR2', 'creation'],
#        doStepIf=generated_pear_pkg,
#        maxTime=10*60,
#        env={
#            'PATH': '/var/local/buildbot/bin:${PATH}'
#        },
#    ))

#    fact.addStep(shell.ShellCommand(
#        command="pyrus.phar %s channel-discover pear.erebot.net" % repos_dir,
#        description=['PEAR2', 'discovery'],
#        descriptionDone=['PEAR2', 'discovery'],
#        doStepIf=generated_pear_pkg,
#        maxTime=10*60,
#        env={
#            'PATH': '/var/local/buildbot/bin:${PATH}'
#        },
#    ))

#    fact.addStep(shell.ShellCommand(
#        command=properties.WithProperties(
#            "pyrus.phar %s install erebot/%%(pear_pkg)s; "
#            "rm `pyrus.phar get cache_dir | tail -n 1`/*.cache*" % repos_dir
#        ),
#        description=['PEAR2', 'installation'],
#        descriptionDone=['PEAR2', 'installation'],
#        warnOnFailure=True,
#        flunkOnFailure=False,
#        doStepIf=generated_pear_pkg,
#        maxTime=10*60,
#        env={
#            'PATH': '/var/local/buildbot/bin:${PATH}'
#        },
#    ))

#    fact.addStep(shell.ShellCommand(
#        command="rm -rf %s" % repos_dir,
#        description=['PEAR2', 'destruction'],
#        descriptionDone=['PEAR2', 'destruction'],
#        doStepIf=generated_pear_pkg,
#        maxTime=10*60,
#    ))

