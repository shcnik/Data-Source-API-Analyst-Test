from client import GHClient
from collections.abc import Sequence
import re
from copy import copy
from requests import Response

def parse_cmds(links: str) -> dict[str, str]:
    regex = re.compile('<https://api\.github\.com/([A-Za-z0-9_/\?&=]*)>; rel="([a-z]*)"')
    res = {}
    for cmd, rel in regex.findall(links):
        res[rel] = cmd
    return res

class GHPaginatedList:
    def __init__(self, client: GHClient, content: Sequence[dict], links: str, step: int = 1):
        self.client = client
        self.content = content
        self.refs = parse_cmds(links)
        self.pos = 0
        self.step = 1
    
    def move(self, rel: str):
        r = self.client.make_request(self.refs[rel])
        self.refs = parse_cmds(r.headers['links'])
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
    
    def next(self) -> dict:
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
    
    def __reversed__(self) -> GHPaginatedList:
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
