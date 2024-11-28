from collections.abc import Sequence
import re
from copy import copy
from time import sleep
from requests import *
import os
from datetime import datetime

def parse_repo(repo: str | tuple[str, str]) -> tuple[str, str]:
    if repo is tuple:
        return repo
    else:
        return repo.split('/')

class GHRateLimitError(Exception):
    def __init__(self, to_wait: int):
        self.to_wait = to_wait
    
    def wait(self):
        sleep(self.to_wait)

class GHAccessError(Exception):
    code_to_msg = {
        codes.unauthorized: 'Requires authentication',
        codes.forbidden: 'Forbidden',
        codes.not_found: 'Resource not found',
        codes.unprocessable_entity: 'Validation failed, or the endpoint has been spammed'
    }

    def __init__(self, msg: str, cmd: str):
        self.msg = msg
        self.cmd = cmd
    
    def __init__(self, code: int, cmd: str):
        self.msg = GHAccessError.code_to_msg[code]
        self.cmd = cmd


def parse_cmds(links: str) -> dict[str, str]:
    if links is None:
        return {}
    regex = re.compile('<https://api\.github\.com/([A-Za-z0-9_/\?&=]*)>; rel="([a-z]*)"')
    res = {}
    for cmd, rel in regex.findall(links):
        res[rel] = cmd
    return res


class GHPaginatedList:
    def __init__(self, client, content: Sequence[dict], links: str, step: int = 1):
        self.client = client
        self.content = content
        self.refs = parse_cmds(links)
        self.pos = 0
        self.step = 1
    
    def move(self, rel: str):
        if rel not in self.refs:
            return
        r = self.client.make_request(self.refs.get(rel))
        self.refs = parse_cmds(r.headers.get('link'))
        self.content = r.json()
    
    def next_page(self):
        self.move('next')
    
    def prev_page(self):
        self.move('prev')
    
    def first_page(self):
        self.move('first')
    
    def last_page(self):
        self.move('last')
    
    def at_start(self) -> bool:
        return 'prev' not in self.refs

    def at_end(self) -> bool:
        return 'next' not in self.refs
    
    def __iter__(self):
        if self.step > 0:
            self.first_page()
            self.pos = 0
        else:
            self.last_page()
            self.pos = len(self.content) - 1
        return self
    
    def __next__(self) -> dict:
        self.pos += self.step
        if self.pos >= len(self.content):
            if self.at_end():
                raise StopIteration()
            self.next_page()
            self.pos = 0
        elif self.pos < 0:
            if self.at_start():
                raise StopIteration()
            self.prev_page()
            self.pos = len(self.content) - 1
        return self.content[self.pos]

    def __getitem__(self, key) -> dict:
        if key >= 0:
            self.first_page()
            while key >= len(self.content):
                key -= len(self.content)
                self.next_page()
            return self.content[key]
        else:
            self.last_page()
            while -key > len(self.content):
                key += len(self.content)
                self.prev_page()
            return self.content[key]
    
    def __reversed__(self):
        rev = copy(self)
        rev.step = -self.step
        return rev

    def __len__(self) -> int:
        self.first_page()
        cnt = len(self.content)
        while not self.at_end():
            self.next_page()
            cnt += len(self.content)
        return cnt


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


    def make_request(self, command: str, **kwargs) -> Response:
        response = get(
            f'https://api.github.com/{command}',
            headers=self.headers,
            params=kwargs
        )
        self.check_response(command, response)
        if response.headers['x-ratelimit-remaining'] == '0':
            raise GHRateLimitError(
                    max(int(response.headers.get('retry-after', '0')),
                    (int(response.headers['x-ratelimit-reset']) - datetime.now().timestamp()))
                )
        return response
    
    def get_repository(self, owner: str, repo: str) -> dict:
        return self.get_repository((owner, repo)).json()
    
    def get_repository(self, repo: str | tuple[str, str]) -> dict:
        owner, repo_name = parse_repo(repo)
        r = self.make_request(f'repos/{owner}/{repo_name}')
        self.check_response(f'repos/{owner}/{repo_name}', r)
        return r.json()
    
    def list_auth_user_repositories(self, **filters) -> GHPaginatedList:
        r = self.make_request('user/repos', **filters)
        self.check_response('user/repos', r)
        return GHPaginatedList(self, r.json(), r.headers.get('link'))
    
    def list_public_repositories(self, **filters) -> GHPaginatedList:
        r = self.make_request('repositories', **filters)
        self.check_response('repositories', r)
        return GHPaginatedList(self, r.json(), r.headers.get('link'))

    def list_user_repositories(self, user: str, **filters) -> GHPaginatedList:
        r = self.make_request(f'users/{user}/repos', **filters)
        self.check_response(f'users/{user}/repos', r)
        return GHPaginatedList(self, r.json(), r.headers.get('link'))
    
    def get_commit(self, repo: str | tuple[str, str], ref: str) -> dict:
        owner, repo_name = parse_repo(repo)
        r = self.make_request(f'/repos/{owner}/{repo_name}/commits/{ref}')
        self.check_response(f'/repos/{owner}/{repo_name}/commits/{ref}', r)
        return r.json()
    
    def list_commits(self, repo: str | tuple[str, str], **filters) -> GHPaginatedList:
        owner, repo_name = parse_repo(repo)
        r = self.make_request(f'/repos/{owner}/{repo_name}/commits', **filters)
        self.check_response(f'/repos/{owner}/{repo_name}/commits', r)
        return GHPaginatedList(self, r.json(), r.headers.get('link'))

    def get_contents(self, repo: str | tuple[str, str], path: str, ref: None | str = None) -> dict | list[dict]:
        owner, repo_name = parse_repo(repo)
        r = self.make_request(f'/repos/{owner}/{repo_name}/contents')
        self.check_response(f'/repos/{owner}/{repo_name}/contents', r)
        return r.json()
