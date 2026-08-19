import asyncio
import os
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


async def main():
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("=== Step 1: Triage ===")
            triage_result = await run_triage(client, session, INCIDENT_DESCRIPTION)
            print(triage_result)

            print("\n=== Step 2: Investigation ===")
            investigation_summary = await run_investigator(
                client, session, INCIDENT_DESCRIPTION, triage_result
            )
            print(investigation_summary)

            print("\n=== Step 3: Notification ===")
            notification = await run_notifier(client, session, triage_result, investigation_summary)
            print(notification)

            print("\n=== Done ===")


if __name__ == "__main__":
    asyncio.run(main())