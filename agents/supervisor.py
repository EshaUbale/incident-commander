import asyncio
import os
import uuid
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai

from triage import run_triage
from investigator import run_investigator
from notifier import run_notifier

load_dotenv()

server_params = StdioServerParameters(
    command="python3",
    args=["mcp_server/server.py"],
)

INCIDENT_DESCRIPTION = "There's a reported issue with the checkout service."


async def run_pipeline(client, session, incident_description, run_id, verbose=True):
    """Runs Triage -> Investigator -> Notifier for one incident. Reusable by both
    the standalone script and the eval harness."""
    if verbose:
        print(f"=== Run ID: {run_id} ===\n")
        print("=== Step 1: Triage ===")

    triage_result = await run_triage(client, session, incident_description, run_id)
    if verbose:
        print(triage_result)
        print("\n=== Step 2: Investigation ===")

    investigation_summary = await run_investigator(
        client, session, incident_description, triage_result, run_id
    )
    if verbose:
        print(investigation_summary)
        print("\n=== Step 3: Notification ===")

    notification = await run_notifier(client, session, triage_result, investigation_summary, run_id)
    if verbose:
        print(notification)
        print(f"\n=== Done (run_id: {run_id}) ===")

    return triage_result, investigation_summary, notification


async def main():
    run_id = str(uuid.uuid4())[:8]
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            await run_pipeline(client, session, INCIDENT_DESCRIPTION, run_id)


if __name__ == "__main__":
    asyncio.run(main())