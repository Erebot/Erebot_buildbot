# -*- encoding: utf-8 -*-

#from lxml import etree

import re
from twisted.python import log
from buildbot.steps.shell import ShellCommand
from buildbot.process.buildstep import BuildStep, LogLineObserver
try:
    from buildbot.status.logfile import STDOUT, STDERR
except ImportError:
    # For older versions.
    from buildbot.status.builder import STDOUT, STDERR

from buildbot.status.builder import SUCCESS, WARNINGS, FAILURE, \
                                    SKIPPED, EXCEPTION


class Link(BuildStep):
    name = "Link"

    def __init__(self, label, href, **kwargs):
        BuildStep.__init__(self, **kwargs)
        self.addFactoryArguments(label=label)
        self.addFactoryArguments(href=href)
        self.label = label
        self.href = href

    def start(self):
        properties = self.build.getProperties()
        href = properties.render(self.href)
        self.addURL(self.label, href)
        self.finished(SUCCESS)


class PHPUnit(ShellCommand, LogLineObserver):
    name = 'PHPUnit'

    def __init__(self, **kwargs):
        ShellCommand.__init__(self, **kwargs)
        LogLineObserver.__init__(self)
        self.addLogObserver('stdio', self)
        self.metrics = {
            "run": 0,
            "Failures": 0,
            "Errors": 0,
            "Incomplete": 0,
            "Skipped": 0,
            "Time elapsed": 0,
        }
        self.progressMetrics += tuple(self.metrics.keys())
        self.phpError = False

    def outLineReceived(self, line):
        # Handle (fatal) PHP errors.
        if 'PHP Error' in line:
            self.phpError = True
        if self.phpError:
            return

        # First, detect and handle coverage data.
        if '[coverage-threshold]' in line and 'Minimum found' in line:
            stats = line.split(':')[1].lstrip().split(' ')
            nb_tokens = len(stats)
            for i, pct in enumerate(stats):
                if pct.endswith('%') and \
                    i+2 < nb_tokens and \
                    stats[i+1] == 'per':
                    pct = float(pct[:-1])
                    # Remove separators from the names of metrics.
                    i = 'coverage-%s' % stats[i+2].rstrip('.,')
                    self.build.setProperty(
                        i,
                        min(pct, self.build.getProperty(i, 100))
                    )
            return

        # Ignore everything else that's not related to the tests.
        if '[phpunit]' not in line or ' Tests ' not in line:
            return
        (ign, sep, rest) = line.partition(' Tests ')
        if not rest:
            return

        # If colors are in use.
        (rest2, sep, ign) = rest.rpartition('\033')
        if rest2:
            rest = rest2

        # Extract metrics values.
        rest = rest.split(', ')
        metrics = {}
        for i in rest:
            metric, value = i.split(': ')
            value = value.rsplit(' s', 2)[0]
            conversion = '.' in value and float or int
            metrics[metric] = conversion(value)

        # Update final metrics & progress meter.
        for metric, value in metrics.iteritems():
            if value > 0:
                self.metrics[metric] += value
                self.step.setProgress(metric, self.metrics[metric])

    def createSummary(self, log):
        for metric, value in self.metrics.iteritems():
            old_value = self.build.getProperty("PHPUnit-%s" % metric, 0)
            self.build.setProperty(
                "PHPUnit-%s" % metric,
                old_value + value,
                "PHPUnit"
            )

    def evaluateCommand(self, cmd):
        passed = self.getProperty("Passed", True)
        self.setProperty('Passed', bool(passed))
        if cmd.rc != 0 or self.phpError or self.metrics['Failures']:
            self.setProperty('Passed', False)
            return FAILURE
        if self.metrics['Errors']:
            self.setProperty('Passed', False)
            return EXCEPTION
        if self.metrics['Skipped'] or self.metrics['Incomplete']:
            return WARNINGS
        if not self.metrics['run']:
            return WARNINGS
        return SUCCESS


