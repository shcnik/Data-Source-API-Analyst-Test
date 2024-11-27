from client import GHClient
from pagination import GHPaginatedList

class GHUser:
    def __init__(self, client: GHClient, **fields):
        self.client = client
        self.fields = fields
    
    def __getattr__(self, name):
        return self.fields[name]
    
    @property
    def repositories(self) -> GHPaginatedList[GHRepositiory]:
        return self.get_repositories()
    
    def get_repositories(self, **filters) -> GHPaginatedList[GHRepositiory]:
        return self.client.list_user_repositories(self, **filters)


class GHCommit:
    def __init__(self, client: GHClient, **fields):
        self.client = client
        self.fields = fields
    
    def __getattr__(self, name):
        if name in ['author', 'committer']:
            return GHUser(self.client, self.fields[name])
        return self.fields[name]


class GHRepositiory:
    def __init__(self, client: GHClient, **fields):
        self.client = client
        self.fields = fields
    
    def __getattr__(self, name):
        if name == 'owner':
            return GHUser(self.client, self.fields[name])
        elif name in ['template_repository', 'parent', 'source']:
            return GHRepositiory(self.client, self.fields[name])
        else:
            return self.fields[name]
    
    def get_commit(self, ref: str) -> GHCommit:
        return self.client.get_commit(self, ref)
    
    def get_commits(self, **filters) -> GHPaginatedList[GHCommit]:
        return self.client.list_commits(self, **filters)
    
    @property
    def commits(self):
        return self.get_commits()


class GHContent:
    def __init__(self, client: GHClient, **fields):
        self.client = client
        self.fields = fields
    
    def __getattr__(self, name):
        return self.fields[name]