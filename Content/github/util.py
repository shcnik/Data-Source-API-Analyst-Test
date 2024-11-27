def parse_repo(repo: str | tuple[str, str]) -> tuple[str, str]:
    if repo is tuple:
        return repo
    else:
        return repo.split('/')
