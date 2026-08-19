from google.genai import types


def mcp_tool_to_gemini_declaration(tool):
    """Converts one MCP tool's schema into the format Gemini expects."""
    return types.FunctionDeclaration(
        name=tool.name,
        description=tool.description or "",
        parameters_json_schema=tool.input_schema,
    )


async def run_agent(client, session, model, prompt, max_turns=6, verbose=True):
    """
    Sends a prompt to Gemini, executes any tool calls it requests against
    the given MCP session, and keeps looping until Gemini gives a final
    text answer. Returns that final text.
    """
    tools_result = await session.list_tools()
    declarations = [mcp_tool_to_gemini_declaration(t) for t in tools_result.tools]
    gemini_tool = types.Tool(function_declarations=declarations)

    contents = [types.Content(role="user", parts=[types.Part(text=prompt)])]

    for turn in range(max_turns):
        response = await client.aio.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(tools=[gemini_tool]),
        )

        candidate = response.candidates[0]
        contents.append(candidate.content)

        function_calls = [
            part.function_call for part in candidate.content.parts
            if part.function_call
        ]

        if not function_calls:
            return response.text

        function_response_parts = []
        for fc in function_calls:
            if verbose:
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

    return "Max turns reached without a final answer."