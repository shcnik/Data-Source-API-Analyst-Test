import requests
import os
import json
from errors import *
from objects import *
from pagination import GHPaginatedList
from util import parse_repo

class GHClient:
    def __init__(self, version: str, useragent: str, use_env_token: bool=False, personal_token: str=None):
        self.token = os.environ['AUTH_TOKEN'] if use_env_token else personal_token
        self.version = version
        self.useragent = useragent
        self.headers = {
            'Authorization': f'token {self.token}',
            'X-GitHub-Api-Version': self.version,
            'User-Agent': self.useragent,
            'Accept': 'application/vnd.github+json'
        }

    def make_request(self, command: str, **kwargs):
        response = requests.get(
            f'https://api.github/com/{command}',
            headers=self.headers,
            params=kwargs
        )
        return response
    
    def get_repository(self, owner: str, repo: str) -> GHRepositiory:
        r = self.make_request(f'repos/{owner}/{repo}')
        if r.status_code == requests.codes.not_found:
            raise ObjectNotFoundError('repo', f'{owner}/{repo}')
        elif r.status_code == requests.codes.forbidden:
            raise UnauthorizedAccessError('repo', f'{owner}/{repo}')
        return GHRepositiory(self, r.json())
    
    def get_repository(self, repo: str) -> GHRepositiory:
        owner, repo_name = repo.split('/')
        return self.get_repository(owner, repo_name)
    
    def list_auth_user_repositories(self, **filters) -> GHPaginatedList[GHRepositiory]:
        r = self.make_request('user/repos', **filters)
        if r.status_code in [requests.codes.forbidden, requests.codes.unauthorized]:
            raise CommandForbiddenError('/user/repos?' + '&'.join([f'{key}={value}' for key, value in filters.items()]))
        return GHPaginatedList(self, [GHRepositiory(self, **obj) for obj in r.json()], GHRepositiory, r.headers['links'])
    
    def list_public_repositories(self, **filters) -> GHPaginatedList[GHRepositiory]:
        r = self.make_request('repositories', **filters)
        return GHPaginatedList(self, [GHRepositiory(self, **obj) for obj in r.json()], GHRepositiory, r.headers['links'])

    def list_user_repositories(self, user: str | GHUser, **filters) -> GHPaginatedList[GHRepositiory]:
        r = self.make_request(f'users/{user.login if user is GHUser else user}/repos', **filters)
        return GHPaginatedList(self, [GHRepositiory(self, **obj) for obj in r.json()], GHRepositiory, r.headers['links'])
    
    def get_commit(self, repo: str | tuple[str, str] | GHRepositiory, ref: str) -> GHCommit:
        owner, repo_name = parse_repo(repo)
        r = self.make_request(f'/repos/{owner}/{repo_name}/commits/{ref}')
        if r.status_code == requests.codes.not_found:
            raise ObjectNotFoundError('commit', ref)
        return GHCommit(self, r.json())
    
    def list_commits(self, repo: str | tuple[str, str] | GHRepositiory, **filters) -> GHPaginatedList[GHCommit]:
        owner, repo_name = parse_repo(repo)
        r = self.make_request(f'/repos/{owner}/{repo_name}/commits/', **filters)
        if r.status_code == requests.codes.not_found:
            raise ObjectNotFoundError('repo', f'{owner}/{repo_name}')
        return GHPaginatedList(self, [GHCommit(self, **obj) for obj in r.json()], GHCommit, r.headers['links'])

    def get_contents(self, repo: str | tuple[str, str] | GHRepositiory, path: str, ref: None | str | GHCommit = None) -> GHContent | list[GHContent]:
        owner, repo_name = parse_repo(repo)
        r = self.make_request(f'/repos/{owner}/{repo_name}/commits/')
        if r.status_code == requests.codes.not_found:
            raise ObjectNotFoundError('repo', f'{owner}/{repo}')
        elif r.status_code == requests.codes.forbidden:
            raise UnauthorizedAccessError('repo', f'{owner}/{repo}')