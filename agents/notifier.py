import asyncio
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai

from tool_loop import run_agent

load_dotenv()

server_params = StdioServerParameters(
    command="python3",
    args=["mcp_server/server.py"],
)


def build_notifier_prompt(triage_result, investigation_summary):
    return f"""You are a notifier agent for an incident response system.

Here is the triage result:
{triage_result}

Here is the investigation summary:
{investigation_summary}

Do two things, in order:
1. Create a ticket using the create_ticket tool, with a clear title and a
   description that summarizes the root cause. Use the severity from the
   triage result.
2. After the ticket is created, write a short, human-readable notification
   message (2-3 sentences) as if posting it to a team Slack channel,
   including the ticket number.
"""


async def run_notifier(client, session, triage_result, investigation_summary):
    prompt = build_notifier_prompt(triage_result, investigation_summary)
    # return await run_agent(client, session, "gemini-3.6-flash", prompt)
    return await run_agent(client, session, "gemini-flash-lite-latest", prompt)


async def main():
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            fake_triage = '{"service": "checkout", "severity": "critical", "reasoning": "test run"}'
            fake_summary = "Test investigation summary for standalone run."
            result = await run_notifier(client, session, fake_triage, fake_summary)
            print(result)


if __name__ == "__main__":
    asyncio.run(main())