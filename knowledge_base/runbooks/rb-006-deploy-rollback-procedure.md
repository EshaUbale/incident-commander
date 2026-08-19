# General deploy rollback procedure

**Service:** all
**Severity:** reference

## When to use this
Use this if a deploy causes a sustained spike in error rate or latency that doesn't recover within a few minutes on its own.

## Steps
1. Confirm the issue started right after a deploy by checking deploy history timestamps against the error spike.
2. Roll back to the previous known-good version.
3. Notify the team in the incident channel.
4. Open a ticket to investigate root cause before re-attempting the deploy.
