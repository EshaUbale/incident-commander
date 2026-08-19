# Spike in JWT validation failures

**Service:** auth
**Severity:** warning

## What happened
Users reported being logged out unexpectedly. Logs showed a spike in "expired token" errors.

## Root cause
A clock drift issue on one auth server caused it to reject tokens slightly early.

## Fix
Restarted NTP sync on the affected server. Added a monitoring alert for clock drift going forward.