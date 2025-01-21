from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional
import asyncio

from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from guakegpt.config.settings import Settings

class Role(Enum):
    SYSTEM = auto()
    USER = auto()
    ASSISTANT = auto()

@dataclass
class Message:
    role: Role
    content: str

class LLMClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.openai_client: Optional[AsyncOpenAI] = None
        self.anthropic_client: Optional[AsyncAnthropic] = None
        self._setup_client()

    def _setup_client(self):
        if self.settings.llm.provider == "openai":
            self.openai_client = AsyncOpenAI(api_key=self.settings.api_key)
        else:
            self.anthropic_client = AsyncAnthropic(api_key=self.settings.api_key)

    async def send_message(self, messages: List[Message]) -> str:
        if self.settings.llm.provider == "openai":
            return await self._send_openai_message(messages)
        else:
            return await self._send_anthropic_message(messages)

    async def _send_openai_message(self, messages: List[Message]) -> str:
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized")

        formatted_messages = [
            {
                "role": {
                    Role.SYSTEM: "system",
                    Role.USER: "user",
                    Role.ASSISTANT: "assistant"
                }[msg.role],
                "content": msg.content
            }
            for msg in messages
        ]

        response = await self.openai_client.chat.completions.create(
            model=self.settings.llm.model,
            messages=formatted_messages,
            temperature=self.settings.llm.temperature,
            max_tokens=self.settings.llm.max_tokens
        )

        return response.choices[0].message.content

    async def _send_anthropic_message(self, messages: List[Message]) -> str:
        if not self.anthropic_client:
            raise RuntimeError("Anthropic client not initialized")

        system_message = next((msg for msg in messages if msg.role == Role.SYSTEM), None)
        conversation = []

        for msg in messages:
            if msg.role == Role.SYSTEM:
                continue
            conversation.append({
                "role": "user" if msg.role == Role.USER else "assistant",
                "content": msg.content
            })

        response = await self.anthropic_client.messages.create(
            model=self.settings.llm.model,
            messages=conversation,
            system=system_message.content if system_message else None,
            temperature=self.settings.llm.temperature,
            max_tokens=self.settings.llm.max_tokens
        )

        return response.content[0].text 