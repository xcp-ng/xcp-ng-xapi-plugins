class Repo:
    def __init__(self, repo_id):
        self.id = repo_id
        self.enabled = True
        self.load_metadata_other = False

    def disable(self):
        self.enabled = False

class RepoDict(dict):
    def iter_enabled(self):
        return (r for r in self.values() if r.enabled)

class Package:
    def __init__(self):
        self.name = "Dummy Package"
        self.version = "0.0.0"
        self.release = "Dummy released"
        self.summary = "Lorem ipsum..."
        self.changelogs = []
        self.url = "http://www.example.com/"
        self.size = "0"
        self.license = "GPLv2 and LGPLv2+ and BSD"

class Query(list):
    def filterm(self, **kwargs):
        return self

    def latest(self):
        return self

class Sack:
    def query(self):
        return Query([Package()])

class Substitutions(dict):
    def update_from_etc(self, installroot, varsdir):
        pass

class Conf:
    installroot = '/'
    varsdir = ('/etc/dnf/vars/',)

    def __init__(self):
        self.substitutions = Substitutions()

    def read(self):
        pass

class Base:
    def __init__(self):
        self.conf = Conf()
        self.repos = RepoDict()
        self.sack = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        pass

    def read_all_repos(self):
        repos = ['xcp-ng-base', 'xcp-ng-updates', 'xcp-ng-linstor', 'totoro', 'lalala', 'riri', 'fifi', 'loulou']
        self.repos.update((r, Repo(r)) for r in repos)

    def fill_sack(self):
        self.sack = Sack()
