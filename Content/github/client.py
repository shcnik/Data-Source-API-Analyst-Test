import requests
import os
import json
from errors import *
from pagination import GHPaginatedList
from util import parse_repo
from time import sleep
from datetime import datetime

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
    
    def check_response(self, cmd: str, response: Response):
        if response.status_code in GHAccessError.code_to_msg:
            raise GHAccessError(response.status_code, cmd)


    def make_request(self, command: str, **kwargs) -> requests.Response:
        response = requests.get(
            f'https://api.github/com/{command}',
            headers=self.headers,
            params=kwargs
        )
        self.check_response(command, response)
        if response.headers['x-ratelimit-remaining'] == '0':
            sleep(int(response.headers.get('retry-after', '0')))
            sleep(int(response.headers['x-ratelimit-reset']) - datetime.now().timestamp())
            return self.make_request(command, **kwargs)
        return response
    
    def get_repository(self, owner: str, repo: str) -> requests.Response:
        return self.make_request(f'repos/{owner}/{repo}')
    
    def get_repository(self, repo: str | tuple[str, str]) -> requests.Response:
        owner, repo_name = parse_repo(repo)
        return self.get_repository(owner, repo_name)
    
    def list_auth_user_repositories(self, **filters) -> tuple[requests.Response, GHPaginatedList]:
        r = self.make_request('user/repos', **filters)
        self.check_response('user/repos', r)
        return r, GHPaginatedList(self, r.json(), r.headers['links'])
    
    def list_public_repositories(self, **filters) -> tuple[requests.Response, GHPaginatedList]:
        r = self.make_request('repositories', **filters)
        self.check_response('repositories', r)
        return r, GHPaginatedList(self, r.json(), r.headers['links'])

    def list_user_repositories(self, user: str, **filters) -> tuple[requests.Response, GHPaginatedList]:
        r = self.make_request(f'users/{user}/repos', **filters)
        self.check_response(f'users/{user}/repos', r)
        return r, GHPaginatedList(self, r.json(), r.headers['links'])
    
    def get_commit(self, repo: str | tuple[str, str], ref: str) -> dict:
        owner, repo_name = parse_repo(repo)
        r = self.make_request(f'/repos/{owner}/{repo_name}/commits/{ref}')
        self.check_response(f'/repos/{owner}/{repo_name}/commits/{ref}', r)
        return r
    
    def list_commits(self, repo: str | tuple[str, str], **filters) -> tuple[requests.Response, GHPaginatedList]:
        owner, repo_name = parse_repo(repo)
        r = self.make_request(f'/repos/{owner}/{repo_name}/commits/', **filters)
        self.check_response(f'/repos/{owner}/{repo_name}/commits/', r)
        return r, GHPaginatedList(self, r.json(), r.headers['links'])

    def get_contents(self, repo: str | tuple[str, str], path: str, ref: None | str = None) -> Response:
        owner, repo_name = parse_repo(repo)
        r = self.make_request(f'/repos/{owner}/{repo_name}/commits/{ref or ''}')
        self.check_response(f'/repos/{owner}/{repo_name}/commits/{ref or ''}', r)
        return r
