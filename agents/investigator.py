import asyncio
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai
from google.genai import types

load_dotenv()

server_params = StdioServerParameters(
    command="python3",
    args=["mcp_server/server.py"],
)


def mcp_tool_to_gemini_declaration(tool):
    """Converts one MCP tool's schema into the format Gemini expects."""
    return types.FunctionDeclaration(
        name=tool.name,
        description=tool.description or "",
        parameters_json_schema=tool.input_schema,
    )


async def main():
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Ask the MCP server what tools it has, translate them for Gemini.
            tools_result = await session.list_tools()
            declarations = [mcp_tool_to_gemini_declaration(t) for t in tools_result.tools]
            gemini_tool = types.Tool(function_declarations=declarations)

            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part(text=(
                        "There's a reported issue with the checkout service. "
                        "Investigate using the available tools: check logs, check metrics, "
                        "and check if this matches any past runbooks. "
                        "Then summarize what's happening and how severe it is."
                    ))],
                )
            ]

            max_turns = 6
            for turn in range(max_turns):
                response = await client.aio.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(tools=[gemini_tool]),
                )

                candidate = response.candidates[0]
                contents.append(candidate.content)

                function_calls = [
                    part.function_call for part in candidate.content.parts
                    if part.function_call
                ]

                # No more tool calls means Gemini is ready to give a final answer.
                if not function_calls:
                    print(response.text)
                    return

                # Otherwise, actually run each requested tool call and feed the result back.
                function_response_parts = []
                for fc in function_calls:
                    print(f"  -> calling {fc.name}({dict(fc.args)})")
                    result = await session.call_tool(fc.name, dict(fc.args))
                    result_text = "".join(
                        block.text for block in result.content if hasattr(block, "text")
                    )
                    function_response_parts.append(
                        types.Part.from_function_response(
                            name=fc.name,
                            response={"result": result_text},
                        )
                    )

                contents.append(types.Content(role="user", parts=function_response_parts))

            print("Max turns reached without a final answer.")


if __name__ == "__main__":
    asyncio.run(main())