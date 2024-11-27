from objects import GHRepositiory

def parse_repo(repo: str | tuple[str, str] | GHRepositiory) -> tuple[str, str]:
    repo_fullname = ''
    if repo is GHRepositiory:
        repo_fullname = repo.full_name
    elif repo is tuple:
        repo_fullname = f'{repo[0]}/{repo[1]}'
    else:
        repo_fullname = repo
    return repo_fullname.split('/')