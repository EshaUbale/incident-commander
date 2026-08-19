# Checkout latency spike during deploy

**Service:** checkout
**Severity:** error

## What happened
Right after a deploy, checkout latency jumped from ~120ms to over 2000ms for about 5 minutes.

## Root cause
The new deploy included a database migration that briefly locked a heavily-used table.

## Fix
Latency recovered on its own once the migration finished. For future migrations on this table, we now run them during low-traffic windows.