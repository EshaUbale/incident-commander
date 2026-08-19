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


def build_investigator_prompt(incident_description, triage_result):
    return f"""You are an investigator agent for an incident response system.
{incident_description}

Triage has already assessed this as:
{triage_result}

Investigate using the available tools: check logs, check metrics, and check if this
matches any past runbooks. Then summarize what's happening and how severe it is.

Do not create a ticket. That is the notifier agent's job, not yours.
Only investigate and summarize.
"""


async def run_investigator(client, session, incident_description, triage_result):
    prompt = build_investigator_prompt(incident_description, triage_result)
    #return await run_agent(client, session, "gemini-3.6-flash", prompt)
    return await run_agent(client, session, "gemini-flash-lite-latest", prompt)


async def main():
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            fake_triage = '{"service": "checkout", "severity": "critical", "reasoning": "test run"}'
            result = await run_investigator(client, session, "There's a reported issue with the checkout service.", fake_triage)
            print(result)


if __name__ == "__main__":
    asyncio.run(main())