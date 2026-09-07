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

Use these thresholds based on the metrics you retrieve, not on how the incident
was described to you. Base your severity purely on the numbers:
- critical: error rate above 15%, OR latency above 1500ms, OR CPU above 90%
- high: error rate 5-15%, OR latency 500-1500ms, OR CPU 75-90%
- medium: error rate 1-5%, OR latency 200-500ms, OR CPU 50-75%
- low: below all of the above

Two incidents with the same underlying metrics should always get the same
severity, regardless of how the incident was worded.

Respond with ONLY a JSON object, no markdown formatting, no extra text,
in exactly this format:

{{
  "service": "the service name",
  "severity": "critical, high, medium, or low",
  "reasoning": "one sentence explaining why, citing the specific metric that drove the decision"
}}
"""


async def run_triage(client, session, incident_description, run_id):
    prompt = build_triage_prompt(incident_description)
    return await run_agent(client, session, "gemini-flash-lite-latest", prompt, run_id, "triage")


async def main():
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await run_triage(client, session, "There's a reported issue with the checkout service.", "test-run")
            print(result)


if __name__ == "__main__":
    asyncio.run(main())