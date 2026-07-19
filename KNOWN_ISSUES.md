# Known Issues

## v3 — POST endpoints reject authentication (as of 2026-07)

**Status:** v3 auth/token bootstrap works. All POST-based endpoints
(`Search`, `SearchV2`, and by extension anything downstream of search:
`ItemDetails`, `DownloadableFilesDetail`) currently fail with:

```
UnsuccessfulResponseError: Unsuccessful response received from server
-STATUS 441 - BODY: '{"code":441,"reason":"UNAUTHORIZED","message":"miss token","metadata":{}}'
```

### What we confirmed

- **GET requests work.** The homepage probe (`MovieBoxHttpClient._init_client`)
  successfully harvests a runtime bearer token via the `x-user` response
  header, exactly as designed.
- **The token is being attached correctly.** `build_signed_headers()`
  attaches `Authorization: Bearer {token}` on every request regardless of
  path (`AUTH_FREE_PATHS` is empty, so the condition is never skipped).
  This isn't a client-side bug in header construction.
- **Both search implementations fail identically.** `Search` (`SEARCH_PATH`)
  and `SearchV2` (`SEARCH_PATH_V2`) both return the exact same 441 error —
  ruling out "one deprecated endpoint" as the explanation. It's not
  endpoint-specific.
- **The pattern is GET-succeeds / POST-fails**, not auth-fails-entirely.
  Every POST call we tested was rejected the same way; every GET call
  succeeded.

### What this likely means

The backend appears to have introduced a POST-specific auth requirement
that didn't exist when this code was written — either:

1. POST endpoints now expect the token somewhere other than the
   `Authorization: Bearer` header (a different header name, or embedded in
   the JSON body), or
2. A second-tier auth/handshake step now gates write-style (POST) access,
   separate from the homepage-token-harvest that only unlocks read (GET)
   access.

We can't distinguish between these from black-box testing (search
requests were the only POST endpoint tried). This needs real traffic
captured from the current Android app (e.g. via mitmproxy/HTTP Toolkit
against a rooted device or emulator, or a cert-pinning bypass) and a
byte-for-byte diff against what `v3/http_client.py` + `v3/crypto.py`
currently produce — not a quick patch.

### Current recommendation

**Use v1 or v2** — both fully verified end-to-end (search → item details →
resolve → download) as of this testing round. v3's code is kept in the
tree (the signing scheme, host-pool failover, and device-fingerprint
spoofing are still legitimate, reusable engineering) but is non-functional
until someone re-reverse-engineers the current POST auth requirement.

If you have insight into this or want to help capture real traffic, please
open an issue.