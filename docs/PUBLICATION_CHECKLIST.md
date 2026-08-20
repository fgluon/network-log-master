# Public Publication Checklist

Use this checklist before every public commit that adds or changes operational material, fixtures, configuration examples, scripts, or imported code.

## Content safety

- [ ] no passwords, tokens, API keys, credentials, or private key material
- [ ] no production IP addresses or firewall allowlists
- [ ] no private DNS names or environment-specific access endpoints
- [ ] no customer-identifying hostnames, payloads, or raw logs
- [ ] no restricted historical branding or organization identifiers
- [ ] no local secret files, credential caches, or generated state

## Fixture safety

- [ ] synthetic device names only
- [ ] IPv4 examples use `192.0.2.0/24`, `198.51.100.0/24`, or `203.0.113.0/24`
- [ ] IPv6 examples use `2001:db8::/32`
- [ ] examples preserve event structure without preserving production identity

## Engineering gates

- [ ] stage only intended files
- [ ] run secret/sanitation scanning against staged and tracked content
- [ ] run restricted-term/environment-identifier scanning
- [ ] run syntax/lint checks applicable to changed files
- [ ] run the complete relevant test suite
- [ ] run whitespace/diff validation
- [ ] inspect the staged diff manually
- [ ] confirm documentation matches the verified implementation state

## Migration gates

When importing code from another repository or live checkout:

- [ ] record source repository/commit provenance
- [ ] compare the live checkout to its remote first
- [ ] preserve working tests and test fixtures
- [ ] sanitize history/content before public consolidation
- [ ] avoid creating a second writable copy that can silently drift
- [ ] update `CURRENT_STATE.md` and `PROJECT_JOURNAL.md`

## Rule

Do not remove, weaken, or bypass a safety check merely to make publication pass. Fix the content or explicitly document why a check is being changed before publication.