class CountingShellCommand(ShellCommand):
    errorCount = 0
    errorPattern = '.*error[: ].*'
    warnCount = 0
    warningPattern = '.*warning[: ].*'

    # The defaults work for GNU Make.
    directoryEnterPattern = "make.*: Entering directory [\"`'](.*)['`\"]"
    directoryLeavePattern = "make.*: Leaving directory"
    suppressionFile = None

    commentEmptyLineRe = re.compile(r"^\s*(\#.*)?$")
    suppressionLineRe = re.compile(r"^\s*(.+?)\s*:\s*(.+?)\s*(?:[:]\s*([0-9]+)(?:-([0-9]+))?\s*)?$")

    def __init__(self, workdir=None,
                 errorPattern=None, errorExtractor=None,
                 warningPattern=None, warningExtractor=None,
                 directoryEnterPattern=None, directoryLeavePattern=None,
                 suppressionFile=None, **kwargs):
        self.workdir = workdir
        # See if we've been given a regular expression to use to match
        # warnings. If not, use a default that assumes any line with "warning"
        # present is a warning. This may lead to false positives in some cases.
        if warningPattern:
            self.warningPattern = warningPattern
        if errorPattern:
            self.errorPattern = errorPattern

        if directoryEnterPattern:
            self.directoryEnterPattern = directoryEnterPattern
        if directoryLeavePattern:
            self.directoryLeavePattern = directoryLeavePattern
        if suppressionFile:
            self.suppressionFile = suppressionFile

        if errorExtractor:
            self.errorExtractor = errorExtractor
        else:
            self.errorExtractor = CountingShellCommand.extractWholeLine

        if warningExtractor:
            self.warningExtractor = warningExtractor
        else:
            self.warningExtractor = CountingShellCommand.extractWholeLine

        # And upcall to let the base class do its work
        ShellCommand.__init__(self, workdir=workdir, **kwargs)

        self.addFactoryArguments(errorPattern=errorPattern,
                                 warningPattern=warningPattern,
                                 directoryEnterPattern=directoryEnterPattern,
                                 directoryLeavePattern=directoryLeavePattern,
                                 errorExtractor=errorExtractor,
                                 warningExtractor=warningExtractor,
                                 suppressionFile=suppressionFile)
        self.suppressions = []
        self.directoryStack = []

    def addSuppression(self, suppressionList):
        """
        This method can be used to add patters of warnings that should
        not be counted.

        It takes a single argument, a list of patterns.

        Each pattern is a 4-tuple (FILE-RE, WARN-RE, START, END).

        FILE-RE is a regular expression (string or compiled regexp), or None.
        If None, the pattern matches all files, else only files matching the
        regexp. If directoryEnterPattern is specified in the class constructor,
        matching is against the full path name, eg. src/main.c.

        WARN-RE is similarly a regular expression matched against the
        text of the warning, or None to match all warnings.

        START and END form an inclusive line number range to match against. If
        START is None, there is no lower bound, similarly if END is none there
        is no upper bound."""

        for fileRe, lineRe, start, end in suppressionList:
            if fileRe != None and isinstance(fileRe, str):
                fileRe = re.compile(fileRe)
            if lineRe != None and isinstance(lineRe, str):
                lineRe = re.compile(lineRe)
            self.suppressions.append((fileRe, lineRe, start, end))

    def extractWholeLine(self, line, match):
        """
        Extract warning text as the whole line.
        No file names or line numbers."""
        return (None, None, line)

    def extractFromRegexpGroups(self, line, match):
        """
        Extract file name, line number, and warning text as groups (1,2,3)
        of warningPattern match."""
        file = match.group(1)
        lineNo = match.group(2)
        if lineNo != None:
            lineNo = int(lineNo)
        text = match.group(3)
        return (file, lineNo, text)

    def maybeAddWarning(self, stack, line, match, is_error):
        if self.suppressions:
            if is_error:
                (file, lineNo, text) = self.errorExtractor(self, line, match)
            else:
                (file, lineNo, text) = self.warnExtractor(self, line, match)

            if file != None and file != "" and self.directoryStack:
                currentDirectory = self.directoryStack[-1]
                if currentDirectory != None and currentDirectory != "":
                    file = "%s/%s" % (currentDirectory, file)

            # Skip adding the warning if any suppression matches.
            for fileRe, warnRe, start, end in self.suppressions:
                if ( (file == None or fileRe == None or fileRe.search(file)) and
                     (warnRe == None or  warnRe.search(text)) and
                     ((start == None and end == None) or
                      (lineNo != None and start <= lineNo and end >= lineNo)) ):
                    return

        stack.append(line)
        if is_error:
            self.errorCount += 1
        else:
            self.warnCount += 1

    def createSummary(self, log):
        """
        Match log lines against warningPattern.

        Warnings are collected into another log for this step, and the
        build-wide 'warnings-count' is updated."""

        self.warnCount = 0
        self.errorCount = 0

        # Now compile a regular expression from whichever warning pattern we're
        # using
        if (not self.warningPattern) and (not self.errorPattern):
            return

        wre = self.warningPattern
        if isinstance(wre, str):
            wre = re.compile(wre)

        ere = self.errorPattern
        if isinstance(ere, str):
            ere = re.compile(ere)

        directoryEnterRe = self.directoryEnterPattern
        if directoryEnterRe != None and isinstance(directoryEnterRe, str):
            directoryEnterRe = re.compile(directoryEnterRe)

        directoryLeaveRe = self.directoryLeavePattern
        if directoryLeaveRe != None and isinstance(directoryLeaveRe, str):
            directoryLeaveRe = re.compile(directoryLeaveRe)

        # Check if each line in the output from this command matched our
        # warnings regular expressions. If did, bump the warnings count and
        # add the line to the collection of lines with warnings
        errors = []
        warnings = []
        # TODO: use log.readlines(), except we need to decide about stdout vs
        # stderr
        for line in log.getText().split("\n"):
            if directoryEnterRe:
                match = directoryEnterRe.search(line)
                if match:
                    self.directoryStack.append(match.group(1))
                if (directoryLeaveRe and
                    self.directoryStack and
                    directoryLeaveRe.search(line)):
                        self.directoryStack.pop()

            match = ere.match(line)
            if match:
                self.maybeAddWarning(errors, line, match, True)
            else:
                match = wre.match(line)
                if match:
                    self.maybeAddWarning(warnings, line, match, False)

        # If there were any warnings, make the log if lines with warnings
        # available
        if self.warnCount:
            self.addCompleteLog("warnings (%d)" % self.warnCount,
                    "\n".join(warnings) + "\n")

        if self.errorCount:
            self.addCompleteLog("errors (%d)" % self.errorCount,
                    "\n".join(errors) + "\n")

        warnings_stat = self.step_status.getStatistic('warnings', 0)
        self.step_status.setStatistic(
            'warnings',
            warnings_stat + self.warnCount
        )

        old_count = self.getProperty("warnings-count", 0)
        self.setProperty(
            "warnings-count",
            old_count + self.warnCount,
            "CountingShellCommand"
        )

        errors_stat = self.step_status.getStatistic('errors', 0)
        self.step_status.setStatistic('errors', errors_stat + self.errorCount)

        old_count = self.getProperty("errors-count", 0)
        self.setProperty(
            "errors-count",
            old_count + self.errorCount,
            "CountingShellCommand"
        )

    def evaluateCommand(self, cmd):
        if cmd.rc != 0:
            return FAILURE
        if self.errorCount:
            return FAILURE
        if self.warnCount:
            return WARNINGS
        return SUCCESS


