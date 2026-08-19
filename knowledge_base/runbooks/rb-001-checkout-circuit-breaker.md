# Checkout circuit breaker opened

**Service:** checkout
**Severity:** critical

## What happened
The checkout service started throwing repeated timeouts when calling the payment gateway. After 3 failed retries, the circuit breaker opened automatically, blocking all further payment calls.

## Root cause
The payment gateway provider had an upstream outage. Our retry logic kept hammering a dead endpoint instead of backing off.

## Fix
Waited for the circuit breaker to reset automatically after 60 seconds once the provider recovered. No code change needed — this is expected behavior working correctly.