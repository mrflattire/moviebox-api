# Known Issues

## v3 — no retry/refresh on transient auth errors (441)

**Status:** v3 is functional. Search → item details → resolve → download
all work end-to-end and were verified across multiple separate test runs.

During initial v0.0.1 testing, one run failed with:

```
UnsuccessfulResponseError: Unsuccessful response received from server
-STATUS 441 - BODY: '{"code":441,"reason":"UNAUTHORIZED","message":"miss token","metadata":{}}'
```

Every subsequent run (same code, same environment, spaced out over time)
succeeded cleanly. This was a transient failure, not a stable backend
break — the earlier assumption that v3's POST endpoints were reliably
broken was wrong and has been reverted from this doc and from the CLI.

### The real, narrower issue

`RETRY_STATUS_CODES` in `v3/constants.py` is `{403, 407, 429, 500, 502,
503, 504}` — **441 isn't included**, and v3's `MovieBoxHttpClient` has no
equivalent to v1's `Session._fetch_user_info` retry-with-refresh loop for
auth failures. So when a transient auth/token hiccup does occur on a POST
request, v3 has no built-in way to recover from it — it just raises
immediately, with no retry and no attempt to fetch a fresh token.

v1's `Session`, by contrast, explicitly retries and refreshes the token on
401/403.

### Possible future improvement

Add 441 to a v3-specific retryable-status set (or a dedicated auth-retry
path similar to v1's) so a one-off transient token issue doesn't
immediately surface as a hard failure to the end user. Not urgent — this
appears to be rare — but worth doing if it recurs with any frequency.