class ObjectAccessError(Exception):
    def __init__(self, type: str, name: str, *args):
        super().__init__(*args)
        self.type = type
        self.name = name


class ObjectNotFoundError(ObjectAccessError):
    def __init__(self, type: str, name: str, *args):
        super().__init__(type, name, *args)


class UnauthorizedAccessError(ObjectAccessError):
    def __init__(self, type: str, name: str, *args):
        super().__init__(type, name, *args)

class CommandForbiddenError(Exception):
    def __init__(self, cmd: str, *args):
        super().__init__(*args)
        self.cmd = cmd
