from time import sleep
from requests import Response, codes

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
