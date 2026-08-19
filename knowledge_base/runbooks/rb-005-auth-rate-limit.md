# Login endpoint rate limit exceeded

**Service:** auth
**Severity:** warning

## What happened
A burst of login attempts from a single IP range triggered rate limiting, blocking some legitimate users too.

## Root cause
A partner integration was retrying failed login calls too aggressively without backoff.

## Fix
Contacted the partner to add exponential backoff on their end. Temporarily raised the rate limit threshold as a stopgap.
