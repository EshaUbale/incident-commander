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


def build_triage_prompt(incident_description):
    return f"""You are a triage agent for an incident response system.
{incident_description}

Quickly check current metrics for the relevant service to gauge severity.
Do not investigate deeply or check logs or runbooks — that is a different agent's job.
Just get a quick read on severity.

Respond with ONLY a JSON object, no markdown formatting, no extra text,
in exactly this format:

{{
  "service": "the service name",
  "severity": "critical, high, medium, or low",
  "reasoning": "one sentence explaining why"
}}
"""


async def run_triage(client, session, incident_description):
    prompt = build_triage_prompt(incident_description)
    # return await run_agent(client, session, "gemini-3.6-flash", prompt)
    return await run_agent(client, session, "gemini-flash-lite-latest", prompt)  


# Lets you still test this agent alone: python3 agents/triage.py
async def main():
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await run_triage(client, session, "There's a reported issue with the checkout service.")
            print(result)


if __name__ == "__main__":
    asyncio.run(main())