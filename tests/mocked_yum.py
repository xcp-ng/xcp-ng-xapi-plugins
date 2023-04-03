class Repos:
    def __init__(self):
        return

    def enableRepo(self, repos):
        return 0

    def disableRepo(self, repos):
        return 0

    def listEnabled(self):
        repos = ['xcp-ng-base', 'xcp-ng-updates', 'totoro', 'lalala', 'riri', 'fifi', 'loulou']

        class RepoObject:
            def __init__(self, repo):
                self.id = repo
        return [RepoObject(repo) for repo in repos]

class Ts:
    def __init__(self):
        return

    def check(self):
        return 0

    def order(self):
        return 0

class Package:
    def __init__(self):
        self.name = "Dummy Package"
        self.version = "0.0.0"
        self.release = "Dummy released"
        self.summary = "Lorem ipsum..."
        self.changelog = {}
        self.url = "http://www.example.com/"
        self.size = "0"
        self.license = "GPLv2 and LGPLv2+ and BSD"

class Preconf:
    def __init__(self):
        return

class YumBase:
    def __init__(self):
        self.repos = Repos()
        self.initActionTs()
        self.preconf = Preconf()
        return

    def doPackageLists(self, pkgnarrow):
        return [Package()]

    def initActionTs(self):
        self.ts = Ts()

    def populateTs(self, keepold):
        return 0
