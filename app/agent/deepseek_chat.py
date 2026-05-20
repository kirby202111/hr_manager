"""DeepSeek-specific LangChain chat model compatibility helpers."""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI


class DeepSeekChatOpenAI(ChatOpenAI):
    """Preserve DeepSeek reasoning content across multi-step tool loops."""

    def _create_chat_result(
        self,
        response: dict[str, Any] | Any,
        generation_info: dict[str, Any] | None = None,
    ) -> Any:
        result = super()._create_chat_result(response, generation_info)
        response_dict = response if isinstance(response, dict) else response.model_dump()
        choices = response_dict.get("choices") or []

        for generation, choice in zip(result.generations, choices):
            if not isinstance(generation.message, AIMessage):
                continue
            message_payload = choice.get("message", {})
            if not isinstance(message_payload, dict):
                continue
            reasoning_content = message_payload.get("reasoning_content")
            if isinstance(reasoning_content, str) and reasoning_content:
                generation.message.additional_kwargs["reasoning_content"] = reasoning_content

        return result

    def _get_request_payload(
        self,
        input_: Any,
        *,
        stop: list[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        payload = super()._get_request_payload(input_, stop=stop, **kwargs)
        request_messages = payload.get("messages")
        if not isinstance(request_messages, list):
            return payload

        original_messages = self._convert_input(input_).to_messages()
        for original_message, payload_message in zip(original_messages, request_messages):
            if not isinstance(original_message, AIMessage) or not isinstance(payload_message, dict):
                continue
            reasoning_content = original_message.additional_kwargs.get("reasoning_content")
            if isinstance(reasoning_content, str) and reasoning_content:
                payload_message["reasoning_content"] = reasoning_content

        return payload


__all__ = ["DeepSeekChatOpenAI"]
