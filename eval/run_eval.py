import asyncio
import os
import sys
import sqlite3
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agents"))

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai

from supervisor import run_pipeline, server_params
from test_cases import TEST_CASES

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "mcp_server", "db", "incidents.db")


def get_tool_calls_for_run(run_id):
    """Reads back which tools were actually called during a run, from the traces table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT details FROM traces WHERE run_id = ? AND event_type = 'tool_call'",
        (run_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    # details look like "get_logs({'service': 'checkout'})" — grab the tool name before "("
    return {r[0].split("(")[0] for r in rows}


def score_case(case, triage_result, tool_calls_made):
    """Returns (passed: bool, notes: list[str]) for one test case."""
    notes = []
    passed = True

    missing_tools = case["expected_tools"] - tool_calls_made
    if missing_tools:
        passed = False
        notes.append(f"Missing expected tool calls: {missing_tools}")

    triage_lower = triage_result.lower()
    is_critical = '"severity": "critical"' in triage_lower or "'severity': 'critical'" in triage_lower

    if case["expected_severity"] == "critical" and not is_critical:
        passed = False
        notes.append("Expected critical severity, Triage did not mark it critical")
    if case["expected_severity"] == "non_critical" and is_critical:
        passed = False
        notes.append("Expected non-critical severity, Triage marked it critical")

    return passed, notes


async def run_all():
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    results = []

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            for case in TEST_CASES:
                run_id = str(uuid.uuid4())[:8]
                print(f"\nRunning: {case['id']} (run_id: {run_id})")

                triage_result, investigation_summary, notification = await run_pipeline(
                    client, session, case["description"], run_id, verbose=False
                )

                tool_calls_made = get_tool_calls_for_run(run_id)
                passed, notes = score_case(case, triage_result, tool_calls_made)

                results.append({"id": case["id"], "passed": passed, "notes": notes})
                status = "PASS" if passed else "FAIL"
                print(f"  {status}")
                for n in notes:
                    print(f"    - {n}")

    print("\n" + "=" * 40)
    passed_count = sum(1 for r in results if r["passed"])
    print(f"RESULTS: {passed_count}/{len(results)} test cases passed")
    print("=" * 40)
    for r in results:
        mark = "✓" if r["passed"] else "✗"
        print(f"  {mark} {r['id']}")


if __name__ == "__main__":
    asyncio.run(run_all())