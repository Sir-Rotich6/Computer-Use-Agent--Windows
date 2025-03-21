"""
Agentic sampling loop that calls the Anthropic API and local implementation of anthropic-defined computer use tools.
"""

import platform
import os
import sys
import logging
from collections.abc import Callable
from datetime import datetime
from enum import StrEnum
from typing import Any, cast

import httpx
from anthropic import (
    Anthropic,
    AnthropicBedrock,
    AnthropicVertex,
    APIError,
    APIResponseValidationError,
    APIStatusError,
)
from anthropic.types.beta import (
    BetaCacheControlEphemeralParam,
    BetaContentBlockParam,
    BetaImageBlockParam,
    BetaMessage,
    BetaMessageParam,
    BetaTextBlock,
    BetaTextBlockParam,
    BetaToolResultBlockParam,
    BetaToolUseBlockParam,
)

from .tools import (
    TOOL_GROUPS_BY_VERSION,
    ToolCollection,
    ToolResult,
    ToolVersion,
)

PROMPT_CACHING_BETA_FLAG = "prompt-caching-2024-07-31"

# Configure logging
logging.basicConfig(
    filename="sampling_loop.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class APIProvider(StrEnum):
    ANTHROPIC = "anthropic"
    BEDROCK = "bedrock"
    VERTEX = "vertex"


# Detect Windows or Linux and modify SYSTEM_PROMPT accordingly
if platform.system() == "Windows":
    SYSTEM_PROMPT = f"""<SYSTEM_CAPABILITY>
* You are running Windows {platform.release()} ({platform.version()}).
* To install applications, use the Windows Package Manager (`winget install <package>`).
* To open applications like Notepad, use `start notepad`.
* PowerShell is available for scripting. Use `powershell.exe -Command "<command>"`.
* When using your computer function calls, they take a while to run and send back to you. Where possible, try to chain multiple of these calls into one function call request.
* The current date is {datetime.today().strftime('%A, %B %-d, %Y')}.
</SYSTEM_CAPABILITY>

<IMPORTANT>
* Use `curl` instead of `wget` for downloading files.
* If using command-line tools, ensure they are available in the system PATH.
</IMPORTANT>"""
else:
    SYSTEM_PROMPT = f"""<SYSTEM_CAPABILITY>
* You are utilising an Ubuntu virtual machine using {platform.machine()} architecture with internet access.
* Use curl instead of wget.
* To open Firefox, click on the Firefox icon. Note that firefox-esr is installed on your system.
* GUI applications can be launched using bash, but ensure `export DISPLAY=:1` is set.
* The current date is {datetime.today().strftime('%A, %B %-d, %Y')}.
</SYSTEM_CAPABILITY>

<IMPORTANT>
* Ignore startup wizards when using Firefox.
</IMPORTANT>"""


async def sampling_loop(
    *,
    model: str,
    provider: APIProvider,
    system_prompt_suffix: str,
    messages: list[BetaMessageParam],
    output_callback: Callable[[BetaContentBlockParam], None],
    tool_output_callback: Callable[[ToolResult, str], None],
    api_response_callback: Callable[
        [httpx.Request, httpx.Response | object | None, Exception | None], None
    ],
    api_key: str,
    only_n_most_recent_images: int | None = None,
    max_tokens: int = 4096,
    tool_version: ToolVersion,
    thinking_budget: int | None = None,
    token_efficient_tools_beta: bool = False,
):
    """
    Agentic sampling loop for the assistant/tool interaction of computer use.
    """
    tool_group = TOOL_GROUPS_BY_VERSION[tool_version]
    tool_collection = ToolCollection(*(ToolCls() for ToolCls in tool_group.tools))
    system = BetaTextBlockParam(
        type="text",
        text=f"{SYSTEM_PROMPT}{' ' + system_prompt_suffix if system_prompt_suffix else ''}",
    )

    logging.info("Starting sampling loop.")

    while True:
        try:
            enable_prompt_caching = False
            betas = [tool_group.beta_flag] if tool_group.beta_flag else []
            if token_efficient_tools_beta:
                betas.append("token-efficient-tools-2025-02-19")
            image_truncation_threshold = only_n_most_recent_images or 0

            # Select API client
            if provider == APIProvider.ANTHROPIC:
                client = Anthropic(api_key=api_key, max_retries=4)
                enable_prompt_caching = True
            elif provider == APIProvider.VERTEX:
                client = AnthropicVertex()
            elif provider == APIProvider.BEDROCK:
                client = AnthropicBedrock()

            if enable_prompt_caching:
                betas.append(PROMPT_CACHING_BETA_FLAG)
                _inject_prompt_caching(messages)
                only_n_most_recent_images = 0
                system["cache_control"] = {"type": "ephemeral"}  # type: ignore

            if only_n_most_recent_images:
                _maybe_filter_to_n_most_recent_images(
                    messages,
                    only_n_most_recent_images,
                    min_removal_threshold=image_truncation_threshold,
                )

            extra_body = {}
            if thinking_budget:
                extra_body = {"thinking": {"type": "enabled", "budget_tokens": thinking_budget}}

            # API call
            raw_response = client.beta.messages.with_raw_response.create(
                max_tokens=max_tokens,
                messages=messages,
                model=model,
                system=[system],
                tools=tool_collection.to_params(),
                betas=betas,
                extra_body=extra_body,
            )

            api_response_callback(raw_response.http_response.request, raw_response.http_response, None)
            response = raw_response.parse()
            response_params = _response_to_params(response)
            messages.append({"role": "assistant", "content": response_params})

            tool_result_content: list[BetaToolResultBlockParam] = []
            for content_block in response_params:
                output_callback(content_block)
                if content_block["type"] == "tool_use":
                    result = await tool_collection.run(
                        name=content_block["name"],
                        tool_input=cast(dict[str, Any], content_block["input"]),
                    )
                    tool_result_content.append(_make_api_tool_result(result, content_block["id"]))
                    tool_output_callback(result, content_block["id"])

            if not tool_result_content:
                return messages

            messages.append({"content": tool_result_content, "role": "user"})

        except APIError as e:
            logging.error(f"API error: {e}")
            api_response_callback(e.request, e.body, e)
            return messages
        except Exception as e:
            logging.error(f"Unexpected error: {e}", exc_info=True)
            return messages


# New Feature: Logging added for debugging API errors
# New Feature: Platform detection for Windows/Linux
# New Feature: More user-friendly system prompt for Windows
