# Pre-Release Checklist (v0.0.1)

Things to resolve before actually publishing to PyPI — not blockers for
local development/testing.

- [ ] **`throttlebuster` dependency is currently a local path override**
      (`uv add --editable ~\Git_Projects\ThrottleBuster`). This only works
      on this machine — it will NOT work for anyone installing from PyPI.
      Before publishing, either:
      - revert to a normal version constraint (`throttlebuster>=0.1.13`)
        once the fork's fix is merged upstream and released, **or**
      - publish the fork under its own PyPI name and depend on that instead
- [ ] **`pyproject.toml` author email is still a placeholder**
      (`your-real-email@example.com`) — needs a real address before publish
- [ ] **Confirm PyPI name situation is resolved** (see the email drafted
      earlier to Simatwa re: inheriting the `moviebox-api` name, or decide
      on a fallback name like `moviebox-api-unofficial` if no response)
- [ ] Tag the release (`git tag v0.0.1`) and write GitHub release notes
      once the above are settled