import asyncio
from google.genai import types
from google.genai import errors
from tracing import log_event


def mcp_tool_to_gemini_declaration(tool):
    return types.FunctionDeclaration(
        name=tool.name,
        description=tool.description or "",
        parameters_json_schema=tool.input_schema,
    )


async def call_gemini_with_retry(client, model, contents, config, run_id, agent_name, max_retries=5):
    """Calls Gemini, retrying with exponential backoff on rate limit (429) or
    server overload (503) errors, instead of letting the whole pipeline crash."""
    delay = 5  # seconds, doubles each retry
    for attempt in range(max_retries):
        try:
            return await client.aio.models.generate_content(
                model=model, contents=contents, config=config
            )
        except errors.ClientError as e:
            if e.code == 429 and attempt < max_retries - 1:
                log_event(run_id, agent_name, "retry", f"429 rate limit, attempt {attempt + 1}, waiting {delay}s")
                print(f"    (rate limited, retrying in {delay}s...)")
                await asyncio.sleep(delay)
                delay *= 2
            else:
                raise
        except errors.ServerError as e:
            if e.code == 503 and attempt < max_retries - 1:
                log_event(run_id, agent_name, "retry", f"503 overloaded, attempt {attempt + 1}, waiting {delay}s")
                print(f"    (model overloaded, retrying in {delay}s...)")
                await asyncio.sleep(delay)
                delay *= 2
            else:
                raise

    raise RuntimeError(f"Failed after {max_retries} retries")


async def run_agent(client, session, model, prompt, run_id, agent_name, max_turns=6, verbose=True):
    tools_result = await session.list_tools()
    declarations = [mcp_tool_to_gemini_declaration(t) for t in tools_result.tools]
    gemini_tool = types.Tool(function_declarations=declarations)

    contents = [types.Content(role="user", parts=[types.Part(text=prompt)])]

    for turn in range(max_turns):
        response = await call_gemini_with_retry(
            client, model, contents,
            types.GenerateContentConfig(tools=[gemini_tool]),
            run_id, agent_name,
        )

        candidate = response.candidates[0]
        contents.append(candidate.content)

        function_calls = [
            part.function_call for part in candidate.content.parts
            if part.function_call
        ]

        if not function_calls:
            log_event(run_id, agent_name, "final_answer", response.text[:500])
            return response.text

        function_response_parts = []
        for fc in function_calls:
            if verbose:
                print(f"  -> calling {fc.name}({dict(fc.args)})")
            log_event(run_id, agent_name, "tool_call", f"{fc.name}({dict(fc.args)})")

            result = await session.call_tool(fc.name, dict(fc.args))
            result_text = "".join(
                block.text for block in result.content if hasattr(block, "text")
            )
            log_event(run_id, agent_name, "tool_result", result_text[:500])

            function_response_parts.append(
                types.Part.from_function_response(
                    name=fc.name,
                    response={"result": result_text},
                )
            )

        contents.append(types.Content(role="user", parts=function_response_parts))

    log_event(run_id, agent_name, "error", "Max turns reached without a final answer.")
    return "Max turns reached without a final answer."