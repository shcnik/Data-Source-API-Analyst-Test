# Error Handling

The GitHub API client handles errors using Python exceptions mechanism. Exceptions of two classes are used:

- `GHRateLimitError` - raised when rate limits reached.
- `GHAccessError` - raised when for some reason access to requested resource was rejected. The field `msg` provided information on error.

## Rate limit reached

Object of `GHRateLimitError` exception provides a method `wait()`. When called, it causes script to sleep as long as instructed by GitHub API (i.e. the maximum of `Retry-After` header value and the time before rate limit reset).

Snippet for handing this error:

```
try:
    # do something...
except GHRateLimitError as e:
    e.wait()
    # do something again...
```

## Access errors

In the next sections we will provide some advice on solving issues when accessing GitHub API not related to rate limits.

### Requires authentication

Authentication to GitHub API failed.

- Verify the AUTH_TOKEN or access token. Ensure it’s active and has the necessary permissions.
- If you provide personal token as parameter, do not set `use_env_token` parameter to `True` when initializing `GHClient`

### Forbidden

Access to requested resource is forbidden to you.

- Check if you use correct token.
- Check if you request correct resource.
- Check if the mode of requested repository was set to private.

### Resource not found

Requested resource not found.

- Check if you spelled resource's name correctly.
- Check if requested resource was deleted by other user.
- Check if you make request for resource with correct type (e.g. you request repository, not commit, when you need repository)

### Validation failed, or the endpoint has been spammed

This error should not be raised when you use specific methods, unless you have issued too many requests.

- Check if your script falls to infinite loop.
- If you have to get multiple objects, consider requesing them as list using respective methods, not getting them one by one.
- If you use `make_request` directly, check if you spell command name correctly. Also, consider using specific methods.
