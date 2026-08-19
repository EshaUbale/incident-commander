# Inventory database connection pool exhausted

**Service:** inventory
**Severity:** critical

## What happened
Inventory sync jobs started failing with "connection pool exhausted" errors during a high-traffic sale event.

## Root cause
A batch job was opening new DB connections without closing them properly, slowly leaking the pool.

## Fix
Restarted the inventory service to reset the pool. Fixed the batch job to use a context manager so connections always close.
