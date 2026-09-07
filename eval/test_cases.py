# Each test case defines an incident scenario and what "correct" behavior looks like.
# expected_tools: which tools the Investigator should call for this incident to be
#   properly diagnosed (order doesn't matter, but all should appear).
# expected_severity: "critical" cases should stay critical; "non_critical" should
#   NOT be classified critical (checking Triage doesn't over- or under-react).
# expected_runbook: the runbook filename that should show up in search_runbooks results,
#   or None if no real match is expected.

TEST_CASES = [
    {
        "id": "checkout-circuit-breaker",
        "description": "There's a reported issue with the checkout service.",
        "expected_tools": {"get_logs", "get_metrics", "search_runbooks"},
        "expected_severity": "critical",
        "expected_runbook": "rb-001-checkout-circuit-breaker.md",
    },
    {
        "id": "checkout-rephrased",
        "description": "Customers are saying checkout is failing a lot right now.",
        "expected_tools": {"get_logs", "get_metrics", "search_runbooks"},
        "expected_severity": "critical",
        "expected_runbook": "rb-001-checkout-circuit-breaker.md",
    },
    {
        "id": "auth-jwt-expiry",
        "description": "Users are reporting they keep getting logged out unexpectedly.",
        "expected_tools": {"get_logs", "get_metrics", "search_runbooks"},
        "expected_severity": "non_critical",
        "expected_runbook": "rb-002-auth-jwt-expiry.md",
    },
    {
        "id": "auth-rate-limit",
        "description": "Some legitimate users are getting blocked when trying to log in.",
        "expected_tools": {"get_logs", "get_metrics", "search_runbooks"},
        "expected_severity": "non_critical",
        "expected_runbook": "rb-005-auth-rate-limit.md",
    },
    {
        "id": "inventory-db-pool",
        "description": "There's a reported issue with the inventory service.",
        "expected_tools": {"get_logs", "get_metrics", "search_runbooks"},
        "expected_severity": "critical",
        "expected_runbook": "rb-003-inventory-db-pool.md",
    },
    {
        "id": "inventory-rephrased",
        "description": "Stock levels aren't syncing correctly, inventory jobs seem to be failing.",
        "expected_tools": {"get_logs", "get_metrics", "search_runbooks"},
        "expected_severity": "critical",
        "expected_runbook": "rb-003-inventory-db-pool.md",
    },
    {
        "id": "deploy-latency-generic",
        "description": "Right after our last deploy, the notifications service got a lot slower for a few minutes.",
        "expected_tools": {"get_logs", "get_metrics", "search_runbooks"},
        "expected_severity": "non_critical",
        "expected_runbook": "rb-004-checkout-payment-timeout.md",
    },
    {
        "id": "unknown-service",
        "description": "There's a reported issue with the billing service.",
        "expected_tools": {"get_logs", "get_metrics", "search_runbooks"},
        "expected_severity": "non_critical",
        "expected_runbook": None,  # no real data exists for this service; system should
                                    # not hallucinate a confident match
    },
]