class MorphProperties(BuildStep):
    name = "MorphProperties"
    progress = False

    def __init__(self, morph_fn, **kwargs):
        BuildStep.__init__(self, **kwargs)
        self.addFactoryArguments(morph_fn=morph_fn)
        self.morph_fn = morph_fn

    def start(self):
        self.morph_fn(self.build.getProperties())
        self.finished(SUCCESS)


class SetPropertiesFromEnv(BuildStep):
    """
    Sets properties from envirionment variables on the slave.

    Note this is transfered when the slave first connects
    """
    name='SetPropertiesFromEnv'
    description='Setting'
    descriptionDone='Set'

    def __init__(self, variables, source="SlaveEnvironment", **kwargs):
        BuildStep.__init__(self, **kwargs)
        self.addFactoryArguments(variables = variables,
                                 source = source)
        self.variables = variables
        self.source = source

    def start(self):
        # on Windows, environment variables are case-insensitive, but we have
        # a case-sensitive dictionary in slave_environ.  Fortunately, that
        # dictionary is also folded to uppercase, so we can simply fold the
        # variable names to uppercase to duplicate the case-insensitivity.
        fold_to_uppercase = (self.buildslave.slave_system == 'win32')

        properties = self.build.getProperties()
        environ = self.buildslave.slave_environ
        variables = self.variables
        if isinstance(variables, str):
            variables = [self.variables]
        for variable in variables:
            key = variable
            if fold_to_uppercase:
                key = variable.upper()
            value = environ.get(key, None)
            if value:
                # note that the property is not uppercased
                properties.setProperty(variable, value, self.source,
                                       runtime=True)
        self.finished(SUCCESS)


class FetchI18n(ShellCommand):
    name = 'Fetch'

    def start(self):
        cmd = []
        files = set()
        for c in self.build.allChanges():
            locale = c.properties.getProperty('locale')
            txProject = c.properties.getProperty('txProject')
            txResource = c.properties.getProperty('txResource')
            files.add( (txProject, txResource, locale) )

        for txProject, txResource, locale in files:
            cmd.append(
                "/bin/mkdir -p data/i18n/%(locale)s/LC_MESSAGES/ && "
                "/usr/bin/wget -O "
                "data/i18n/%(locale)s/LC_MESSAGES/%(resource)s.po "
                "'https://www.transifex.com/api/2/project/%(project)s/resource/"
                "%(resource)s/translation/%(locale)s/?file=1&mode=reviewed'" % {
                    'project': txProject,
                    'resource': txResource,
                    'locale': locale,
                }
            )

        self.command = " && ".join(cmd)
        ShellCommand.start(self)


class AddI18n(ShellCommand):
    name = 'Add'

    def start(self):
        cmd = [
            '/usr/bin/git',
            'add',
        ]

        files = set()
        for c in self.build.allChanges():
            for f in c.files:
                if f.startswith('data/i18n/'):
                    files.add(f)
        cmd.extend(files)
        self.command = cmd
        ShellCommand.start(self)


class CommitI18n(ShellCommand):
    name = 'Commit'

    def start(self):
        cmd = [
            '/usr/bin/git',
            'commit',
            '-m',
        ]

        locales = {}
        for c in self.build.allChanges():
            locales[c.properties.getProperty('locale')] = \
                c.properties.getProperty('percent')
        sorted_locales = locales.keys()
        sorted_locales.sort()

        commit_message = ['i18n update\n\n']
        for locale in sorted_locales:
            commit_message.append( "%s: %s%%\n" % (locale, locales[locale]) )
        commit_message.append("[ci skip]\n") # Skip travis-ci build.
        cmd.append("".join(commit_message).rstrip())
        self.command = cmd
        ShellCommand.start(self)

