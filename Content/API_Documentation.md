# Github API documentation

## `GHClient`

Class `GHClient` is main class for accessing GitHub API. It provides methods for interacting with it, handles authentication and errors.

### `__init__(self, version: str, useragent: str, use_env_token: bool=False, personal_token: str=None)`

Constructs new client.

#### Parameters

- `version`: API version to use
- `useragent`: useragent to use for ineractions
- `use_env_token`: if set to `True`, the value of environment variable `AUTH_TOKEN` is used.
- `personal_token`: string with personal token to use. If `None`, no token will be used.

### `make_request(self, command: str, **kwargs) -> Response`

Generic method to issue commands to GitHub API.

#### Parameters

- `command`: command to issue
- `**kwargs`: query parameters

#### Returns

An object of `requests.Response` class with API response to command.

### `get_repository(self, owner: str, repo: str) -> dict`

Get information on repository.

#### Parameters

- `owner`: Username of repository author
- `repo`: Repository name

#### Returns

Dictionary with information about repository.

### `get_repository(self, repo: str | tuple[str, str]) -> dict`

Get information on repository.

#### Parameters

- `repo`: either tuple of `(owner, name)` or string `"owner/name"`

#### Returns

Dictionary with information about repository.

### `list_auth_user_repositories(self, **filters) -> GHPaginatedList`

Get list of repositories available to authenticated user.

#### Parameters

- `**filters`: query parameters

#### Returns

List of repositories - an object of `GHPaginatedList` class, which handles pagination if required.

### `list_public_repositories(self, **filters)`

Get list of available public repositories with set requirements.

#### Parameters

- `**filters`: query parameters

#### Returns

List of repositories - an object of `GHPaginatedList` class, which handles pagination if required.

### `list_user_repositories(self, user: str, **filters) -> GHPaginatedList`

Lists public repositories associated with user.

#### Parameters

- `user`: user's name
- `**filters`: query parameters

#### Returns

List of repositories - an object of `GHPaginatedList` class, which handles pagination if required.

### `get_commit(self, repo: str | tuple[str, str], ref: str) -> dict`

Fetches info about commit.

### Parameters

- `repo`: either tuple of `(owner, name)` or string `"owner/name"`, repository to search for commit
- `ref`: Can be a commit SHA, branch name (heads/BRANCH_NAME), or tag name (tags/TAG_NAME).

### Returns

Dictionary with information about commit.

### `list_commits(self, repo: str | tuple[str, str], **filters) -> GHPaginatedList`

Lists commits in repository.

### Parameters

- `repo`: either tuple of `(owner, name)` or string `"owner/name"`, repository to search for commit
- `**filters`: query parameters

### Returns

List of commits - an object of `GHPaginatedList` class, which handles pagination if required.

## `get_contents(self, repo: str | tuple[str, str], path: str, ref: None | str = None) -> dict | list[dict]`

Gets content of an object (file or directory) in repository on set path.

### Parameters

- `repo`: either tuple of `(owner, name)` or string `"owner/name"`, repository to search for commit
- `path`: path to object
- `ref`: (*optional*) commit where contents of object should be retrieved

### Returns

Dictionary with information if requested object is file; list of dictionaries about contained objects if dictionary was requested.

## `GHPaginatedList`

Class `GHPaginatedList` handles pagination. It allows iteration over paged response as if it was one complete list as well as handling pages separately.

Objects of this class shall not be created manually, they are generated in `GHClient` methods when needed.

`GHPaginatedList` allows the same operations as usual list: indexed access, iteration with `for ... in ...`, `len()`, `reversed()`.

### `next_page(self)`, `prev_page(self)`, `first_page(self)`, `last_page(self)`

Moves to next, previous, first or last page respectively.

### `at_start(self) -> bool`, `at_end(self) -> bool`

Checks if list points to first or last page respectively.

#### Returns

Result of check

### `contents`

Contents of current page as list.

